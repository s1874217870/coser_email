"""
Celery配置模块
处理异步任务队列配置
"""
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

# 创建Celery实例
celery_app = Celery(
    'coser_bot',
    broker=f'amqp://guest:guest@localhost:5672//',
    backend='redis://localhost:6379/1'
)

# Celery配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=200,
    broker_connection_retry_on_startup=True,
    broker_pool_limit=10,
)

# 导入任务模块
celery_app.autodiscover_tasks(['app.tasks'], force=True)

# 显式导入任务模块以确保注册
import app.tasks.email_tasks
