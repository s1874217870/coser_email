"""
权益服务模块
处理用户权益转移相关的业务逻辑
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.models.user import User
from app.core.redis import redis_client
from datetime import datetime, timedelta
from typing import Tuple, Optional
import json

class RightsService:
    """权益服务类"""
    
    TRANSFER_COOLDOWN_DAYS = 90  # 转移冷却期
    ANNUAL_TRANSFER_LIMIT = 3    # 年度转移限制
    CONFIRMATION_HOURS = 24      # 确认期
    
    @staticmethod
    async def can_transfer_rights(db: AsyncSession, user_id: int) -> Tuple[bool, str]:
        """
        检查用户是否可以转移权益
        
        参数:
            db: 数据库会话
            user_id: 用户ID
        """
        # 检查用户是否存在
        user = await db.get(User, user_id)
        if not user:
            return False, "用户不存在"
            
        # 检查冷却期
        last_transfer = redis_client.get(f"last_transfer:{user_id}")
        if last_transfer:
            last_date = datetime.fromisoformat(last_transfer)
            days_since = (datetime.now() - last_date).days
            if days_since < RightsService.TRANSFER_COOLDOWN_DAYS:
                return False, f"转移冷却中，还需等待{RightsService.TRANSFER_COOLDOWN_DAYS - days_since}天"
                
        # 检查年度限制
        current_year = datetime.now().year
        transfer_count = int(redis_client.get(f"transfer_count:{user_id}:{current_year}") or 0)
        if transfer_count >= RightsService.ANNUAL_TRANSFER_LIMIT:
            return False, f"已达到年度转移限制({RightsService.ANNUAL_TRANSFER_LIMIT}次)"
            
        return True, "可以转移权益"
        
    @staticmethod
    async def initiate_transfer(
        db: AsyncSession,
        from_user_id: int,
        to_user_id: int,
        rights_data: dict
    ) -> Tuple[bool, str]:
        """
        发起权益转移
        
        参数:
            db: 数据库会话
            from_user_id: 转出用户ID
            to_user_id: 接收用户ID
            rights_data: 权益数据
        """
        # 检查双方用户是否存在
        from_user = await db.get(User, from_user_id)
        to_user = await db.get(User, to_user_id)
        if not from_user or not to_user:
            return False, "用户不存在"
            
        # 检查是否可以转移
        can_transfer, message = await RightsService.can_transfer_rights(db, from_user_id)
        if not can_transfer:
            return False, message
            
        # 创建转移请求
        transfer_id = f"transfer:{from_user_id}:{to_user_id}:{datetime.now().isoformat()}"
        transfer_data = {
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "rights_data": rights_data,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # 存储转移请求（24小时有效期）
        redis_client.setex(
            transfer_id,
            RightsService.CONFIRMATION_HOURS * 3600,
            json.dumps(transfer_data)
        )
        
        return True, transfer_id
        
    @staticmethod
    async def confirm_transfer(
        db: AsyncSession,
        transfer_id: str,
        confirmation_code: str
    ) -> Tuple[bool, str]:
        """
        确认权益转移
        
        参数:
            db: 数据库会话
            transfer_id: 转移请求ID
            confirmation_code: 确认码
        """
        # 获取转移请求
        transfer_data = redis_client.get(transfer_id)
        if not transfer_data:
            return False, "转移请求不存在或已过期"
            
        transfer = json.loads(transfer_data)
        if transfer["status"] != "pending":
            return False, "转移请求已处理"
            
        # 验证确认码
        stored_code = redis_client.get(f"transfer_code:{transfer_id}")
        if not stored_code or stored_code != confirmation_code:
            return False, "确认码错误"
            
        try:
            # 执行权益转移
            from_user = await db.get(User, transfer["from_user_id"])
            to_user = await db.get(User, transfer["to_user_id"])
            
            # 转移积分
            points = transfer["rights_data"].get("points", 0)
            if points > 0 and from_user.points >= points:
                from_user.points -= points
                to_user.points += points
                
            # 更新转移记录
            current_year = datetime.now().year
            redis_client.incr(f"transfer_count:{from_user.id}:{current_year}")
            redis_client.set(f"last_transfer:{from_user.id}", datetime.now().isoformat())
            
            # 更新转移状态
            transfer["status"] = "completed"
            redis_client.setex(
                transfer_id,
                RightsService.CONFIRMATION_HOURS * 3600,
                json.dumps(transfer)
            )
            
            await db.commit()
            return True, "权益转移成功"
            
        except Exception as e:
            await db.rollback()
            print(f"权益转移失败: {e}")
            return False, "权益转移失败，请稍后重试"
            
    @staticmethod
    async def cancel_transfer(transfer_id: str) -> Tuple[bool, str]:
        """
        取消权益转移
        
        参数:
            transfer_id: 转移请求ID
        """
        # 获取转移请求
        transfer_data = redis_client.get(transfer_id)
        if not transfer_data:
            return False, "转移请求不存在或已过期"
            
        transfer = json.loads(transfer_data)
        if transfer["status"] != "pending":
            return False, "转移请求已处理"
            
        # 更新转移状态
        transfer["status"] = "cancelled"
        redis_client.setex(
            transfer_id,
            RightsService.CONFIRMATION_HOURS * 3600,
            json.dumps(transfer)
        )
        
        return True, "转移请求已取消"
