"""
邮件服务模块
处理邮件发送功能
"""
from app.core.config import get_settings
from app.i18n.translations import Language, get_text
from app.tasks.email_tasks import send_verification_email

settings = get_settings()

class EmailService:
    """邮件服务类"""
    
    @staticmethod
    async def send_verification_email(to_email: str, code: str, lang: Language = Language.ZH) -> bool:
        """
        发送验证码邮件
        
        参数:
            to_email: 目标邮箱
            code: 验证码
            lang: 语言设置
        """
        try:
            # 使用Celery异步发送邮件
            send_verification_email.delay(to_email, code, lang.value)
            return True
            
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
