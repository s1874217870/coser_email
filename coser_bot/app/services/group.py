"""
群组服务模块
处理群组成员管理和邀请系统
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from telegram import Bot, ChatMember, ChatInviteLink
from app.models.user import User
from app.core.redis import redis_client
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import json

class GroupService:
    """群组服务类"""
    
    INVITE_EXPIRE_HOURS = 24  # 邀请链接有效期
    
    @staticmethod
    async def get_member_info(bot: Bot, chat_id: int, user_id: int) -> Optional[ChatMember]:
        """
        获取群组成员信息
        使用getChatMember API替代getUpdates
        
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
            
    @staticmethod
    async def create_invite_link(
        bot: Bot,
        chat_id: int,
        creator_id: int,
        member_limit: int = 1
    ) -> Tuple[bool, str]:
        """
        创建群组邀请链接
        
        参数:
            bot: Telegram Bot实例
            chat_id: 群组ID
            creator_id: 创建者ID
            member_limit: 使用限制人数
        """
        try:
            # 创建临时邀请链接
            invite_link = await bot.create_chat_invite_link(
                chat_id=chat_id,
                expire_date=datetime.now() + timedelta(hours=GroupService.INVITE_EXPIRE_HOURS),
                member_limit=member_limit,
                creates_join_request=True
            )
            
            # 记录邀请链接信息
            invite_data = {
                "link": invite_link.invite_link,
                "creator_id": creator_id,
                "created_at": datetime.now().isoformat(),
                "expire_at": (datetime.now() + timedelta(hours=GroupService.INVITE_EXPIRE_HOURS)).isoformat(),
                "member_limit": member_limit,
                "used_count": 0
            }
            
            # 存储邀请记录
            redis_client.setex(
                f"invite:{invite_link.invite_link}",
                GroupService.INVITE_EXPIRE_HOURS * 3600,
                json.dumps(invite_data)
            )
            
            return True, invite_link.invite_link
            
        except Exception as e:
            print(f"创建邀请链接失败: {e}")
            return False, str(e)
            
    @staticmethod
    async def track_invite_usage(invite_link: str) -> bool:
        """
        跟踪邀请链接使用情况
        
        参数:
            invite_link: 邀请链接
        """
        try:
            invite_key = f"invite:{invite_link}"
            invite_data = redis_client.get(invite_key)
            if not invite_data:
                return False
                
            data = json.loads(invite_data)
            data["used_count"] += 1
            
            # 更新使用记录
            redis_client.setex(
                invite_key,
                GroupService.INVITE_EXPIRE_HOURS * 3600,
                json.dumps(data)
            )
            
            return True
            
        except Exception as e:
            print(f"更新邀请使用记录失败: {e}")
            return False
            
    @staticmethod
    async def handle_join_request(
        bot: Bot,
        chat_id: int,
        user_id: int,
        approve: bool = True
    ) -> bool:
        """
        处理加入请求
        
        参数:
            bot: Telegram Bot实例
            chat_id: 群组ID
            user_id: 用户ID
            approve: 是否批准
        """
        try:
            if approve:
                await bot.approve_chat_join_request(
                    chat_id=chat_id,
                    user_id=user_id
                )
            else:
                await bot.decline_chat_join_request(
                    chat_id=chat_id,
                    user_id=user_id
                )
            return True
            
        except Exception as e:
            print(f"处理加入请求失败: {e}")
            return False
            
    @staticmethod
    async def get_member_count(bot: Bot, chat_id: int) -> int:
        """
        获取群组成员数量
        
        参数:
            bot: Telegram Bot实例
            chat_id: 群组ID
        """
        try:
            chat = await bot.get_chat(chat_id)
            return chat.get_member_count()
        except Exception as e:
            print(f"获取群组成员数量失败: {e}")
            return 0
