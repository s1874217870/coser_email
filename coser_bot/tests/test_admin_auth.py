"""
管理员认证测试模块
"""
import pytest
import pytest_asyncio
from app.core.auth import Auth
from app.models.admin import AdminUser, AdminRole

@pytest.mark.asyncio
async def test_login(client, test_db, test_admin):
    """测试登录"""
    print("\n=== 测试管理员登录 ===")
    
    # 使用 application/x-www-form-urlencoded 格式
    form_data = {
        "username": "test_admin",
        "password": "testpass123",
        "grant_type": "password"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print(f"发送登录请求: {form_data}")
    response = await client.post(
        "/admin/login",
        headers=headers,
        data=form_data
    )
    
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应内容: {response.text}")
    
    assert response.status_code == 200, "登录失败"
    data = response.json()
    assert "access_token" in data, "响应中缺少access_token"
    assert data["token_type"] == "bearer", "无效的token_type"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client, test_db, test_admin):
    """测试无效凭据登录"""
    print("\n=== 测试无效凭据登录 ===")
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    form_data = {
        "username": "test_admin",
        "password": "wrongpass",
        "grant_type": "password"
    }
    
    print(f"发送无效凭据登录请求")
    response = await client.post(
        "/admin/login",
        headers=headers,
        data=form_data
    )
    
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应内容: {response.text}")
    
    assert response.status_code == 401, "预期应该返回401未授权错误"
    assert "无效的认证凭据" in response.text, "错误消息不符合预期"

@pytest.mark.asyncio
async def test_get_admin_info(client, test_db, test_admin):
    """测试获取管理员信息"""
    print("\n=== 开始测试获取管理员信息 ===")
    print(f"测试管理员ID: {test_admin.id}")
    print(f"测试管理员用户名: {test_admin.username}")
    
    # 先登录获取token
    print("\n尝试登录...")
    login_response = await client.post(
        "/admin/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": "test_admin",
            "password": "testpass123",
            "grant_type": "password"
        }
    )
    print(f"登录响应状态码: {login_response.status_code}")
    print(f"登录响应内容: {login_response.json()}")
    
    assert login_response.status_code == 200, "登录失败"
    token = login_response.json()["access_token"]
    print(f"获取到的令牌: {token[:20]}...")
    
    # 使用token获取管理员信息
    print("\n尝试获取管理员信息...")
    response = await client.get(
        "/admin/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"获取信息响应状态码: {response.status_code}")
    if response.status_code != 200:
        print(f"错误响应: {response.json()}")
    
    assert response.status_code == 200, "获取管理员信息失败"
    
    # 验证返回的管理员信息
    data = response.json()
    print(f"返回的管理员信息: {data}")
    assert data["username"] == "test_admin"
    assert data["role"] == AdminRole.SUPERADMIN.value

@pytest.mark.asyncio
async def test_logout(client, test_db, test_admin):
    """测试注销"""
    # 先登录获取token
    login_response = await client.post(
        "/admin/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": "test_admin",
            "password": "testpass123",
            "grant_type": "password"
        }
    )
    token = login_response.json()["access_token"]
    
    # 注销
    response = await client.post(
        "/admin/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 验证token已失效
    info_response = await client.get(
        "/admin/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert info_response.status_code == 401
