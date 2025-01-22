"""
邮件服务模块
处理邮件发送功能
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings
from app.i18n.translations import Language, get_text

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
            message = MIMEMultipart()
            message["From"] = settings.SMTP_USERNAME
            message["To"] = to_email
            message["Subject"] = get_text(lang, "email_subject")
            
            body = get_text(lang, "email_body", code=code)
            message.attach(MIMEText(body, "plain"))
            
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=True
            )
            return True
            
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
