"""
邮件服务模块
处理邮件发送和验证相关功能
"""
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings
from app.i18n.translations import Language, get_text

settings = get_settings()

class EmailService:
    """邮件服务类"""
    
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
    async def send_verification_email(to_email: str, code: str, lang: Language = Language.ZH) -> bool:
        """
        发送验证码邮件
        
        参数:
            to_email: 目标邮箱
            code: 验证码
            lang: 语言设置
        """
        try:
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USERNAME
            msg['To'] = to_email
            msg['Subject'] = get_text(lang, "email_subject")
            
            # 邮件正文
            body = get_text(lang, "email_body", code=code)
            msg.attach(MIMEText(body, 'plain'))
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
