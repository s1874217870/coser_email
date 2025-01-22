"""
管理员相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional
from app.models.admin import AdminRole

class AdminLogin(BaseModel):
    """管理员登录请求模型"""
    username: str
    password: str

class AdminCreate(BaseModel):
    """创建管理员请求模型"""
    username: str
    password: str
    role: AdminRole = AdminRole.MODERATOR

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"

class AdminInfo(BaseModel):
    """管理员信息响应模型"""
    id: int
    username: str
    role: AdminRole
    is_active: bool

    class Config:
        from_attributes = True
