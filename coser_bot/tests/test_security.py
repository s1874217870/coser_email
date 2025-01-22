"""
安全机制测试模块
"""
import pytest
from app.services.verification import VerificationService
import re
import fakeredis
from unittest.mock import patch
from app.core.redis import CacheManager

@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis客户端"""
    redis_client = fakeredis.FakeStrictRedis(decode_responses=True)
    
    # 替换Redis客户端
    import app.core.redis
    app.core.redis.redis_client = redis_client
    app.core.redis.CacheManager.redis_client = redis_client
    app.core.redis.RateLimit.redis_client = redis_client
    
    return redis_client

def test_email_validation():
    """测试邮箱格式验证"""
    # 有效邮箱测试用例
    valid_emails = [
        "test@example.com",
        "user.name+tag@example.co.uk",
        "chinese@域名.中国",
        "number123@server.com",
        "under_score@example.com"
    ]
    
    # 无效邮箱测试用例
    invalid_emails = [
        "test@",
        "@example.com",
        "test@.com",
        "test@com",
        "test.com",
        "test@example.",
        "test space@example.com",
        "test@example..com"
    ]
    
    # 验证有效邮箱
    for email in valid_emails:
        assert VerificationService.is_valid_email(email), f"应该接受有效邮箱: {email}"
        
    # 验证无效邮箱
    for email in invalid_emails:
        assert not VerificationService.is_valid_email(email), f"应该拒绝无效邮箱: {email}"

def test_verification_code_format():
    """测试验证码格式"""
    # 生成多个验证码并验证格式
    codes = [VerificationService.generate_verification_code() for _ in range(100)]
    
    for code in codes:
        # 验证长度为6位
        assert len(code) == 6, f"验证码长度应为6位: {code}"
        # 验证全为数字
        assert code.isdigit(), f"验证码应全为数字: {code}"
        # 验证不以0开头
        assert code[0] != '0', f"验证码不应以0开头: {code}"

@pytest.mark.asyncio
async def test_retry_limit():
    """测试重试限制"""
    identifier = "test_ip"
    
    # 测试允许的重试次数
    for i in range(5):
        assert await VerificationService.check_retry_limit(identifier)
    
    # 测试超出限制
    assert not await VerificationService.check_retry_limit(identifier)

@pytest.mark.asyncio
async def test_verification_code_expiry():
    """测试验证码过期"""
    import time
    
    # 生成验证码
    user_id = "test_user"
    code = await VerificationService.generate_and_store_code(user_id)
    
    # 验证码应该有效
    assert await VerificationService.verify_code(user_id, code)
    
    # 等待验证码过期（设置较短的过期时间用于测试）
    time.sleep(2)
    
    # 验证码应该已过期
    assert not await VerificationService.verify_code(user_id, code)
