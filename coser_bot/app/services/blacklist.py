"""
黑名单服务模块
处理邮箱黑名单和IP限制
"""
from app.core.redis import redis_client
from app.core.mongodb import get_mongodb
from datetime import datetime

class BlacklistService:
    """黑名单服务类"""
    
    @staticmethod
    async def is_email_blacklisted(email: str) -> bool:
        """
        检查邮箱是否在黑名单中
        
        参数:
            email: 待检查的邮箱地址
        """
        db = await get_mongodb()
        result = await db.email_blacklist.find_one({"email": email})
        return result is not None
        
    @staticmethod
    async def add_to_blacklist(email: str, reason: str):
        """
        将邮箱添加到黑名单
        
        参数:
            email: 要加入黑名单的邮箱
            reason: 加入黑名单的原因
        """
        db = await get_mongodb()
        await db.email_blacklist.insert_one({
            "email": email,
            "reason": reason,
            "created_at": datetime.utcnow()
        })
        
    @staticmethod
    async def remove_from_blacklist(email: str):
        """
        从黑名单中移除邮箱
        
        参数:
            email: 要移除的邮箱
        """
        db = await get_mongodb()
        await db.email_blacklist.delete_one({"email": email})
