"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from backend.config import get_settings

settings = get_settings()

# SQLAlchemy Engine 配置
if "sqlite" in settings.database_url:
    # SQLite 使用特殊配置
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug,  # 调试模式下打印SQL
    )
else:
    # PostgreSQL/MySQL 使用连接池
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
    )

# SessionLocal 工厂类
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# 声明基类（所有ORM模型都应继承这个）
Base = declarative_base()


def get_db():
    """
    FastAPI 依赖注入：获取数据库会话
    在路由中使用：
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
