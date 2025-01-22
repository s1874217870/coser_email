"""
主应用模块
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.services.telegram_bot import bot_service
from app.middleware.error_handler import error_handler
from app.middleware.signature import verify_signature
from app.middleware.performance import performance_monitor
import uvicorn

settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title="Coser展馆社区机器人",
    description="Coser展馆社区机器人API服务",
    version="1.0.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加中间件
app.middleware("http")(performance_monitor)
app.middleware("http")(verify_signature)

# 注册错误处理器
app.exception_handler(Exception)(error_handler)

@app.on_event("startup")
async def startup_event():
    """应用启动时的处理"""
    # 启动Telegram机器人
    await bot_service.run()

@app.get("/")
async def root():
    """根路由"""
    return {"message": "Coser展馆社区机器人服务正在运行"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )
