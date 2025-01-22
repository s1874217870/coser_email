"""
MongoDB连接模块
处理MongoDB连接和操作
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

settings = get_settings()

# MongoDB客户端
client = AsyncIOMotorClient(settings.MONGODB_URI)

async def get_mongodb():
    """获取MongoDB数据库实例"""
    return client[settings.MONGODB_DB]
