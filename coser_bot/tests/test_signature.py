"""
签名验证测试模块
"""
import pytest
from fastapi import Request, HTTPException
from app.middleware.signature import verify_signature, verify_hmac_signature
import time
import hmac
import hashlib
from app.core.config import get_settings

settings = get_settings()

async def create_test_request(headers: dict | None = {}, body: str = "") -> Request:
    """创建测试请求"""
    scope = {
        "type": "http",
        "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
        "method": "POST",
        "client": ("127.0.0.1", 12345),  # 添加客户端信息
    }
    
    class MockReceive:
        async def __call__(self):
            return {"type": "http.request", "body": body.encode()}
            
    return Request(scope, MockReceive(), None)

def generate_signature(timestamp: str, nonce: str, body: str) -> str:
    """生成测试签名"""
    params = [timestamp, nonce, body]
    params.sort()
    message = ''.join(params)
    
    key = settings.SECRET_KEY.encode('utf-8')
    message = message.encode('utf-8')
    return hmac.new(key, message, hashlib.sha256).hexdigest()

@pytest.mark.asyncio
async def test_verify_signature_success():
    """测试有效签名验证"""
    timestamp = str(int(time.time()))
    nonce = "test_nonce"
    body = '{"test": "data"}'
    signature = generate_signature(timestamp, nonce, body)
    
    headers = {
        "X-Signature": signature,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce
    }
    
    request = await create_test_request(headers, body)
    # 不应抛出异常
    await verify_signature(request)

@pytest.mark.asyncio
async def test_verify_signature_missing_headers():
    """测试缺少签名信息"""
    request = await create_test_request()
    with pytest.raises(HTTPException) as exc:
        await verify_signature(request)
    assert exc.value.status_code == 401
    assert "缺少签名信息" in exc.value.detail

@pytest.mark.asyncio
async def test_verify_signature_expired():
    """测试过期签名"""
    timestamp = str(int(time.time()) - 600)  # 10分钟前
    nonce = "test_nonce"
    body = '{"test": "data"}'
    signature = generate_signature(timestamp, nonce, body)
    
    headers = {
        "X-Signature": signature,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce
    }
    
    request = await create_test_request(headers, body)
    with pytest.raises(HTTPException) as exc:
        await verify_signature(request)
    assert exc.value.status_code == 401
    assert "签名已过期" in exc.value.detail

@pytest.mark.asyncio
async def test_verify_signature_invalid():
    """测试无效签名"""
    timestamp = str(int(time.time()))
    nonce = "test_nonce"
    body = '{"test": "data"}'
    signature = "invalid_signature"
    
    headers = {
        "X-Signature": signature,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce
    }
    
    request = await create_test_request(headers, body)
    with pytest.raises(HTTPException) as exc:
        await verify_signature(request)
    assert exc.value.status_code == 401
    assert "无效的签名" in exc.value.detail
