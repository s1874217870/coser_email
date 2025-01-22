"""
性能监控中间件
用于监控API响应时间和并发处理
"""
import time
from fastapi import Request
from app.core.redis import redis_client

async def performance_middleware(request: Request, call_next):
    """
    性能监控中间件
    监控API响应时间和请求数量
    """
    start_time = time.time()
    
    # 增加请求计数
    redis_client.incr("api:request_count")
    
    response = await call_next(request)
    
    # 计算响应时间
    process_time = (time.time() - start_time) * 1000
    redis_client.lpush("api:response_times", process_time)
    
    # 如果响应时间超过200ms，记录警告
    if process_time > 200:
        redis_client.incr("api:slow_requests")
    
    return response
