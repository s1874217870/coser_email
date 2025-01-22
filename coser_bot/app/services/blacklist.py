"""
黑名单服务模块
处理用户黑名单功能
"""
from app.core.redis import redis_client
from typing import Optional

class BlacklistService:
    """黑名单服务类"""
    
    BLACKLIST_KEY = "blacklist:email"
    
    @staticmethod
    async def add_to_blacklist(email: str, reason: Optional[str] = None) -> bool:
        """
        将邮箱添加到黑名单
        
        参数:
            email: 邮箱地址
            reason: 添加原因
        """
        try:
            redis_client.hset(BlacklistService.BLACKLIST_KEY, email, reason or "未指定原因")
            return True
        except Exception as e:
            print(f"添加黑名单失败: {e}")
            return False
            
    @staticmethod
    async def remove_from_blacklist(email: str) -> bool:
        """
        从黑名单中移除邮箱
        
        参数:
            email: 邮箱地址
        """
        try:
            redis_client.hdel(BlacklistService.BLACKLIST_KEY, email)
            return True
        except Exception as e:
            print(f"移除黑名单失败: {e}")
            return False
            
    @staticmethod
    async def is_email_blacklisted(email: str) -> bool:
        """
        检查邮箱是否在黑名单中
        
        参数:
            email: 邮箱地址
        """
        return bool(redis_client.hexists(BlacklistService.BLACKLIST_KEY, email))
        
    @staticmethod
    async def get_blacklist_reason(email: str) -> Optional[str]:
        """
        获取邮箱被加入黑名单的原因
        
        参数:
            email: 邮箱地址
        """
        reason = redis_client.hget(BlacklistService.BLACKLIST_KEY, email)
        return reason.decode() if reason else None
