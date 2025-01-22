"""
Redis客户端模块
处理Redis连接和操作
"""
import redis
from app.core.config import get_settings

settings = get_settings()

# 创建Redis连接池
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

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
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, period)
        return current <= limit
