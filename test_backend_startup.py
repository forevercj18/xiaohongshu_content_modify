#!/usr/bin/env python3
"""
测试后端启动
"""
import sys
import os
sys.path.append('backend')

def test_imports():
    """测试关键模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        from app.main import app
        print("✅ 主应用导入成功")
    except Exception as e:
        print(f"❌ 主应用导入失败: {e}")
        return False
    
    try:
        from app.api.emoji import router
        print("✅ 表情API导入成功")
    except Exception as e:
        print(f"❌ 表情API导入失败: {e}")
        return False
    
    try:
        from app.models.database import XiaohongshuEmoji
        print("✅ 表情模型导入成功")
    except Exception as e:
        print(f"❌ 表情模型导入失败: {e}")
        return False
    
    try:
        from app.database.connection import get_database
        print("✅ 数据库连接导入成功")
    except Exception as e:
        print(f"❌ 数据库连接导入失败: {e}")
        return False
    
    return True

def test_database_connection():
    """测试数据库连接"""
    print("\n🧪 测试数据库连接...")
    
    try:
        from app.database.connection import SessionLocal, engine
        from app.models.database import XiaohongshuEmoji
        
        # 测试会话创建
        db = SessionLocal()
        
        # 测试查询
        emoji_count = db.query(XiaohongshuEmoji).count()
        print(f"✅ 数据库连接成功，表情数量: {emoji_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 后端启动测试")
    print("=" * 50)
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 模块导入测试失败")
        return False
    
    # 测试数据库连接
    if not test_database_connection():
        print("\n❌ 数据库连接测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！后端可以正常启动")
    print("\n🚀 启动命令:")
    print("   cd backend")
    print("   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    return True

if __name__ == "__main__":
    main()