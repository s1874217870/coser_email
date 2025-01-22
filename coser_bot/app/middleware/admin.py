"""
管理员路由中间件
处理IP白名单和访问控制
"""
from fastapi import Request, HTTPException, status
from app.core.redis import redis_client
from app.core.config import get_settings
import ipaddress

settings = get_settings()

async def admin_middleware(request: Request, call_next):
    """
    管理员路由中间件
    检查IP白名单和访问限制
    """
    # 检查是否是管理员路由
    if request.url.path.startswith("/admin"):
        # 获取客户端IP
        client_ip = request.client.host
        
        # 检查IP白名单
        whitelist_key = "admin:ip_whitelist"
        if redis_client.exists(whitelist_key):
            whitelist = redis_client.smembers(whitelist_key)
            if not any(
                ipaddress.ip_address(client_ip) in ipaddress.ip_network(network)
                for network in whitelist
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="IP地址未授权访问"
                )
                
    response = await call_next(request)
    return response
