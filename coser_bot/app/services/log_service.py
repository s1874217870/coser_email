"""
日志服务模块
处理系统安全日志的存储和查询
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core.mongodb import get_mongodb
from motor.motor_asyncio import AsyncIOMotorDatabase

class LogService:
    """日志服务类"""
    
    @staticmethod
    async def add_log(
        level: str,
        event_type: str,
        description: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加安全日志
        
        参数:
            level: 日志级别（info/warning/error）
            event_type: 事件类型
            description: 事件描述
            user_id: 相关用户ID
            ip_address: IP地址
            metadata: 额外元数据
        """
        try:
            db: AsyncIOMotorDatabase = await get_mongodb()
            collection = db.security_logs
            
            log_entry = {
                "level": level,
                "event_type": event_type,
                "description": description,
                "user_id": user_id,
                "ip_address": ip_address,
                "metadata": metadata or {},
                "created_at": datetime.utcnow()
            }
            
            await collection.insert_one(log_entry)
            return True
        except Exception as e:
            print(f"添加日志失败: {e}")
            return False
            
    @staticmethod
    async def get_logs(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        level: Optional[str] = None,
        event_type: Optional[str] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取安全日志
        
        参数:
            start_date: 开始日期
            end_date: 结束日期
            level: 日志级别
            event_type: 事件类型
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数
        """
        try:
            db: AsyncIOMotorDatabase = await get_mongodb()
            collection = db.security_logs
            
            # 构建查询条件
            query = {}
            if start_date:
                query["created_at"] = {"$gte": start_date}
            if end_date:
                query.setdefault("created_at", {})["$lte"] = end_date
            if level:
                query["level"] = level
            if event_type:
                query["event_type"] = event_type
            if user_id:
                query["user_id"] = user_id
                
            # 执行查询
            cursor = collection.find(query)
            cursor.sort("created_at", -1)
            cursor.skip(skip).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            print(f"获取日志失败: {e}")
            return []
            
    @staticmethod
    async def get_log_statistics() -> Dict[str, int]:
        """获取日志统计信息"""
        try:
            db: AsyncIOMotorDatabase = await get_mongodb()
            collection = db.security_logs
            
            # 统计各级别日志数量
            pipeline = [
                {
                    "$group": {
                        "_id": "$level",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=None)
            return {doc["_id"]: doc["count"] for doc in result}
            
        except Exception as e:
            print(f"获取日志统计失败: {e}")
            return {}
