"""
配置模块
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置类"""
    # Telegram配置
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ADMIN_ID: int
    TELEGRAM_LOG_GROUP_ID: int

    # 邮件配置
    SMTP_SERVER: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    VERIFICATION_EMAIL: str

    # 数据库配置
    DATABASE_URL: str
    REDIS_URL: str

    # 应用配置
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
