"""
主应用模块
"""
from fastapi import FastAPI
from config import settings
from bot import CoserBot
import uvicorn

app = FastAPI(
    title="Coser展馆社区机器人",
    description="Coser展馆社区机器人API服务",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    """应用启动时的处理"""
    # 启动Telegram机器人
    bot = CoserBot()
    bot.run()

@app.get("/")
async def root():
    """根路由"""
    return {"message": "Coser展馆社区机器人服务正在运行"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.DEBUG else False
    )
