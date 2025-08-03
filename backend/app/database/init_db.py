"""
数据库初始化
"""
import os
import json
from sqlalchemy import text
from passlib.context import CryptContext

from app.database.connection import engine, create_database_directory, SessionLocal
from app.models.database import Base, AdminUser, ProhibitedWord, OriginalWord, HomophoneReplacement

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_database():
    """初始化数据库"""
    try:
        # 创建数据库目录
        create_database_directory()
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        # 初始化数据
        await init_default_data()
        
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")


async def init_default_data():
    """初始化默认数据"""
    db = SessionLocal()
    try:
        # 检查是否已有管理员用户
        admin_count = db.query(AdminUser).count()
        if admin_count == 0:
            # 创建默认管理员
            default_admin = AdminUser(
                username="admin",
                password_hash=pwd_context.hash("admin123"),
                email="admin@example.com",
                role="super_admin",
                permissions=json.dumps({
                    "prohibited_words": {"create": True, "read": True, "update": True, "delete": True},
                    "homophone_words": {"create": True, "read": True, "update": True, "delete": True},
                    "user_management": {"create": True, "read": True, "update": True, "delete": True},
                    "system_settings": {"read": True, "update": True}
                })
            )
            db.add(default_admin)
            print("✅ 创建默认管理员账户: admin / admin123")
        
        # 初始化一些基础违禁词
        prohibited_count = db.query(ProhibitedWord).count()
        if prohibited_count == 0:
            basic_prohibited_words = [
                {"word": "减肥药", "category": "medical", "risk_level": 3},
                {"word": "包治百病", "category": "commercial", "risk_level": 3},
                {"word": "广告", "category": "commercial", "risk_level": 2},
                {"word": "推广", "category": "commercial", "risk_level": 2},
                {"word": "微商", "category": "commercial", "risk_level": 2},
            ]
            
            for word_data in basic_prohibited_words:
                prohibited_word = ProhibitedWord(
                    word=word_data["word"],
                    category=word_data["category"],
                    risk_level=word_data["risk_level"],
                    status=1,
                    created_by="system"
                )
                db.add(prohibited_word)
            
            print("✅ 初始化基础违禁词库")
        
        # 初始化一些基础谐音词
        original_count = db.query(OriginalWord).count()
        if original_count == 0:
            # 创建原词
            original_words = [
                {"word": "广告", "category": "commercial"},
                {"word": "推广", "category": "commercial"},
                {"word": "减肥", "category": "medical"},
            ]
            
            for word_data in original_words:
                original_word = OriginalWord(
                    word=word_data["word"],
                    category=word_data["category"],
                    status=1,
                    created_by="system"
                )
                db.add(original_word)
            
            db.commit()  # 提交以获取ID
            
            # 创建谐音词替换
            replacements_data = [
                # 广告的谐音词
                {"original": "广告", "replacement": "广*告", "type": "符号分隔", "priority": 1},
                {"original": "广告", "replacement": "guang告", "type": "英文混用", "priority": 0},
                {"original": "广告", "replacement": "广膏", "type": "形近字", "priority": 0},
                
                # 推广的谐音词
                {"original": "推广", "replacement": "推guang", "type": "英文混用", "priority": 1},
                {"original": "推广", "replacement": "推*广", "type": "符号分隔", "priority": 0},
                
                # 减肥的谐音词
                {"original": "减肥", "replacement": "减费", "type": "同音字", "priority": 1},
                {"original": "减肥", "replacement": "jian肥", "type": "英文混用", "priority": 0},
            ]
            
            for repl_data in replacements_data:
                original_word = db.query(OriginalWord).filter(OriginalWord.word == repl_data["original"]).first()
                if original_word:
                    replacement = HomophoneReplacement(
                        original_word_id=original_word.id,
                        replacement_word=repl_data["replacement"],
                        replacement_type=repl_data["type"],
                        priority=repl_data["priority"],
                        confidence_score=0.8,
                        status=1,
                        created_by="system"
                    )
                    db.add(replacement)
            
            print("✅ 初始化基础谐音词库")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化默认数据失败: {e}")
    finally:
        db.close()


def reset_database():
    """重置数据库（开发用）"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("🔄 数据库已重置")