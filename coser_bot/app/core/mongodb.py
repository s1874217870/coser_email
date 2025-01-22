"""
MongoDB连接模块
用于文档数据库操作
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

settings = get_settings()

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]

async def get_mongodb():
    """获取MongoDB数据库实例"""
    return db
