"""
认证模块测试
"""
import pytest
from datetime import timedelta
from app.core.auth import Auth
from app.models.admin import AdminUser, AdminRole
from app.schemas.admin import Token
from sqlalchemy.orm import Session
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_password_hashing():
    """测试密码哈希"""
    password = "testpassword123"
    hashed = Auth.get_password_hash(password)
    
    assert Auth.verify_password(password, hashed)
    assert not Auth.verify_password("wrongpassword", hashed)

@pytest.mark.asyncio
async def test_token_creation():
    """测试令牌创建"""
    data = {"sub": "1"}
    expires = timedelta(minutes=30)
    
    token = Auth.create_access_token(data, expires)
    assert isinstance(token, str)
    assert len(token) > 0

@pytest.mark.asyncio
async def test_token_blacklist():
    """测试令牌黑名单"""
    data = {"sub": "1"}
    token = Auth.create_access_token(data)
    
    # 将令牌加入黑名单
    result = await Auth.blacklist_token(token)
    assert result is True
    
    # 验证令牌已被注销
    with pytest.raises(HTTPException) as exc_info:
        await Auth.get_current_admin(token)
    assert exc_info.value.status_code == 401
