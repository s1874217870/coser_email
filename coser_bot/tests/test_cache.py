"""
缓存管理测试模块
"""
import pytest
from app.core.redis import CacheManager
import fakeredis
import json
from datetime import datetime, timedelta
import time

@pytest.fixture
def redis_client():
    """创建fakeredis客户端用于测试"""
    client = fakeredis.FakeStrictRedis(decode_responses=True)
    return client

@pytest.fixture(autouse=True)
def mock_redis(mocker, redis_client):
    """Mock Redis客户端"""
    mocker.patch('app.core.redis.redis_client', redis_client)
    return redis_client

def test_generate_key():
    """测试缓存键生成"""
    key = CacheManager.generate_key("test", 123, "abc")
    assert key == "test:123:abc"
    
    key = CacheManager.generate_key("prefix", "key")
    assert key == "prefix:key"

@pytest.mark.asyncio
async def test_cache_operations():
    """测试基本缓存操作"""
    # 测试字符串缓存
    key = CacheManager.generate_key("test", "string")
    assert CacheManager.set_cache(key, "value")
    assert CacheManager.get_cache(key) == "value"
    
    # 测试JSON缓存
    data = {"name": "test", "value": 123}
    key = CacheManager.generate_key("test", "json")
    assert CacheManager.set_cache(key, data)
    assert CacheManager.get_cache(key, json_decode=True) == data
    
    # 测试过期时间
    key = CacheManager.generate_key("test", "expire")
    CacheManager.set_cache(key, "temp", expire=1)
    assert CacheManager.get_cache(key) == "temp"
    time.sleep(2)
    assert CacheManager.get_cache(key) is None
    
    # 测试删除缓存
    key = CacheManager.generate_key("test", "delete")
    CacheManager.set_cache(key, "delete_me")
    assert CacheManager.delete_cache(key)
    assert CacheManager.get_cache(key) is None
    
    # 测试清除前缀
    prefix = "test_prefix"
    key1 = CacheManager.generate_key(prefix, "1")
    key2 = CacheManager.generate_key(prefix, "2")
    CacheManager.set_cache(key1, "value1")
    CacheManager.set_cache(key2, "value2")
    assert CacheManager.clear_prefix(prefix)
    assert CacheManager.get_cache(key1) is None
    assert CacheManager.get_cache(key2) is None

@pytest.mark.asyncio
async def test_incr_with_expire():
    """测试递增并设置过期时间"""
    key = CacheManager.generate_key("test", "incr")
    
    
    # 测试递增
    value = CacheManager.incr_with_expire(key, 60)
    assert value == 1
    
    # 测试再次递增
    value = CacheManager.incr_with_expire(key, 60)
    assert value == 2
    
    # 测试过期
    key = CacheManager.generate_key("test", "incr_expire")
    CacheManager.incr_with_expire(key, 1)
    time.sleep(2)
    assert CacheManager.get_cache(key) is None
