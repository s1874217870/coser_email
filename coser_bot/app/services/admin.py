"""
管理员服务模块
处理管理后台相关的业务逻辑
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, select, distinct
from app.models.user import User, PointRecord
from app.models.admin import AdminLog, SecurityLog
from app.core.mongodb import get_mongodb
from app.core.redis import redis_client
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

class AdminService:
    """管理员服务类"""
    
    @staticmethod
    async def get_system_statistics(db: AsyncSession) -> Dict[str, Any]:
        """
        获取系统统计数据
        
        参数:
            db: 数据库会话
        """
        try:
            # 获取用户统计
            total_users = await db.scalar(
                select(func.count()).select_from(User)
            )
            
            # 获取今日活跃用户
            today = datetime.now().date()
            active_users = await db.scalar(
                select(func.count(distinct(User.id)))
                .select_from(User)
                .join(PointRecord)
                .where(
                    and_(
                        PointRecord.created_at >= today,
                        PointRecord.created_at < today + timedelta(days=1)
                    )
                )
            )
            
            # 获取积分统计
            total_points = await db.scalar(
                select(func.sum(User.points)).select_from(User)
            )
            
            # 获取今日签到数
            daily_checkins = await db.scalar(
                select(func.count())
                .select_from(PointRecord)
                .where(
                    and_(
                        PointRecord.type == 1,  # 签到类型
                        PointRecord.created_at >= today,
                        PointRecord.created_at < today + timedelta(days=1)
                    )
                )
            )
            
            return {
                "total_users": total_users or 0,
                "active_users": active_users or 0,
                "total_points": total_points or 0,
                "daily_checkins": daily_checkins or 0
            }
            
        except Exception as e:
            print(f"获取系统统计数据失败: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "total_points": 0,
                "daily_checkins": 0
            }
            
    @staticmethod
    async def get_security_logs(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取安全日志
        
        参数:
            start_date: 开始日期
            end_date: 结束日期
            level: 日志级别
            limit: 返回数量限制
        """
        try:
            db = await get_mongodb()
            collection = db.security_logs
            
            # 构建查询条件
            query = {}
            if start_date:
                query["timestamp"] = {"$gte": start_date}
            if end_date:
                query.setdefault("timestamp", {})["$lte"] = end_date
            if level:
                query["level"] = level
                
            # 执行查询
            cursor = collection.find(query)
            cursor.sort("timestamp", -1)
            cursor.limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            print(f"获取安全日志失败: {e}")
            return []
            
    @staticmethod
    async def update_translation(lang: str, key: str, value: str) -> bool:
        """
        更新翻译内容
        
        参数:
            lang: 语言代码
            key: 翻译键值
            value: 翻译内容
        """
        try:
            db = await get_mongodb()
            collection = db.translations
            
            # 更新或插入翻译
            result = await collection.update_one(
                {"lang": lang, "key": key},
                {"$set": {"value": value}},
                upsert=True
            )
            
            return bool(result.modified_count or result.upserted_id)
            
        except Exception as e:
            print(f"更新翻译失败: {e}")
            return False
