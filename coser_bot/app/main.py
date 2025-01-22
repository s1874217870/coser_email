"""
应用程序主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.models import user, admin
from app.middleware.performance import performance_middleware
from app.middleware.admin import admin_middleware
from app.routers import admin as admin_router
from app.core.redis import redis_client
from app.core.mongodb import get_mongodb
from app.core.rabbitmq import get_rabbitmq_connection
from app.services.telegram_bot import bot_service
import asyncio

app = FastAPI(
    title="Coser展馆社区机器人",
    description="Coser展馆社区机器人API文档",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_origin_regex="https?://.*"
)

# 添加中间件
app.middleware("http")(performance_middleware)
app.middleware("http")(admin_middleware)

# 注册路由
app.include_router(admin_router.router)

@app.on_event("startup")
async def startup_event():
    """应用程序启动事件"""
    # 创建数据库表
    try:
        async with engine.begin() as conn:
            await conn.run_sync(user.Base.metadata.create_all)
            await conn.run_sync(admin.Base.metadata.create_all)
        print("数据库表创建成功")
    except Exception as e:
        print(f"数据库表创建失败: {e}")
        
    # 测试Redis连接
    try:
        redis_client.ping()
        print("Redis连接成功")
    except Exception as e:
        print(f"Redis连接失败: {e}")
        
    # 测试MongoDB连接
    try:
        db = await get_mongodb()
        await db.command("ping")
        print("MongoDB连接成功")
    except Exception as e:
        print(f"MongoDB连接失败: {e}")
        
    # 测试RabbitMQ连接
    try:
        connection = await get_rabbitmq_connection()
        await connection.close()
        print("RabbitMQ连接成功")
    except Exception as e:
        print(f"RabbitMQ连接失败: {e}")
        
    # 暂时禁用Telegram Bot，用于测试管理员功能
    # asyncio.create_task(bot_service.run())

@app.get("/")
async def root():
    """根路由"""
    return {"message": "Coser展馆社区机器人API服务正在运行"}
