"""
邮件服务测试模块
"""
import pytest
from app.services.email_service import EmailService
from app.i18n.translations import Language
from unittest.mock import patch

@pytest.mark.asyncio
async def test_send_verification_email():
    """测试发送验证邮件"""
    with patch('app.tasks.email_tasks.send_verification_email.delay') as mock_task:
        # 测试发送邮件
        result = await EmailService.send_verification_email(
            "test@example.com",
            "123456",
            Language.ZH
        )
        assert result is True
        mock_task.assert_called_once()
        
        # 验证任务参数
        args = mock_task.call_args[0]
        assert args[0] == "test@example.com"
        assert args[1] == "123456"
        assert args[2] == Language.ZH.value

@pytest.mark.asyncio
async def test_send_verification_email_with_different_languages():
    """测试不同语言的验证邮件"""
    with patch('app.tasks.email_tasks.send_verification_email.delay') as mock_task:
        # 测试中文邮件
        await EmailService.send_verification_email(
            "test@example.com",
            "123456",
            Language.ZH
        )
        assert mock_task.call_args[0][2] == Language.ZH.value
        
        # 测试英文邮件
        await EmailService.send_verification_email(
            "test@example.com",
            "123456",
            Language.EN
        )
        assert mock_task.call_args[0][2] == Language.EN.value
        
        # 测试俄语邮件
        await EmailService.send_verification_email(
            "test@example.com",
            "123456",
            Language.RU
        )
        assert mock_task.call_args[0][2] == Language.RU.value

@pytest.mark.asyncio
async def test_send_verification_email_error_handling():
    """测试邮件发送错误处理"""
    with patch('app.tasks.email_tasks.send_verification_email.delay', side_effect=Exception("测试异常")):
        result = await EmailService.send_verification_email(
            "test@example.com",
            "123456",
            Language.ZH
        )
        assert result is False
