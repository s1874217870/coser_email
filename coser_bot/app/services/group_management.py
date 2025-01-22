"""
群组管理服务模块
处理群组相关的管理功能
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.user import User
from app.models.admin import AdminLog
from app.core.redis import redis_client
from app.services.group import GroupService
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class GroupManagementService:
    """群组管理服务类"""
    
    @staticmethod
    async def get_group_members(
        bot: Any,
        chat_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取群组成员列表"""
        try:
            members = []
            async for member in bot.get_chat_members(chat_id):
                members.append({
                    "user_id": member.user.id,
                    "username": member.user.username,
                    "status": member.status,
                    "joined_date": member.joined_date,
                    "permissions": member.permissions.to_dict() if member.permissions else {}
                })
            return members[skip:skip + limit]
        except Exception as e:
            print(f"获取群组成员失败: {e}")
            return []
            
    @staticmethod
    async def update_member_permissions(
        bot: Any,
        chat_id: int,
        user_id: int,
        permissions: Dict[str, bool],
        admin_id: int,
        db: AsyncSession
    ) -> bool:
        """更新成员权限"""
        try:
            # 更新权限
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions
            )
            
            # 记录操作日志
            log = AdminLog(
                admin_id=admin_id,
                action="update_permissions",
                target_type="user",
                target_id=str(user_id),
                details=f"更新用户 {user_id} 的群组权限"
            )
            db.add(log)
            await db.commit()
            
            return True
        except Exception as e:
            print(f"更新成员权限失败: {e}")
            await db.rollback()
            return False
            
    @staticmethod
    async def kick_member(
        bot: Any,
        chat_id: int,
        user_id: int,
        admin_id: int,
        reason: str,
        db: AsyncSession
    ) -> bool:
        """踢出群组成员"""
        try:
            await bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                until_date=datetime.now() + timedelta(seconds=35)  # 踢出后允许重新加入
            )
            
            # 记录操作日志
            log = AdminLog(
                admin_id=admin_id,
                action="kick_member",
                target_type="user",
                target_id=str(user_id),
                details=f"踢出用户 {user_id}，原因：{reason}"
            )
            db.add(log)
            await db.commit()
            
            return True
        except Exception as e:
            print(f"踢出成员失败: {e}")
            await db.rollback()
            return False
            
    @staticmethod
    async def ban_member(
        bot: Any,
        chat_id: int,
        user_id: int,
        admin_id: int,
        reason: str,
        db: AsyncSession
    ) -> bool:
        """封禁群组成员"""
        try:
            await bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id
            )
            
            # 记录操作日志
            log = AdminLog(
                admin_id=admin_id,
                action="ban_member",
                target_type="user",
                target_id=str(user_id),
                details=f"封禁用户 {user_id}，原因：{reason}"
            )
            db.add(log)
            await db.commit()
            
            return True
        except Exception as e:
            print(f"封禁成员失败: {e}")
            await db.rollback()
            return False
            
    @staticmethod
    async def unban_member(
        bot: Any,
        chat_id: int,
        user_id: int,
        admin_id: int,
        db: AsyncSession
    ) -> bool:
        """解封群组成员"""
        try:
            await bot.unban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                only_if_banned=True
            )
            
            # 记录操作日志
            log = AdminLog(
                admin_id=admin_id,
                action="unban_member",
                target_type="user",
                target_id=str(user_id),
                details=f"解封用户 {user_id}"
            )
            db.add(log)
            await db.commit()
            
            return True
        except Exception as e:
            print(f"解封成员失败: {e}")
            await db.rollback()
            return False
            
    @staticmethod
    async def get_banned_members(
        bot: Any,
        chat_id: int
    ) -> List[Dict[str, Any]]:
        """获取被封禁的成员列表"""
        try:
            banned_members = []
            async for member in bot.get_chat_members(
                chat_id,
                filter="banned"
            ):
                banned_members.append({
                    "user_id": member.user.id,
                    "username": member.user.username,
                    "banned_at": member.joined_date
                })
            return banned_members
        except Exception as e:
            print(f"获取封禁列表失败: {e}")
            return []
