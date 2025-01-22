"""
邮件任务模块
处理异步邮件发送
"""
from app.core.celery import celery_app
from app.i18n.translations import Language
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings
from celery.utils.log import get_task_logger
from app.i18n.translations import get_text, Language

settings = get_settings()
logger = get_task_logger(__name__)

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1分钟后重试
    autoretry_for=(Exception,),
    retry_backoff=True,  # 使用指数退避
    retry_jitter=True    # 添加随机抖动
)
def send_verification_email(self, to_email: str, code: str, lang: str = Language.ZH.value) -> bool:
    """
    发送验证码邮件的异步任务
    
    参数:
        to_email: 目标邮箱
        code: 验证码
        lang: 语言设置
    """
    try:
        message = MIMEMultipart()
        message["From"] = settings.SMTP_USERNAME
        message["To"] = to_email
        # 获取多语言文本
        subject = str(get_text(Language(lang), "email_subject"))
        body = str(get_text(Language(lang), "email_body", code=code))
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # 同步发送邮件
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
            
        logger.info(f"验证邮件发送成功: {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        # 自动重试
        raise self.retry(exc=e)
