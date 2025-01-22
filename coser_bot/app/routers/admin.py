"""
管理后台路由模块
处理管理后台的所有路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.core.response import ResponseModel
from app.models.user import User, PointRecord
from app.core.config import get_settings
from app.middleware.admin import admin_required
from app.services.user import UserService
from app.services.points import PointsService
from app.services.blacklist import BlacklistService
from app.services.group_management import GroupManagementService
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from datetime import datetime, timedelta
from app.services.telegram_bot import bot_service
from app.services.log_service import LogService
from app.core.mongodb import get_mongodb

# 请求体模型
class BatchOperationRequest(BaseModel):
    """批量操作请求模型"""
    operation: str
    items: List[int]
    reason: Optional[str] = None

class PermissionsUpdate(BaseModel):
    """权限更新请求模型"""
    permissions: Dict[str, bool]

class ReasonRequest(BaseModel):
    reason: str

# 获取bot实例的依赖
async def get_bot():
    return bot_service.application.bot

router = APIRouter(prefix="/admin", tags=["admin"])
settings = get_settings()

from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    pageSize: int

@router.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    _: bool = Depends(admin_required)
):
    """获取用户列表"""
    total = await UserService.get_total_users(db)
    users = await UserService.get_users(db, (page - 1) * pageSize, pageSize)
    return ResponseModel.success(data={
        "items": users,
        "total": total,
        "page": page,
        "pageSize": pageSize
    })

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(admin_required)
):
    """获取用户详情"""
    user = await UserService.get_user(db, user_id)
    if not user:
        return ResponseModel.error(message="用户不存在", status_code=404)
    return ResponseModel.success(data=user)

@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    reason: str,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(admin_required)
):
    """封禁用户"""
    success = await UserService.ban_user(db, user_id, reason)
    if not success:
        return ResponseModel.error(message="封禁失败")
    return ResponseModel.success(message="封禁成功")

@router.get("/statistics/overview")
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(admin_required)
):
    """获取统计概览"""
    try:
        stats = {
            "total_users": await UserService.get_total_users(db),
            "active_users": await UserService.get_active_users(db),
            "total_points": await PointsService.get_total_points(db),
            "daily_checkins": await PointsService.get_daily_checkins(db)
        }
        return ResponseModel.success(data=stats)
    except Exception as e:
        return ResponseModel.error(message=str(e))

# 群组管理路由
@router.get("/groups/{chat_id}/members")
async def get_group_members(
    chat_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    bot = Depends(get_bot),
    _: bool = Depends(admin_required)
):
    """获取群组成员列表"""
    try:
        members = await GroupManagementService.get_group_members(
            bot,
            chat_id,
            skip,
            limit
        )
        return ResponseModel.success(data={
            "items": members,
            "total": len(members),
            "skip": skip,
            "limit": limit
        })
    except Exception as e:
        return ResponseModel.error(message=f"获取群组成员失败: {str(e)}")

@router.put("/groups/{chat_id}/members/{user_id}/permissions")
async def update_member_permissions(
    chat_id: int,
    user_id: int,
    request: PermissionsUpdate,
    db: AsyncSession = Depends(get_db),
    bot = Depends(get_bot),
    _: bool = Depends(admin_required)
):
    """更新成员权限"""
    try:
        success = await GroupManagementService.update_member_permissions(
            bot,
            chat_id,
            user_id,
            request.permissions,
            settings.TELEGRAM_ADMIN_ID,
            db
        )
        if not success:
            return ResponseModel.error(message="更新权限失败")
            
        # 记录操作日志
        await LogService.add_log(
            level="info",
            event_type="permission_update",
            description=f"更新用户 {user_id} 的群组权限",
            metadata={"chat_id": chat_id, "permissions": request.permissions}
        )
        return ResponseModel.success(message="更新成功")
    except Exception as e:
        return ResponseModel.error(message=str(e))

@router.post("/groups/{chat_id}/members/{user_id}/kick")
async def kick_member(
    chat_id: int,
    user_id: int,
    request: ReasonRequest,
    db: AsyncSession = Depends(get_db),
    bot = Depends(get_bot),
    _: bool = Depends(admin_required)
):
    """踢出群组成员"""
    try:
        success = await GroupManagementService.kick_member(
            bot,
            chat_id,
            user_id,
            settings.TELEGRAM_ADMIN_ID,
            request.reason,
            db
        )
        if not success:
            return ResponseModel.error(message="踢出失败")
            
        # 记录操作日志
        await LogService.add_log(
            level="warning",
            event_type="member_kick",
            description=f"踢出用户 {user_id}",
            metadata={"chat_id": chat_id, "reason": request.reason}
        )
        return ResponseModel.success(message="踢出成功")
    except Exception as e:
        return ResponseModel.error(message=str(e))

@router.post("/groups/{chat_id}/members/{user_id}/ban")
async def ban_member(
    chat_id: int,
    user_id: int,
    request: ReasonRequest,
    db: AsyncSession = Depends(get_db),
    bot = Depends(get_bot),
    _: bool = Depends(admin_required)
):
    """封禁群组成员"""
    try:
        success = await GroupManagementService.ban_member(
            bot,
            chat_id,
            user_id,
            settings.TELEGRAM_ADMIN_ID,
            request.reason,
            db
        )
        if not success:
            return ResponseModel.error(message="封禁失败")
            
        # 记录操作日志
        await LogService.add_log(
            level="warning",
            event_type="member_ban",
            description=f"封禁用户 {user_id}",
            metadata={"chat_id": chat_id, "reason": request.reason}
        )
        return ResponseModel.success(message="封禁成功")
    except Exception as e:
        return ResponseModel.error(message=str(e))

@router.post("/groups/{chat_id}/members/{user_id}/unban")
async def unban_member(
    chat_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    bot = Depends(get_bot),
    _: bool = Depends(admin_required)
):
    """解封群组成员"""
    try:
        success = await GroupManagementService.unban_member(
            bot,
            chat_id,
            user_id,
            settings.TELEGRAM_ADMIN_ID,
            db
        )
        if not success:
            return ResponseModel.error(message="解封失败")
            
        # 记录操作日志
        await LogService.add_log(
            level="info",
            event_type="member_unban",
            description=f"解封用户 {user_id}",
            metadata={"chat_id": chat_id}
        )
        return ResponseModel.success(message="解封成功")
    except Exception as e:
        return ResponseModel.error(message=str(e))

@router.get("/groups/{chat_id}/banned")
async def get_banned_members(
    chat_id: int,
    bot = Depends(get_bot),
    _: bool = Depends(admin_required)
):
    """获取被封禁的成员列表"""
    try:
        members = await GroupManagementService.get_banned_members(bot, chat_id)
        return ResponseModel.success(data={
            "items": members,
            "total": len(members)
        })
    except Exception as e:
        return ResponseModel.error(message=f"获取被封禁成员列表失败: {str(e)}")

@router.get("/blacklist")
async def get_blacklist(_: bool = Depends(admin_required)):
    """获取黑名单列表"""
    try:
        blacklist = await BlacklistService.get_all_blacklist()
        return ResponseModel.success(data=blacklist)
    except Exception as e:
        return ResponseModel.error(message=f"获取黑名单失败: {str(e)}")

@router.post("/blacklist/{email}")
async def add_to_blacklist(
    email: str,
    reason: str,
    _: bool = Depends(admin_required)
):
    """添加邮箱到黑名单"""
    try:
        success = await BlacklistService.add_to_blacklist(email, reason)
        if not success:
            return ResponseModel.error(message="添加失败")
            
        # 记录操作日志
        await LogService.add_log(
            level="info",
            event_type="blacklist_add",
            description=f"添加邮箱 {email} 到黑名单",
            metadata={"reason": reason}
        )
        return ResponseModel.success(message="添加成功")
    except Exception as e:
        return ResponseModel.error(message=str(e))

@router.delete("/blacklist/{email}")
async def remove_from_blacklist(
    email: str,
    _: bool = Depends(admin_required)
):
    """从黑名单移除邮箱"""
    try:
        success = await BlacklistService.remove_from_blacklist(email)
        if not success:
            return ResponseModel.error(message="移除失败")
            
        # 记录操作日志
        await LogService.add_log(
            level="info",
            event_type="blacklist_remove",
            description=f"从黑名单移除邮箱 {email}"
        )
        return ResponseModel.success(message="移除成功")
    except Exception as e:
        return ResponseModel.error(message=str(e))

@router.get("/logs")
async def get_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    level: Optional[str] = None,
    event_type: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    _: bool = Depends(admin_required)
):
    """获取安全日志"""
    try:
        logs = await LogService.get_logs(
            start_date=start_date,
            end_date=end_date,
            level=level,
            event_type=event_type,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        # 获取日志统计信息
        stats = await LogService.get_log_statistics()
        
        return ResponseModel.success(data={
            "items": logs,
            "total": len(logs),
            "statistics": stats,
            "skip": skip,
            "limit": limit
        })
    except Exception as e:
        return ResponseModel.error(message=f"获取日志失败: {str(e)}")

@router.post("/batch")
async def batch_operation(
    request: BatchOperationRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(admin_required)
):
    """批量操作"""
    try:
        if request.operation == "ban":
            for user_id in request.items:
                await UserService.ban_user(db, user_id, request.reason or "批量封禁")
        elif request.operation == "unban":
            for user_id in request.items:
                await UserService.unban_user(db, user_id)
        elif request.operation == "delete":
            for user_id in request.items:
                await UserService.delete_user(db, user_id)
        else:
            return ResponseModel.error(message="不支持的操作类型")
            
        # 记录操作日志
        await LogService.add_log(
            level="info",
            event_type="batch_operation",
            description=f"批量{request.operation}操作",
            metadata={"items": request.items, "reason": request.reason}
        )
        
        return ResponseModel.success(message="批量操作成功")
    except Exception as e:
        return ResponseModel.error(message=str(e))

@router.get("/translations")
async def get_translations(_: bool = Depends(admin_required)):
    """获取多语言翻译"""
    from app.i18n.translations import TRANSLATIONS
    return ResponseModel.success(data=TRANSLATIONS)

@router.put("/translations/{lang}/{key}")
async def update_translation(
    lang: str,
    key: str,
    value: str,
    _: bool = Depends(admin_required)
):
    """更新翻译"""
    try:
        from app.i18n.translations import Language
        
        # 验证语言代码
        if lang not in Language.__members__.values():
            return ResponseModel.error(message="不支持的语言代码")
            
        # 更新翻译
        db = await get_mongodb()
        collection = db.translations
        
        result = await collection.update_one(
            {"lang": lang, "key": key},
            {"$set": {"value": value}},
            upsert=True
        )
        
        if result.modified_count > 0 or result.upserted_id:
            # 记录操作日志
            await LogService.add_log(
                level="info",
                event_type="translation_update",
                description=f"更新翻译 {lang}.{key}",
                metadata={"value": value}
            )
            return ResponseModel.success(message="更新成功")
        else:
            return ResponseModel.error(message="更新失败")
    except Exception as e:
        return ResponseModel.error(message=f"更新翻译失败: {str(e)}")
