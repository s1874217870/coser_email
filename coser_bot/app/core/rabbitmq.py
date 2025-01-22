"""
RabbitMQ连接模块
处理RabbitMQ连接和操作
"""
import aio_pika
from app.core.config import get_settings

settings = get_settings()

async def get_rabbitmq_connection():
    """获取RabbitMQ连接"""
    return await aio_pika.connect_robust(
        host="localhost",
        port=5672,
        login="guest",
        password="guest"
    )

async def get_channel():
    """获取RabbitMQ通道"""
    connection = await get_rabbitmq_connection()
    return await connection.channel()
