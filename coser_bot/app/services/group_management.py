"""
群组管理服务模块
处理Telegram群组管理相关功能
"""
from telegram import Bot, ChatPermissions
from telegram.error import TelegramError
from app.core.config import get_settings
from app.models.admin import AdminLog
from datetime import datetime, timedelta
from typing import Optional
import logging

settings = get_settings()

class GroupManagementService:
    """群组管理服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.log_group_id = settings.TELEGRAM_LOG_GROUP_ID
        
    async def mute_user(
        self,
        chat_id: int,
        user_id: int,
        duration: Optional[int] = None,
        reason: str = ""
    ) -> bool:
        """
        禁言用户
        
        参数:
            chat_id: 群组ID
            user_id: 用户ID
            duration: 禁言时长（分钟），None表示永久
            reason: 禁言原因
        """
        try:
            # 设置禁言权限
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_invite_users=False,
                can_send_audios=False,
                can_send_documents=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False
            )
            
            # 计算解除时间
            until_date = None
            if duration:
                until_date = datetime.utcnow() + timedelta(minutes=duration)
                
            # 执行禁言
            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions,
                until_date=until_date
            )
            
            # 发送禁言通知
            duration_text = f"{duration}分钟" if duration else "永久"
            message = (
                f"用户 {user_id} 已被禁言\n"
                f"时长: {duration_text}\n"
                f"原因: {reason}"
            )
            await self.bot.send_message(
                chat_id=self.log_group_id,
                text=message
            )
            
            return True
            
        except TelegramError as e:
            logging.error(f"禁言用户失败: {e}")
            return False
            
    async def unmute_user(
        self,
        chat_id: int,
        user_id: int,
        reason: str = ""
    ) -> bool:
        """
        解除用户禁言
        
        参数:
            chat_id: 群组ID
            user_id: 用户ID
            reason: 解除原因
        """
        try:
            # 恢复默认权限
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_invite_users=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True
            )
            
            # 执行解除禁言
            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions
            )
            
            # 发送解除通知
            message = (
                f"用户 {user_id} 的禁言已解除\n"
                f"原因: {reason}"
            )
            await self.bot.send_message(
                chat_id=self.log_group_id,
                text=message
            )
            
            return True
            
        except TelegramError as e:
            logging.error(f"解除禁言失败: {e}")
            return False
            
    async def get_chat_member(self, chat_id: int, user_id: int):
        """
        获取群组成员信息
        
        参数:
            chat_id: 群组ID
            user_id: 用户ID
        """
        try:
            return await self.bot.get_chat_member(
                chat_id=chat_id,
                user_id=user_id
            )
        except TelegramError as e:
            logging.error(f"获取群组成员信息失败: {e}")
            return None

# 创建服务实例
group_service = GroupManagementService()
