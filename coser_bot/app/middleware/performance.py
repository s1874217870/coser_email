"""
性能监控中间件
处理性能指标收集和监控
"""
from fastapi import Request
from prometheus_client import Counter, Histogram
import time

# 请求计数器
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests count',
    ['method', 'endpoint', 'status']
)

# 响应时间直方图
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

async def performance_middleware(request: Request, call_next):
    """性能监控中间件"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # 记录请求数
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    # 记录响应时间
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response
