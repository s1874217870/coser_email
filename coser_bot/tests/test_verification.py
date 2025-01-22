"""
验证服务测试模块
"""
import pytest
from app.services.verification import VerificationService
from app.i18n.translations import Language
import re

def test_email_validation():
    """测试邮箱格式验证"""
    # 有效邮箱
    assert VerificationService.is_valid_email("test@example.com")
    assert VerificationService.is_valid_email("user.name+tag@example.co.uk")
    
    # 无效邮箱
    assert not VerificationService.is_valid_email("invalid.email")
    assert not VerificationService.is_valid_email("@example.com")
    assert not VerificationService.is_valid_email("test@.com")
    
@pytest.mark.asyncio
async def test_verify_code(test_redis):
    """测试验证码验证"""
    # 设置测试验证码
    test_redis.setex("verify_code:test_user", 600, "123456")
    
    # 测试正确验证码
    assert await VerificationService.verify_code("test_user", "123456", Language.ZH)
    
    # 测试错误验证码
    assert not await VerificationService.verify_code("test_user", "654321", Language.ZH)
    
    # 测试过期验证码
    test_redis.delete("verify_code:test_user")
    assert not await VerificationService.verify_code("test_user", "123456", Language.ZH)
    
@pytest.mark.asyncio
async def test_retry_limit(test_redis):
    """测试重试限制"""
    identifier = "test_ip"
    limit = 5
    period = 3600
    
    # 测试未超出限制
    for i in range(limit):
        assert await VerificationService.check_retry_limit(identifier, limit, period)
        
    # 测试超出限制
    assert not await VerificationService.check_retry_limit(identifier, limit, period)
