"""
测试配置文件
提供共享的测试夹具
"""
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.admin import AdminUser, AdminRole, Base
from app.core.auth import Auth
from app.core.config import get_settings
from app.core.redis import redis_client
from app.db.database import get_db
from app.routers import admin as admin_router

settings = get_settings()
settings.TESTING = True

# 创建测试数据库引擎
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    echo=True
)

TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 创建测试应用
app = FastAPI()
app.include_router(admin_router.router)

# 替换数据库依赖
async def override_get_db():
    """获取测试数据库会话"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """设置测试数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(lambda ctx: Base.metadata.create_all(ctx))
    yield
    redis_client.flushdb()
    async with engine.begin() as conn:
        await conn.run_sync(lambda ctx: Base.metadata.drop_all(ctx))

@pytest_asyncio.fixture
async def test_db():
    """创建测试数据库会话"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture
async def test_admin(test_db):
    """创建测试管理员"""
    admin = AdminUser(
        username="test_admin",
        password_hash=Auth.get_password_hash("testpass123"),
        role=AdminRole.SUPERADMIN,
        is_active=True
    )
    test_db.add(admin)
    await test_db.commit()
    await test_db.refresh(admin)
    return admin

@pytest_asyncio.fixture
async def client():
    """创建异步测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
