"""
群组服务测试模块
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.group import GroupService
from telegram import Bot, ChatMember, ChatInviteLink, Chat
from datetime import datetime, timedelta
import json

@pytest.mark.asyncio
async def test_get_member_info():
    """测试获取群组成员信息"""
    # 创建模拟对象
    mock_bot = AsyncMock(spec=Bot)
    mock_member = MagicMock(spec=ChatMember)
    mock_member.status = "member"
    mock_bot.get_chat_member.return_value = mock_member
    
    # 测试成功获取成员信息
    result = await GroupService.get_member_info(mock_bot, 123, 456)
    assert result is not None
    assert result.status == "member"
    mock_bot.get_chat_member.assert_called_once_with(chat_id=123, user_id=456)
    
    # 测试获取失败
    mock_bot.get_chat_member.side_effect = Exception("API Error")
    result = await GroupService.get_member_info(mock_bot, 123, 456)
    assert result is None

@pytest.mark.asyncio
async def test_create_invite_link(test_redis):
    """测试创建邀请链接"""
    # 创建模拟对象
    mock_bot = AsyncMock(spec=Bot)
    mock_invite = MagicMock(spec=ChatInviteLink)
    mock_invite.invite_link = "https://t.me/joinchat/abc123"
    mock_bot.create_chat_invite_link.return_value = mock_invite
    
    # 测试创建邀请链接
    success, link = await GroupService.create_invite_link(mock_bot, 123, 456)
    assert success
    assert link == "https://t.me/joinchat/abc123"
    
    # 验证Redis中的数据
    invite_data = json.loads(test_redis.get(f"invite:{link}"))
    assert invite_data["creator_id"] == 456
    assert invite_data["member_limit"] == 1
    assert invite_data["used_count"] == 0

@pytest.mark.asyncio
async def test_track_invite_usage(test_redis):
    """测试跟踪邀请链接使用情况"""
    # 准备测试数据
    invite_link = "https://t.me/joinchat/test123"
    invite_data = {
        "link": invite_link,
        "creator_id": 123,
        "created_at": datetime.now().isoformat(),
        "expire_at": (datetime.now() + timedelta(hours=24)).isoformat(),
        "member_limit": 1,
        "used_count": 0
    }
    test_redis.setex(
        f"invite:{invite_link}",
        24 * 3600,
        json.dumps(invite_data)
    )
    
    # 测试更新使用记录
    success = await GroupService.track_invite_usage(invite_link)
    assert success
    
    # 验证更新后的数据
    updated_data = json.loads(test_redis.get(f"invite:{invite_link}"))
    assert updated_data["used_count"] == 1

@pytest.mark.asyncio
async def test_handle_join_request():
    """测试处理加入请求"""
    # 创建模拟对象
    mock_bot = AsyncMock(spec=Bot)
    
    # 测试批准请求
    success = await GroupService.handle_join_request(mock_bot, 123, 456, True)
    assert success
    mock_bot.approve_chat_join_request.assert_called_once_with(
        chat_id=123,
        user_id=456
    )
    
    # 测试拒绝请求
    success = await GroupService.handle_join_request(mock_bot, 123, 456, False)
    assert success
    mock_bot.decline_chat_join_request.assert_called_once_with(
        chat_id=123,
        user_id=456
    )

@pytest.mark.asyncio
async def test_get_member_count():
    """测试获取群组成员数量"""
    # 创建模拟对象
    mock_bot = AsyncMock(spec=Bot)
    mock_chat = MagicMock(spec=Chat)
    mock_chat.get_member_count.return_value = 100
    mock_bot.get_chat.return_value = mock_chat
    
    # 测试获取成员数量
    count = await GroupService.get_member_count(mock_bot, 123)
    assert count == 100
    mock_bot.get_chat.assert_called_once_with(123)
