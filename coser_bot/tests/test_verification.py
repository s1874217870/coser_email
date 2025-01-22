"""
验证系统测试模块
测试邮箱验证和验证码相关功能
"""
import pytest
import asyncio
from unittest.mock import patch
from app.services.verification import VerificationService
from app.services.email_service import EmailService
from app.i18n.translations import Language
from app.core.redis import redis_client
from app.core.config import get_settings

settings = get_settings()

@pytest.mark.asyncio
async def test_email_format_validation():
    """测试邮箱格式验证"""
    # 有效邮箱测试
    valid_emails = [
        "test@example.com",
        "user.name@domain.com",
        "user+label@domain.co.uk"
    ]
    for email in valid_emails:
        assert VerificationService.is_valid_email(email) is True
        
    # 无效邮箱测试
    invalid_emails = [
        "invalid.email",
        "@domain.com",
        "user@",
        "user@domain",
        "user name@domain.com"
    ]
    for email in invalid_emails:
        assert VerificationService.is_valid_email(email) is False

@pytest.mark.asyncio
async def test_verification_code():
    """测试验证码功能"""
    test_id = "test_user:123456"
    code = "123456"
    
    # 存储验证码
    redis_client.setex(f"verify_code:{test_id}", 600, code)
    
    # 测试验证码验证
    assert await VerificationService.verify_code(test_id, code) is True
    assert await VerificationService.verify_code(test_id, "654321") is False
    
    # 测试验证码过期
    redis_client.delete(f"verify_code:{test_id}")
    assert await VerificationService.verify_code(test_id, code) is False

@pytest.mark.asyncio
async def test_rate_limit():
    """测试IP限流"""
    test_id = "test_ip:127.0.0.1"
    
    # 清除之前的限流记录
    redis_client.delete(f"verify_retry:{test_id}")
    
    # 测试正常请求（每小时最多5次）
    for _ in range(5):
        assert await VerificationService.check_retry_limit(test_id) is True
        
    # 测试超出限制（第6次应该失败）
    assert await VerificationService.check_retry_limit(test_id) is False

@pytest.mark.asyncio
@patch('smtplib.SMTP')
async def test_email_sending(mock_smtp):
    """测试邮件发送"""
    # 配置SMTP模拟
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.send_message.return_value = None
    
    # 测试中文邮件
    result_zh = await EmailService.send_verification_email(
        settings.SMTP_USERNAME,
        "123456",
        Language.ZH
    )
    assert result_zh is True
    
    # 测试英文邮件
    result_en = await EmailService.send_verification_email(
        settings.SMTP_USERNAME,
        "123456",
        Language.EN
    )
    assert result_en is True
    
    # 测试俄语邮件
    result_ru = await EmailService.send_verification_email(
        settings.SMTP_USERNAME,
        "123456",
        Language.RU
    )
    assert result_ru is True
    
    # 验证SMTP调用
    assert mock_smtp_instance.send_message.call_count == 3

if __name__ == "__main__":
    asyncio.run(pytest.main(["-v", __file__]))
