"""
数据库连接模块
管理数据库连接和会话
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# 数据库连接配置
def get_database_url():
    """获取数据库连接URL"""
    if settings.TESTING:
        return "sqlite+aiosqlite:///./test.db"
    return f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"

# 创建数据库引擎
engine = create_async_engine(
    get_database_url(),
    echo=True,
    future=True
)

# 创建会话工厂
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    """获取数据库会话"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
