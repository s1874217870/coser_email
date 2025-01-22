"""
RabbitMQ连接模块
用于消息队列管理
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

async def publish_message(queue_name: str, message: str):
    """
    发布消息到指定队列
    
    参数:
        queue_name: 队列名称
        message: 消息内容
    """
    connection = await get_rabbitmq_connection()
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(queue_name, durable=True)
        
        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=queue_name
        )
