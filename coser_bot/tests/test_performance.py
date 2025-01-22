"""
性能测试模块
测试API响应时间、并发处理能力和系统可用性
"""
import pytest
import asyncio
import aiohttp
from app.services.points import PointsService
from app.services.verification import VerificationService
from app.services.rights import RightsService
from app.models.user import User
from app.i18n.translations import get_text, Language
from time import time
from statistics import mean, median
from typing import List, Dict, Any

# 测试端点列表
TEST_ENDPOINTS = [
    "/api/v1/users/points",
    "/api/v1/users/checkin",
    "/api/v1/users/verify",
    "/api/v1/rights/transfer",
    "/api/v1/blacklist",
    "/api/v1/translations"
]

async def measure_endpoint_performance(url: str, num_requests: int = 100) -> Dict[str, Any]:
    """测量端点性能指标"""
    async with aiohttp.ClientSession() as session:
        response_times = []
        success_count = 0
        error_counts = {
            "network": 0,
            "server": 0,
            "client": 0
        }
        
        async def make_request():
            start = time()
            try:
                async with session.get(url) as response:
                    response_time = (time() - start) * 1000  # 转换为毫秒
                    response_times.append(response_time)
                    
                    if response.status == 200:
                        return "success"
                    elif response.status >= 500:
                        return "server_error"
                    else:
                        return "client_error"
            except Exception as e:
                return "network_error"
        
        # 执行并发请求
        start_time = time()
        tasks = [make_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time() - start_time
        
        # 统计结果
        for result in results:
            if result == "success":
                success_count += 1
            elif result == "server_error":
                error_counts["server"] += 1
            elif result == "client_error":
                error_counts["client"] += 1
            else:
                error_counts["network"] += 1
        
        # 计算性能指标
        qps = num_requests / total_time if total_time > 0 else 0
        availability = (success_count / num_requests) * 100
        
        # 计算响应时间统计
        if response_times:
            avg_time = mean(response_times)
            med_time = median(response_times)
            p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
        else:
            avg_time = med_time = p99_time = 0
        
        return {
            "qps": qps,
            "availability": availability,
            "total_time": total_time,
            "success_count": success_count,
            "error_counts": error_counts,
            "total_requests": num_requests,
            "response_times": {
                "average": avg_time,
                "median": med_time,
                "p99": p99_time
            }
        }

@pytest.mark.asyncio
async def test_api_response_time():
    """测试API响应时间"""
    base_url = "http://localhost:8000"
    
    for endpoint in TEST_ENDPOINTS:
        url = f"{base_url}{endpoint}"
        print(f"\n测试端点: {endpoint}")
        
        # 执行性能测试
        results = await measure_endpoint_performance(url)
        
        # 验证性能指标
        assert results["qps"] >= 1000, f"QPS({results['qps']:.2f})低于目标值(1000)"
        assert results["availability"] >= 99.9, f"可用性({results['availability']:.2f}%)未达到99.9%要求"
        
        # 输出详细性能报告
        print(f"性能测试报告:")
        print(f"- QPS: {results['qps']:.2f}")
        print(f"- 可用性: {results['availability']:.2f}%")
        print(f"- 响应时间:")
        print(f"  * 平均: {results['response_times']['average']:.2f}ms")
        print(f"  * 中位数: {results['response_times']['median']:.2f}ms")
        print(f"  * P99: {results['response_times']['p99']:.2f}ms")
        print(f"- 总响应时间: {results['total_time']:.2f}秒")
        print(f"- 请求统计:")
        print(f"  * 总请求数: {results['total_requests']}")
        print(f"  * 成功请求: {results['success_count']}")
        print(f"- 错误统计:")
        print(f"  * 网络错误: {results['error_counts']['network']}")
        print(f"  * 服务器错误: {results['error_counts']['server']}")
        print(f"  * 客户端错误: {results['error_counts']['client']}")
        
        # 验证响应时间要求
        assert results['response_times']['p99'] < 200, f"99%响应时间({results['response_times']['p99']:.2f}ms)超过200ms要求"

@pytest.mark.asyncio
async def test_concurrent_requests():
    """测试并发请求处理"""
    base_url = "http://localhost:8000"
    num_requests = 1000  # 提高到1000个并发请求
    
    for endpoint in TEST_ENDPOINTS:
        url = f"{base_url}{endpoint}"
        print(f"\n测试端点: {endpoint}")
        
        # 执行并发测试
        results = await measure_endpoint_performance(url, num_requests)
        
        # 验证性能指标
        assert results["qps"] >= 1000, f"QPS({results['qps']:.2f})低于目标值(1000)"
        print(f"QPS: {results['qps']:.2f}")
        print(f"总响应时间: {results['total_time']:.2f}秒")
        print(f"成功请求数: {results['success_count']}")

@pytest.mark.asyncio
async def test_system_availability():
    """测试系统可用性"""
    url = "http://localhost:8000/health"
    total_requests = 1000
    success_count = 0
    
    async with aiohttp.ClientSession() as session:
        for _ in range(total_requests):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        success_count += 1
            except:
                continue
    
    availability = (success_count / total_requests) * 100
    assert availability >= 99.9, f"系统可用性为{availability}%，未达到99.9%要求"

@pytest.mark.asyncio
async def test_core_features(test_session):
    """测试核心功能"""
    # 测试邮箱验证
    assert VerificationService.is_valid_email("test@example.com")
    
    # 测试签到积分
    user = User(telegram_id="test_user")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    success, points, _ = await PointsService.daily_checkin(test_session, user.id)
    assert success
    assert points > 0
    
    # 测试权益转移
    user2 = User(telegram_id="test_user2")
    test_session.add(user2)
    await test_session.commit()
    await test_session.refresh(user2)
    
    success = await RightsService.transfer_rights(
        test_session,
        user.id,
        user2.id,
        50  # 转移50积分
    )
    assert success

@pytest.mark.asyncio
async def test_multi_language_support():
    """测试多语言支持"""
    # 测试中文
    assert get_text(Language.ZH, "welcome") == "欢迎使用Coser展馆社区机器人！"
    
    # 测试英文
    assert get_text(Language.EN, "welcome") == "Welcome to Coser Gallery Community Bot!"
    
    # 测试俄语
    assert get_text(Language.RU, "welcome") == "Добро пожаловать в бот сообщества Coser Gallery!"
