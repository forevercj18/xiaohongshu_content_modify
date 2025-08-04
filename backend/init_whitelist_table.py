#!/usr/bin/env python3
"""
初始化白名单模式表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine, SessionLocal
from app.models.database import Base, WhitelistPattern
from sqlalchemy import text

def create_whitelist_table():
    """创建白名单表"""
    try:
        # 创建表
        Base.metadata.create_all(bind=engine)
        print("白名单表创建成功")
        return True
    except Exception as e:
        print(f"创建白名单表失败: {e}")
        return False

def init_default_whitelist_patterns():
    """初始化默认白名单模式"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing_count = db.query(WhitelistPattern).count()
        if existing_count > 0:
            print(f"白名单模式已存在 {existing_count} 条记录")
            return True
        
        # 初始化默认白名单模式
        default_patterns = [
            # "第一"相关的安全表达
            {
                "prohibited_word": "第一",
                "pattern": r"第一次",
                "description": "时间表达：第一次",
                "category": "时间表达",
                "example": "这是我第一次来这里"
            },
            {
                "prohibited_word": "第一",
                "pattern": r"第一天",
                "description": "时间表达：第一天",
                "category": "时间表达", 
                "example": "第一天上班很紧张"
            },
            {
                "prohibited_word": "第一",
                "pattern": r"第一个月",
                "description": "时间表达：第一个月",
                "category": "时间表达",
                "example": "第一个月的工资"
            },
            {
                "prohibited_word": "第一",
                "pattern": r"第一步",
                "description": "流程表达：第一步",
                "category": "流程表达",
                "example": "第一步需要注册账号"
            },
            {
                "prohibited_word": "第一",
                "pattern": r"第一印象",
                "description": "感受表达：第一印象",
                "category": "感受表达",
                "example": "给人的第一印象很重要"
            },
            {
                "prohibited_word": "第一",
                "pattern": r"第一时间",
                "description": "时间表达：第一时间",
                "category": "时间表达",
                "example": "第一时间通知大家"
            },
            
            # "最"相关的安全表达
            {
                "prohibited_word": "最好",
                "pattern": r"最近",
                "description": "时间副词：最近",
                "category": "时间副词",
                "example": "最近天气很好"
            },
            {
                "prohibited_word": "最有效",
                "pattern": r"最新",
                "description": "时间描述：最新",
                "category": "时间描述",
                "example": "最新的消息"
            },
            {
                "prohibited_word": "最好",
                "pattern": r"最后",
                "description": "时间顺序：最后",
                "category": "时间顺序",
                "example": "最后一个问题"
            },
            {
                "prohibited_word": "最有效",
                "pattern": r"最基本",
                "description": "程度描述：最基本",
                "category": "程度描述",
                "example": "最基本的要求"
            },
            {
                "prohibited_word": "最好",
                "pattern": r"最常见",
                "description": "客观描述：最常见",
                "category": "客观描述",
                "example": "最常见的问题"
            },
            {
                "prohibited_word": "最有效",
                "pattern": r"最重要",
                "description": "程度描述：最重要",
                "category": "程度描述",
                "example": "最重要的一点"
            },
            
            # "减肥"相关的安全表达
            {
                "prohibited_word": "减肥药",
                "pattern": r"减肥餐",
                "description": "饮食表达：减肥餐",
                "category": "饮食表达",
                "example": "今天的减肥餐很清淡"
            },
            {
                "prohibited_word": "减肥药",
                "pattern": r"减肥运动",
                "description": "运动表达：减肥运动",
                "category": "运动表达",
                "example": "做减肥运动很累"
            },
            {
                "prohibited_word": "减肥药",
                "pattern": r"健康减肥",
                "description": "健康表达：健康减肥",
                "category": "健康表达",
                "example": "提倡健康减肥方式"
            },
            
            # "微商"相关的安全表达
            {
                "prohibited_word": "微商",
                "pattern": r"不是微商",
                "description": "否定表达：不是微商",
                "category": "否定表达",
                "example": "我不是微商，只是分享"
            },
            {
                "prohibited_word": "微商",
                "pattern": r"拒绝微商",
                "description": "否定表达：拒绝微商",
                "category": "否定表达",
                "example": "拒绝微商骚扰"
            },
        ]
        
        # 批量插入
        for pattern_data in default_patterns:
            pattern = WhitelistPattern(
                prohibited_word=pattern_data["prohibited_word"],
                pattern=pattern_data["pattern"],
                description=pattern_data["description"],
                category=pattern_data["category"],
                example=pattern_data["example"],
                is_active=1,
                priority=1,
                created_by="system"
            )
            db.add(pattern)
        
        db.commit()
        print(f"成功初始化 {len(default_patterns)} 个默认白名单模式")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"初始化白名单模式失败: {e}")
        return False
    finally:
        db.close()

def main():
    """主函数"""
    print("开始初始化白名单表...")
    
    # 创建表
    if not create_whitelist_table():
        return
    
    # 初始化数据
    if not init_default_whitelist_patterns():
        return
    
    print("白名单表初始化完成！")

if __name__ == "__main__":
    main()