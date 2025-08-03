"""
小红书内容优化工具 - FastAPI主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.database.init_db import init_database
from app.api.auth import router as auth_router
from app.api.content import router as content_router
from app.api.admin import router as admin_router
from app.api.stats import router as stats_router
from app.api.emoji import router as emoji_router
from app.api.emoji_recommendation import router as emoji_recommendation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_database()
    yield
    # 关闭时清理资源


# 创建FastAPI应用
app = FastAPI(
    title="小红书内容优化工具",
    description="智能违禁词检测和内容优化API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(content_router, prefix="/api/content", tags=["内容处理"])
app.include_router(admin_router, prefix="/api/admin", tags=["管理员"])
app.include_router(stats_router, prefix="/api/stats", tags=["统计"])
app.include_router(emoji_router, tags=["表情管理"])
app.include_router(emoji_recommendation_router, tags=["智能表情推荐"])


@app.get("/")
async def root():
    """根路径"""
    return {"message": "小红书内容优化工具 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)