"""
签名验证中间件
处理请求签名验证
"""
from fastapi import Request, HTTPException
from app.core.config import get_settings
from app.core.redis import RateLimit
import hmac
import hashlib
import time
from typing import Optional

settings = get_settings()

async def verify_signature(request: Request):
    """
    验证请求签名并进行IP限流
    
    参数:
        request: 请求对象
    """
    # 获取签名相关信息
    signature = request.headers.get("X-Signature")
    timestamp = request.headers.get("X-Timestamp")
    nonce = request.headers.get("X-Nonce")
    
    if not all([signature, timestamp, nonce]):
        raise HTTPException(status_code=401, detail="缺少签名信息")
        
    # 验证时间戳（5分钟有效期）
    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > 300:
            raise HTTPException(status_code=401, detail="签名已过期")
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的时间戳")
        
    # 获取请求体
    body = await get_request_body(request)
    
    # 验证签名
    if not verify_hmac_signature(signature, timestamp, nonce, body):
        raise HTTPException(status_code=401, detail="无效的签名")
        
    # IP限流检查（测试环境跳过）
    if not settings.TESTING:
        client_ip = request.client.host if request.client else "127.0.0.1"
        if not RateLimit.check_rate_limit(
            f"ip_limit:{client_ip}",
            limit=10,  # 每小时最多10次请求
            period=3600
        ):
            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试"
            )
    # 获取签名相关信息
    signature = request.headers.get("X-Signature")
    timestamp = request.headers.get("X-Timestamp")
    nonce = request.headers.get("X-Nonce")
    
    if not all([signature, timestamp, nonce]):
        raise HTTPException(status_code=401, detail="缺少签名信息")
        
    # 验证时间戳（5分钟有效期）
    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > 300:
            raise HTTPException(status_code=401, detail="签名已过期")
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的时间戳")
        
    # 获取请求体
    body = await get_request_body(request)
    
    # 验证签名
    if not verify_hmac_signature(signature, timestamp, nonce, body):
        raise HTTPException(status_code=401, detail="无效的签名")
        
async def get_request_body(request: Request) -> str:
    """获取请求体内容"""
    body = await request.body()
    return body.decode() if body else ""
    
def verify_hmac_signature(signature: str, timestamp: str, nonce: str, body: str) -> bool:
    """
    验证HMAC签名
    
    参数:
        signature: 签名字符串
        timestamp: 时间戳
        nonce: 随机字符串
        body: 请求体
    """
    # 按字典序拼接参数
    params = [timestamp, nonce, body]
    params.sort()
    message = ''.join(params)
    
    # 使用HMAC-SHA256计算签名
    key = settings.SECRET_KEY.encode('utf-8')
    message = message.encode('utf-8')
    expected = hmac.new(key, message, hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(signature.lower(), expected.lower())
