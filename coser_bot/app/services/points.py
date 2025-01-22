"""
积分服务模块
处理用户积分相关的业务逻辑
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.user import User, PointRecord
from app.core.redis import redis_client, CacheManager
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
        """用户每日签到"""
        # 检查今日是否已签到
        today = datetime.now().date()
        checkin_key = CacheManager.generate_key(CacheManager.PREFIX_CHECKIN, user_id, today)
        if CacheManager.get_cache(checkin_key):
            return False, 0, "今日已签到"
            
        try:
            # 获取用户连续签到天数
            streak_key = CacheManager.generate_key(CacheManager.PREFIX_CHECKIN_STREAK, user_id)
            current_streak = int(CacheManager.get_cache(streak_key) or 0)
            
            # 检查是否中断连续签到
            yesterday = today - timedelta(days=1)
            if not redis_client.exists(f"checkin:{user_id}:{yesterday}"):
                current_streak = 0
                
            # 更新连续签到天数
            current_streak += 1
            CacheManager.set_cache(streak_key, str(current_streak), expire=86400 * 31)  # 31天过期
            
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
            CacheManager.set_cache(checkin_key, "1", expire=86400)  # 24小时过期
            
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
    async def get_user_points(db: Session, user_id: int) -> Optional[int]:
        """获取用户总积分"""
        user = db.query(User).filter(User.id == user_id).first()
        return user.points if user else None
        
    @staticmethod
    async def get_point_records(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[PointRecord]:
        """获取用户积分记录"""
        return (
            db.query(PointRecord)
            .filter(PointRecord.user_id == user_id)
            .order_by(PointRecord.created_at.desc())
            .limit(limit)
            .all()
        )
