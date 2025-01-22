"""
验证服务模块
处理邮箱验证和验证码验证
"""
from app.core.redis import redis_client
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
        """
        验证邮箱格式
        
        参数:
            email: 待验证的邮箱地址
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    async def verify_code(identifier: str, code: str, lang: Language = Language.ZH) -> bool:
        """
        验证用户提供的验证码并发送验证邮件
        
        参数:
            identifier: 用户标识（可以是用户ID或其他标识）
            code: 用户提供的验证码
            lang: 用户语言设置
        """
        stored_code = redis_client.get(f"verify_code:{identifier}")
        if not stored_code:
            return False
            
        # 验证码匹配检查
        if stored_code != code:
            return False
            
        # 发送验证邮件
        try:
            # 发送验证邮件到指定邮箱
            await EmailService.send_verification_email(
                settings.SMTP_USERNAME,  # 目标邮箱（固定的验证邮箱）
                code,
                lang
            )
            
            # 记录验证成功
            redis_client.setex(
                f"verify_success:{identifier}",
                600,  # 10分钟有效期
                "1"
            )
            
            return True
        except Exception as e:
            print(f"发送验证邮件失败: {e}")
            return False
    
    @staticmethod
    async def check_retry_limit(identifier: str, limit: int = 5, period: int = 3600) -> bool:
        """
        检查是否超出重试限制
        
        参数:
            identifier: 用户标识（可以是用户ID或IP地址）
            limit: 限制次数
            period: 时间周期(秒)
        返回:
            bool: 是否未超出限制
        """
        key = f"verify_retry:{identifier}"
        retry_count = redis_client.incr(key)
        
        if retry_count == 1:
            redis_client.expire(key, period)
            
        return retry_count <= limit
