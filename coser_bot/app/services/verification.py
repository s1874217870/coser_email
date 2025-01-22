"""
验证服务模块
处理邮箱验证和验证码验证
"""
from app.core.redis import redis_client, CacheManager
from app.services.email_service import EmailService
from app.i18n.translations import Language
from app.core.config import get_settings
import re
from datetime import datetime, timedelta

settings = get_settings()

class VerificationService:
    """验证服务类"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    async def verify_code(identifier: str, code: str, lang: Language = Language.ZH) -> bool:
        """验证用户提供的验证码并发送验证邮件"""
        verify_key = CacheManager.generate_key(CacheManager.PREFIX_VERIFY_CODE, identifier)
        stored_code = CacheManager.get_cache(verify_key)
        if not stored_code or stored_code != code:
            return False
            
        # 发送验证邮件
        try:
            await EmailService.send_verification_email(
                settings.SMTP_USERNAME,
                code,
                lang
            )
            
            # 记录验证成功
            success_key = CacheManager.generate_key("verify_success", identifier)
            CacheManager.set_cache(success_key, "1", expire=600)  # 10分钟有效期
            
            return True
        except Exception as e:
            print(f"发送验证邮件失败: {e}")
            return False
    
    @staticmethod
    async def check_retry_limit(identifier: str, limit: int = 5, period: int = 3600) -> bool:
        """检查是否超出重试限制"""
        retry_key = CacheManager.generate_key("verify_retry", identifier)
        retry_count = CacheManager.incr_with_expire(retry_key, period)
        return retry_count is not None and retry_count <= limit
