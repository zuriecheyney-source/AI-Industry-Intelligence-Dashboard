from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.scheduler.tasks import start_scheduler, stop_scheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动AI行业情报系统...")
    
    # 启动定时任务调度器
    start_scheduler()
    logger.info(f"定时任务已配置: {settings.schedule_times_list}")
    
    yield
    
    # 关闭时清理
    stop_scheduler()
    logger.info("关闭AI行业情报系统...")


# 创建FastAPI应用
app = FastAPI(
    title="AI行业情报系统",
    description="自动化采集和推送行业情报的智能系统",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "message": "AI行业情报系统运行中",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "ai_provider": settings.ai_provider,
        "timezone": settings.timezone
    }


# 注册API路由
from app.api import routes
app.include_router(routes.router, prefix="/api", tags=["intelligence"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )