"""
Redis客户端模块
处理Redis连接和操作
"""
import redis
from app.core.config import get_settings
from typing import Any, Optional, Union
import json
from datetime import datetime, timedelta

settings = get_settings()

# 创建Redis连接池
pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
    max_connections=100,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)

redis_client = redis.Redis(connection_pool=pool)

class CacheManager:
    """缓存管理类"""
    
    # 默认过期时间（秒）
    DEFAULT_EXPIRE = 3600
    
    # 缓存键前缀
    PREFIX_USER_LANG = "user_lang"
    PREFIX_VERIFY_CODE = "verify_code"
    PREFIX_VERIFY_STATUS = "verify_status"
    PREFIX_CHECKIN = "checkin"
    PREFIX_CHECKIN_STREAK = "checkin_streak"
    
    @staticmethod
    def generate_key(prefix: str, *args) -> str:
        """生成缓存键"""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    @staticmethod
    def set_cache(
        key: str,
        value: Any,
        expire: int = DEFAULT_EXPIRE,
        nx: bool = False
    ) -> bool:
        """
        设置缓存
        
        参数:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            nx: 是否只在键不存在时设置
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return bool(redis_client.set(
                key,
                value,
                ex=expire,
                nx=nx
            ))
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    @staticmethod
    def get_cache(
        key: str,
        default: Any = None,
        json_decode: bool = False
    ) -> Any:
        """
        获取缓存
        
        参数:
            key: 缓存键
            default: 默认值
            json_decode: 是否需要JSON解码
        """
        try:
            value = redis_client.get(key)
            if value is None:
                return default
            if json_decode:
                return json.loads(value)
            return value
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return default
    
    @staticmethod
    def delete_cache(*keys: str) -> bool:
        """删除缓存"""
        try:
            return bool(redis_client.delete(*keys))
        except Exception as e:
            print(f"删除缓存失败: {e}")
            return False
    
    @staticmethod
    def clear_prefix(prefix: str) -> bool:
        """清除指定前缀的所有缓存"""
        try:
            pattern = f"{prefix}:*"
            keys = redis_client.keys(pattern)
            if keys:
                return bool(redis_client.delete(*keys))
            return True
        except Exception as e:
            print(f"清除缓存失败: {e}")
            return False
            
    @staticmethod
    def incr_with_expire(key: str, expire: int) -> Optional[int]:
        """
        递增并设置过期时间
        
        参数:
            key: 缓存键
            expire: 过期时间（秒）
        """
        try:
            with redis_client.pipeline() as pipe:
                current = pipe.incr(key).expire(key, expire).execute()
                return current[0]
        except Exception as e:
            print(f"递增操作失败: {e}")
            return None

class RateLimit:
    """速率限制类"""
    
    @staticmethod
    def check_rate_limit(key: str, limit: int, period: int) -> bool:
        """
        检查是否超出速率限制
        
        参数:
            key: Redis键
            limit: 限制次数
            period: 时间周期(秒)
        """
        try:
            current = CacheManager.incr_with_expire(key, period)
            return current is not None and current <= limit
        except Exception as e:
            print(f"速率限制检查失败: {e}")
            return False
