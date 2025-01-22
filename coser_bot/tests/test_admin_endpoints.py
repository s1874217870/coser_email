"""
管理员接口测试模块
测试管理员相关的API接口
"""
import pytest
import pytest_asyncio
from app.core.auth import Auth
from app.models.admin import AdminUser, AdminRole
from app.models.user import User

@pytest_asyncio.fixture
async def admin_token(test_admin):
    """获取管理员令牌"""
    # 使用已创建的测试管理员生成令牌
    token = Auth.create_access_token({"sub": str(test_admin.id)})
    return token

@pytest.mark.asyncio
async def test_ban_user(client, admin_token):
    """测试封禁用户"""
    print("\n=== 测试封禁用户 ===")
    
    response = await client.put(
        "/admin/users/123456/ban",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"封禁响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "用户已封禁"

@pytest.mark.asyncio
async def test_unban_user(client, admin_token):
    """测试解封用户"""
    print("\n=== 测试解封用户 ===")
    
    response = await client.put(
        "/admin/users/123456/unban",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"解封响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "用户已解封"

@pytest.mark.asyncio
async def test_adjust_points(client, admin_token):
    """测试调整积分"""
    print("\n=== 测试调整积分 ===")
    
    response = await client.put(
        "/admin/users/123456/points",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={
            "points": -100,  # 减少100积分
            "reason": "测试调整积分"
        }
    )
    
    print(f"调整积分响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "积分调整成功"

@pytest.mark.asyncio
async def test_get_user_stats(client, admin_token):
    """测试获取用户统计"""
    response = await client.get(
        "/admin/stats/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "active_users" in data
    assert "banned_users" in data
