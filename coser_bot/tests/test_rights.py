"""
权益服务测试模块
"""
import pytest
from app.services.rights import RightsService
from app.models.user import User
from datetime import datetime, timedelta
import json

@pytest.mark.asyncio
async def test_can_transfer_rights(test_session, test_redis):
    """测试权益转移条件检查"""
    # 创建测试用户
    user = User(telegram_id="test_user")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    # 测试首次转移
    can_transfer, message = await RightsService.can_transfer_rights(test_session, user.id)
    assert can_transfer
    assert "可以转移权益" in message
    
    # 测试冷却期限制
    test_redis.set(
        f"last_transfer:{user.id}",
        datetime.now().isoformat()
    )
    can_transfer, message = await RightsService.can_transfer_rights(test_session, user.id)
    assert not can_transfer
    assert "转移冷却中" in message
    
    # 测试年度限制
    current_year = datetime.now().year
    test_redis.set(f"transfer_count:{user.id}:{current_year}", RightsService.ANNUAL_TRANSFER_LIMIT)
    can_transfer, message = await RightsService.can_transfer_rights(test_session, user.id)
    assert not can_transfer
    assert "年度转移限制" in message

@pytest.mark.asyncio
async def test_rights_transfer_flow(test_session, test_redis):
    """测试完整的权益转移流程"""
    # 创建测试用户
    from_user = User(telegram_id="from_user", points=100)
    to_user = User(telegram_id="to_user", points=50)
    test_session.add_all([from_user, to_user])
    await test_session.commit()
    await test_session.refresh(from_user)
    await test_session.refresh(to_user)
    
    # 发起转移
    rights_data = {"points": 30}
    success, transfer_id = await RightsService.initiate_transfer(
        test_session,
        from_user.id,
        to_user.id,
        rights_data
    )
    assert success
    
    # 设置确认码
    confirmation_code = "123456"
    test_redis.setex(f"transfer_code:{transfer_id}", 3600, confirmation_code)
    
    # 确认转移
    success, message = await RightsService.confirm_transfer(
        test_session,
        transfer_id,
        confirmation_code
    )
    assert success
    assert "转移成功" in message
    
    # 验证积分变动
    await test_session.refresh(from_user)
    await test_session.refresh(to_user)
    assert from_user.points == 70
    assert to_user.points == 80
    
    # 验证转移记录
    current_year = datetime.now().year
    transfer_count = int(test_redis.get(f"transfer_count:{from_user.id}:{current_year}"))
    assert transfer_count == 1
    
    # 验证转移状态
    transfer_data = json.loads(test_redis.get(transfer_id))
    assert transfer_data["status"] == "completed"

@pytest.mark.asyncio
async def test_cancel_transfer(test_redis):
    """测试取消权益转移"""
    # 创建测试转移请求
    transfer_id = "test_transfer"
    transfer_data = {
        "status": "pending",
        "from_user_id": 1,
        "to_user_id": 2,
        "rights_data": {"points": 50}
    }
    test_redis.setex(transfer_id, 3600, json.dumps(transfer_data))
    
    # 取消转移
    success, message = await RightsService.cancel_transfer(transfer_id)
    assert success
    assert "已取消" in message
    
    # 验证状态
    transfer_data = json.loads(test_redis.get(transfer_id))
    assert transfer_data["status"] == "cancelled"
