"""
用户服务模块
处理用户相关的业务逻辑
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from telegram import Bot, ChatMember
from app.models.user import User
from typing import Optional

class UserService:
    """用户服务类"""
    
    @staticmethod
    async def get_user_by_telegram_id(db: AsyncSession, telegram_id: str) -> Optional[User]:
        """
        通过Telegram ID获取用户
        
        参数:
            db: 数据库会话
            telegram_id: Telegram用户ID
        """
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
        
    @staticmethod
    async def create_user(db: AsyncSession, telegram_id: str) -> User:
        """
        创建新用户
        
        参数:
            db: 数据库会话
            telegram_id: Telegram用户ID
        """
        user = User(telegram_id=telegram_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
        
    @staticmethod
    async def get_chat_member_info(bot: Bot, chat_id: int, user_id: int) -> Optional[ChatMember]:
        """
        获取用户在群组中的信息
        
        参数:
            bot: Telegram Bot实例
            chat_id: 群组ID
            user_id: 用户ID
        """
        try:
            return await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        except Exception as e:
            print(f"获取群组成员信息失败: {e}")
            return None
