"""
Celery Worker启动脚本
"""
from app.core.celery import celery_app

if __name__ == '__main__':
    celery_app.worker_main(['worker', '--loglevel=info'])
