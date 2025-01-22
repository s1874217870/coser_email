"""
积分系统测试模块
测试积分相关功能
"""
import pytest
from datetime import datetime, timedelta
from app.services.points import PointsService
from app.models.user import User, PointRecord
from app.core.redis import redis_client
from app.db.database import SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///:memory:"  # 使用内存数据库
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # 允许多线程访问
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    """测试数据库会话"""
    # 创建测试数据库表
    User.metadata.create_all(bind=engine)
    PointRecord.metadata.create_all(bind=engine)
    
    # 创建测试会话
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 清理测试数据库
        User.metadata.drop_all(bind=engine)
        PointRecord.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(telegram_id="test_user", points=0)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.mark.asyncio
async def test_daily_checkin(db, test_user):
    """测试每日签到"""
    # 清除之前的签到记录
    today = datetime.now().date()
    redis_client.delete(f"checkin:{test_user.id}:{today}")
    redis_client.delete(f"checkin_streak:{test_user.id}")
    
    # 测试首次签到
    success, points, message = await PointsService.daily_checkin(db, test_user.id)
    assert success is True
    assert points == PointsService.DAILY_CHECKIN_POINTS
    
    # 测试重复签到
    success, points, message = await PointsService.daily_checkin(db, test_user.id)
    assert success is False
    assert points == 0
    
    # 测试连续签到奖励
    # 模拟连续6天签到
    for i in range(1, 7):
        past_date = today - timedelta(days=i)
        redis_client.setex(f"checkin:{test_user.id}:{past_date}", 86400, 1)
    redis_client.setex(f"checkin_streak:{test_user.id}", 86400 * 31, 6)
    
    # 第7天签到
    redis_client.delete(f"checkin:{test_user.id}:{today}")
    success, points, message = await PointsService.daily_checkin(db, test_user.id)
    assert success is True
    assert points == PointsService.DAILY_CHECKIN_POINTS + PointsService.WEEKLY_BONUS_POINTS

@pytest.mark.asyncio
async def test_activity_points(db, test_user):
    """测试活动积分"""
    # 测试有效积分范围
    success, message = await PointsService.add_activity_points(
        db, test_user.id, 50, "测试活动"
    )
    assert success is True
    
    # 测试无效积分范围
    success, message = await PointsService.add_activity_points(
        db, test_user.id, 150, "超出范围"
    )
    assert success is False
    
    # 验证用户总积分
    user_points = await PointsService.get_user_points(db, test_user.id)
    assert user_points == 50

@pytest.mark.asyncio
async def test_content_points(db, test_user):
    """测试内容发布积分"""
    # 测试有效积分范围
    success, message = await PointsService.add_content_points(
        db, test_user.id, 30, "测试内容"
    )
    assert success is True
    
    # 测试无效积分范围
    success, message = await PointsService.add_content_points(
        db, test_user.id, 60, "超出范围"
    )
    assert success is False
    
    # 验证积分记录
    records = await PointsService.get_point_records(db, test_user.id)
    assert len(records) == 1
    assert records[0].points == 30
    assert records[0].type == 3  # 3:内容
