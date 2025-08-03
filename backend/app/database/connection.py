"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "content_optimizer.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 生产环境设为False
    connect_args={"check_same_thread": False}  # SQLite特有配置
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database_directory():
    """创建数据库目录"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)