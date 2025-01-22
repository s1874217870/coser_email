"""
管理员模型测试模块
测试管理员用户和日志相关功能
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.admin import AdminUser, AdminLog, AdminRole
from datetime import datetime

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    """测试数据库会话"""
    # 创建测试数据库表
    AdminUser.metadata.create_all(bind=engine)
    AdminLog.metadata.create_all(bind=engine)
    
    # 创建测试会话
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 清理测试数据库
        AdminUser.metadata.drop_all(bind=engine)
        AdminLog.metadata.drop_all(bind=engine)

@pytest.fixture
def test_admin(db):
    """创建测试管理员用户"""
    admin = AdminUser(
        username="test_admin",
        password_hash="hashed_password",
        role=AdminRole.MODERATOR
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.mark.asyncio
async def test_create_admin_user(db):
    """测试创建管理员用户"""
    admin = AdminUser(
        username="admin1",
        password_hash="hashed_password",
        role=AdminRole.SUPERADMIN
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    assert admin.id is not None
    assert admin.username == "admin1"
    assert admin.role == AdminRole.SUPERADMIN
    assert admin.is_active is True

@pytest.mark.asyncio
async def test_create_admin_log(db, test_admin):
    """测试创建管理员日志"""
    log = AdminLog(
        admin_id=test_admin.id,
        action="ban_user",
        target_type="user",
        target_id="123456",
        details="Ban user for spam",
        ip_address="127.0.0.1"
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    assert log.id is not None
    assert log.admin_id == test_admin.id
    assert log.action == "ban_user"
    assert log.target_type == "user"
