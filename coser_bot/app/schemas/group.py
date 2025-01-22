"""
群组管理相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional

class MuteRequest(BaseModel):
    """禁言请求模型"""
    user_id: int
    duration: Optional[int] = None
    reason: str = ""

class UnmuteRequest(BaseModel):
    """解除禁言请求模型"""
    user_id: int
    reason: str = ""

class MuteResponse(BaseModel):
    """禁言响应模型"""
    message: str
    success: bool

class UnmuteResponse(BaseModel):
    """解除禁言响应模型"""
    message: str
    success: bool

class MemberInfo(BaseModel):
    """群组成员信息模型"""
    user_id: int
    status: str
    is_member: bool
    can_send_messages: bool
    joined_date: Optional[str] = None
