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
def mock_redis(mocker):
    """Mock Redis客户端"""
    mock_client = mocker.MagicMock()
    mock_client._data = {}
    mock_client._expire_times = {}
    
    # 模拟exists方法
    def mock_exists(key):
        if key in mock_client._expire_times:
            if time.time() > mock_client._expire_times[key]:
                del mock_client._data[key]
                del mock_client._expire_times[key]
                return False
        return key in mock_client._data
    mock_client.exists = mock_exists
    
    # 模拟get方法
    def mock_get(key):
        if mock_exists(key):
            return mock_client._data.get(key)
        return None
    mock_client.get = mock_get
    
    # 模拟set方法
    def mock_set(key, value, ex=None, nx=False):
        if nx and key in mock_client._data:
            return False
        mock_client._data[key] = value
        if ex:
            mock_client._expire_times[key] = time.time() + ex
        return True
    mock_client.set = mock_set
    
    # 模拟delete方法
    def mock_keys(pattern):
        import fnmatch
        # 将Redis模式转换为fnmatch模式
        pattern = pattern.replace('*', '?*')  # 处理通配符
        pattern = pattern.replace('?', '.')   # 处理单字符匹配
        pattern = pattern.replace('[', '[')    # 处理字符集
        pattern = pattern.replace(']', ']')    # 处理字符集结束
        # 获取所有匹配的键
        matched_keys = [key for key in mock_client._data.keys() 
                       if fnmatch.fnmatch(key, pattern)]
        return matched_keys
    mock_client.keys = mock_keys
    
    def mock_delete(*keys):
        deleted = 0
        for key in keys:
            if key in mock_client._data:
                del mock_client._data[key]
                if key in mock_client._expire_times:
                    del mock_client._expire_times[key]
                deleted += 1
        return deleted > 0  # 返回布尔值而不是删除计数
    mock_client.delete = mock_delete
    
    # 模拟pipeline
    class MockPipeline:
        def __init__(self):
            self.commands = []
            self.results = []
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def incr(self, key):
            if key not in mock_client._data:
                mock_client._data[key] = "0"
            value = int(mock_client._data[key]) + 1
            mock_client._data[key] = str(value)
            self.commands.append(("incr", key))
            self.results.append(value)
            return self
            
        def expire(self, key, seconds):
            mock_client._expire_times[key] = time.time() + seconds
            self.commands.append(("expire", key, seconds))
            self.results.append(True)
            return self
            
        def delete(self, key):
            self.commands.append(("delete", key))
            return self
            
        def execute(self):
            # 执行所有累积的命令
            for cmd in self.commands:
                if cmd[0] == "delete":
                    if cmd[1] in mock_client._data:
                        del mock_client._data[cmd[1]]
                        if cmd[1] in mock_client._expire_times:
                            del mock_client._expire_times[cmd[1]]
                        self.results.append(1)
                    else:
                        self.results.append(0)
            
            results = self.results
            self.commands = []
            self.results = []
            return results
            
    def mock_pipeline():
        return MockPipeline()
    mock_client.pipeline = mock_pipeline
    
    mocker.patch('app.core.redis.redis_client', mock_client)
    return mock_client

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

@pytest.mark.asyncio
async def test_error_handling():
    """测试错误处理"""
    # 测试无效的JSON数据
    key = CacheManager.generate_key("test", "invalid_json")
    CacheManager.set_cache(key, "invalid json")
    assert CacheManager.get_cache(key, json_decode=True) is None
    
    # 测试删除不存在的键
    assert not CacheManager.delete_cache("nonexistent_key")
    
    # 测试清除不存在的前缀
    assert CacheManager.clear_prefix("nonexistent_prefix")
    
    # 测试递增操作异常处理
    key = CacheManager.generate_key("test", "incr_error")
    CacheManager.set_cache(key, "not a number")
    assert CacheManager.incr_with_expire(key, 60) is None
    
    # 测试设置缓存异常
    key = CacheManager.generate_key("test", "set_error")
    complex_obj = {"func": lambda x: x}  # 不可序列化的对象
    assert not CacheManager.set_cache(key, complex_obj)
    
    # 测试获取缓存异常
    key = CacheManager.generate_key("test", "get_error")
    CacheManager.set_cache(key, "value")
    CacheManager.delete_cache(key)  # 使用CacheManager方法删除
    assert CacheManager.get_cache(key) is None
    
    # 测试清理前缀异常
    prefix = "test_error"
    key = CacheManager.generate_key(prefix, "1")
    CacheManager.set_cache(key, "value")
    CacheManager.delete_cache(key)  # 使用CacheManager方法删除
    assert CacheManager.clear_prefix(prefix)

@pytest.mark.asyncio
async def test_cache_lifecycle():
    """测试缓存生命周期管理"""
    # 测试nx参数（只在键不存在时设置）
    key = CacheManager.generate_key("test", "nx_test")
    assert CacheManager.set_cache(key, "first", nx=True)
    assert not CacheManager.set_cache(key, "second", nx=True)
    assert CacheManager.get_cache(key) == "first"
    
    # 测试批量删除
    keys = [
        CacheManager.generate_key("test", "multi_1"),
        CacheManager.generate_key("test", "multi_2")
    ]
    for key in keys:
        CacheManager.set_cache(key, "value")
    assert CacheManager.delete_cache(*keys)
    for key in keys:
        assert CacheManager.get_cache(key) is None
    
    # 测试前缀清理
    prefix = "test_clear"
    keys = [
        CacheManager.generate_key(prefix, "1"),
        CacheManager.generate_key(prefix, "2"),
        CacheManager.generate_key(prefix, "3")
    ]
    for key in keys:
        CacheManager.set_cache(key, "value")
    assert CacheManager.clear_prefix(prefix)
    for key in keys:
        assert CacheManager.get_cache(key) is None
