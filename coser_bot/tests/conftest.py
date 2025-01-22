"""
测试配置文件
提供测试所需的fixture
"""
import pytest
import fakeredis
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_redis():
    """创建测试Redis客户端"""
    redis_client = fakeredis.FakeStrictRedis(decode_responses=True)
    yield redis_client
    redis_client.flushdb()  # 清理测试数据
