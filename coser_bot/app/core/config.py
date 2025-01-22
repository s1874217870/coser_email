"""
配置模块
用于加载和管理应用程序配置
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """应用程序设置类"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # 环境配置
    TESTING: bool = False
    
    # Telegram配置
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ADMIN_ID: int
    TELEGRAM_LOG_GROUP_ID: int

    # 数据库配置
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str
    
    # Redis配置
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    
    # MongoDB配置
    MONGODB_URI: str
    MONGODB_DB: str
    
    # 邮件配置
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    
    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

@lru_cache()
def get_settings() -> Settings:
    """获取应用程序设置单例"""
    return Settings()
