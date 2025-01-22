"""
Redis连接模块
用于管理Redis连接和提供缓存服务
"""
from redis import Redis
from app.core.config import get_settings

settings = get_settings()

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

class RateLimit:
    """IP限流实现"""
    @staticmethod
    async def check_rate_limit(ip: str, limit: int = 10, period: int = 3600) -> bool:
        """
        检查IP是否超出限流
        
        参数:
            ip: IP地址
            limit: 限制次数
            period: 时间周期(秒)
        """
        key = f"rate_limit:{ip}"
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, period)
        return current <= limit
