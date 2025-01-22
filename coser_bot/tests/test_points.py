"""
积分服务测试模块
"""
import pytest
from app.services.points import PointsService
from app.models.user import User, PointRecord
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_daily_checkin(test_session, test_redis):
    """测试每日签到"""
    # 创建测试用户
    user = User(telegram_id="test_user")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    # 测试首次签到
    success, points, message = await PointsService.daily_checkin(test_session, user.id)
    assert success
    assert points == PointsService.DAILY_CHECKIN_POINTS
    assert "签到成功" in message
    
    # 测试重复签到
    success, points, message = await PointsService.daily_checkin(test_session, user.id)
    assert not success
    assert points == 0
    assert "今日已签到" in message
    
    # 测试连续签到奖励
    # 模拟6天的签到记录
    yesterday = datetime.now().date() - timedelta(days=1)
    test_redis.setex(f"checkin:{user.id}:{yesterday}", 86400, 1)
    test_redis.setex(f"checkin_streak:{user.id}", 86400 * 31, 6)
    
    # 第7天签到
    success, points, message = await PointsService.daily_checkin(test_session, user.id)
    assert success
    assert points == PointsService.DAILY_CHECKIN_POINTS + PointsService.WEEKLY_BONUS_POINTS
    assert "连续7天奖励" in message

@pytest.mark.asyncio
async def test_get_user_points(test_session):
    """测试获取用户积分"""
    # 创建测试用户
    user = User(telegram_id="test_user", points=100)
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    points = await PointsService.get_user_points(test_session, user.id)
    assert points == 100
    
@pytest.mark.asyncio
async def test_get_point_records(test_session):
    """测试获取积分记录"""
    # 创建测试用户
    user = User(telegram_id="test_user")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    # 创建测试积分记录
    records = [
        PointRecord(user_id=user.id, points=10, type=1, description="签到"),
        PointRecord(user_id=user.id, points=20, type=2, description="活动"),
        PointRecord(user_id=user.id, points=30, type=3, description="转移")
    ]
    test_session.add_all(records)
    await test_session.commit()
    
    # 获取积分记录
    result = await PointsService.get_point_records(test_session, user.id, limit=3)
    assert len(result) == 3
    assert result[0].points == 30  # 最新记录
    assert result[1].points == 20
    assert result[2].points == 10
