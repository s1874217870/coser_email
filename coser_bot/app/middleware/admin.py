"""
管理员中间件
处理管理员权限验证
"""
from fastapi import Depends, HTTPException, Request
from app.core.config import get_settings
from functools import wraps

settings = get_settings()

async def admin_required(request: Request):
    """
    验证管理员权限
    
    参数:
        request: 请求对象
    """
    auth_token = request.headers.get("Authorization")
    if not auth_token:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
        
    # 验证管理员Token
    try:
        token_type, token = auth_token.split()
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=401, detail="无效的认证类型")
            
        # TODO: 实现Token验证逻辑
        # 临时使用简单的Token比较
        if token != settings.ADMIN_TOKEN:
            raise HTTPException(status_code=403, detail="无效的管理员令牌")
            
        return True
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的认证格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
