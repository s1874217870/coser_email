"""
数据库连接模块
处理SQLAlchemy数据库连接
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# 构建数据库URL
DATABASE_URL = (
    f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,           # 连接池大小
    max_overflow=5,         # 最大溢出连接数
    pool_timeout=30,        # 连接池超时时间
    pool_recycle=1800,      # 连接回收时间（30分钟）
    pool_pre_ping=True      # 连接前ping
)

# 创建会话工厂
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False         # 禁用自动刷新以提高性能
)

async def get_db():
    """获取数据库会话"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
