"""
FastAPI 主应用程序入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.api.routes import router

# 初始化设置
settings = get_settings()


# ============================================================================
# 应用生命周期管理（使用 lifespan 替代已弃用的 on_event）
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期上下文管理器"""
    # ===== 启动事件 =====
    print(f"[启动] {settings.app_name} v{settings.app_version}")
    print(f"[文档] http://{settings.server_host}:{settings.server_port}/docs")
    print(f"[调试模式] {settings.debug}")
    
    yield
    
    # ===== 关闭事件 =====
    print(f"[关闭] {settings.app_name}")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI驱动的劳动者维权诉状生成系统",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=settings.debug,
    lifespan=lifespan,
)

# ============================================================================
# CORS 中间件配置
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体的origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 注册路由
# ============================================================================
app.include_router(router)


# ============================================================================
# 根路由
# ============================================================================

@app.get("/")
async def root():
    """根路由 - 返回应用基本信息"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "api_prefix": "/api/v1"
    }


# ============================================================================
# 应用主入口（本地开发运行）
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
    )
