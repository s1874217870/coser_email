"""
积分服务模块
处理用户积分相关的业务逻辑
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.user import User, PointRecord
from app.core.redis import redis_client
from app.core.config import get_settings
from typing import Optional, List, Tuple

settings = get_settings()

class PointsService:
    """积分服务类"""
    
    DAILY_CHECKIN_POINTS = 10  # 每日签到积分
    WEEKLY_BONUS_POINTS = 20   # 连续7天奖励
    MONTHLY_BONUS_POINTS = 100 # 连续30天奖励
    
    @staticmethod
    async def daily_checkin(db: Session, user_id: int) -> Tuple[bool, int, str]:
        """
        用户每日签到
        
        参数:
            db: 数据库会话
            user_id: 用户ID
            
        返回:
            Tuple[bool, int, str]: (是否成功, 获得积分数, 消息)
        """
        # 检查今日是否已签到
        today = datetime.now().date()
        key = f"checkin:{user_id}:{today}"
        if redis_client.exists(key):
            return False, 0, "今日已签到"
            
        try:
            # 获取用户连续签到天数
            streak_key = f"checkin_streak:{user_id}"
            current_streak = int(redis_client.get(streak_key) or 0)
            
            # 检查是否中断连续签到
            yesterday = today - timedelta(days=1)
            if not redis_client.exists(f"checkin:{user_id}:{yesterday}"):
                current_streak = 0
                
            # 更新连续签到天数
            current_streak += 1
            redis_client.setex(streak_key, 86400 * 31, current_streak)  # 31天过期
            
            # 计算奖励积分
            points = PointsService.DAILY_CHECKIN_POINTS
            bonus_msg = ""
            
            if current_streak == 7:
                points += PointsService.WEEKLY_BONUS_POINTS
                bonus_msg = f"，获得连续7天奖励{PointsService.WEEKLY_BONUS_POINTS}积分"
            elif current_streak == 30:
                points += PointsService.MONTHLY_BONUS_POINTS
                bonus_msg = f"，获得连续30天奖励{PointsService.MONTHLY_BONUS_POINTS}积分"
                
            # 记录签到
            redis_client.setex(key, 86400, 1)  # 24小时过期
            
            # 添加积分记录
            point_record = PointRecord(
                user_id=user_id,
                points=points,
                type=1,  # 1:签到
                description=f"每日签到{bonus_msg}"
            )
            db.add(point_record)
            
            # 更新用户总积分
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.points += points
                
            db.commit()
            
            return True, points, f"签到成功，获得{points}积分{bonus_msg}"
            
        except Exception as e:
            db.rollback()
            print(f"签到失败: {e}")
            return False, 0, "签到失败，请稍后重试"
            
    @staticmethod
    async def add_activity_points(
        db: Session,
        user_id: int,
        points: int,
        description: str
    ) -> Tuple[bool, str]:
        """
        添加活动积分
        
        参数:
            db: 数据库会话
            user_id: 用户ID
            points: 积分数量（20-100）
            description: 积分说明
        """
        if not 20 <= points <= 100:
            return False, "活动积分必须在20-100之间"
            
        try:
            # 添加积分记录
            point_record = PointRecord(
                user_id=user_id,
                points=points,
                type=2,  # 2:活动
                description=description
            )
            db.add(point_record)
            
            # 更新用户总积分
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.points += points
                
            db.commit()
            return True, f"获得{points}活动积分"
            
        except Exception as e:
            db.rollback()
            print(f"添加活动积分失败: {e}")
            return False, "添加积分失败，请稍后重试"
            
    @staticmethod
    async def add_content_points(
        db: Session,
        user_id: int,
        points: int,
        description: str
    ) -> Tuple[bool, str]:
        """
        添加内容发布积分
        
        参数:
            db: 数据库会话
            user_id: 用户ID
            points: 积分数量（5-50）
            description: 积分说明
        """
        if not 5 <= points <= 50:
            return False, "内容积分必须在5-50之间"
            
        try:
            # 添加积分记录
            point_record = PointRecord(
                user_id=user_id,
                points=points,
                type=3,  # 3:内容
                description=description
            )
            db.add(point_record)
            
            # 更新用户总积分
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.points += points
                
            db.commit()
            return True, f"获得{points}内容积分"
            
        except Exception as e:
            db.rollback()
            print(f"添加内容积分失败: {e}")
            return False, "添加积分失败，请稍后重试"
            
    @staticmethod
    async def get_user_points(db: Session, user_id: int) -> Optional[int]:
        """
        获取用户总积分
        
        参数:
            db: 数据库会话
            user_id: 用户ID
        """
        user = db.query(User).filter(User.id == user_id).first()
        return user.points if user else None
        
    @staticmethod
    async def get_point_records(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[PointRecord]:
        """
        获取用户积分记录
        
        参数:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回记录数量
        """
        return (
            db.query(PointRecord)
            .filter(PointRecord.user_id == user_id)
            .order_by(PointRecord.created_at.desc())
            .limit(limit)
            .all()
        )
