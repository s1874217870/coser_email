"""
用户服务模块
处理用户相关的数据库操作
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.mongodb import get_mongodb
from datetime import datetime

class UserService:
    """用户服务类"""
    
    @staticmethod
    async def create_user(db: Session, telegram_id: str):
        """
        创建新用户
        
        参数:
            db: 数据库会话
            telegram_id: Telegram用户ID
        """
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
        
    @staticmethod
    async def get_user_by_telegram_id(db: Session, telegram_id: str):
        """
        通过Telegram ID获取用户
        
        参数:
            db: 数据库会话
            telegram_id: Telegram用户ID
        """
        return db.query(User).filter(User.telegram_id == telegram_id).first()
        
    @staticmethod
    async def update_user_email(db: Session, telegram_id: str, email: str):
        """
        更新用户邮箱
        
        参数:
            db: 数据库会话
            telegram_id: Telegram用户ID
            email: 新的邮箱地址
        """
        user = await UserService.get_user_by_telegram_id(db, telegram_id)
        if user:
            user.email = email
            db.commit()
            db.refresh(user)
        return user
        
    @staticmethod
    async def get_chat_member_info(bot, chat_id: int, user_id: int):
        """
        获取群组成员信息（替代getUpdates方案）
        
        参数:
            bot: Telegram Bot实例
            chat_id: 群组ID
            user_id: 用户ID
        """
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            return member
        except Exception as e:
            print(f"获取群组成员信息失败: {e}")
            return None
