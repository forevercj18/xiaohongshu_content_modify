#!/usr/bin/env python3
"""
添加测试违禁词数据
"""
import sys
import os
sys.path.append('backend')

import sqlite3
from datetime import datetime

# 连接数据库
db_path = 'backend/data/content_optimizer.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建违禁词表（如果不存在）
cursor.execute('''
CREATE TABLE IF NOT EXISTS prohibited_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    risk_level INTEGER NOT NULL,
    status INTEGER DEFAULT 1,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 测试违禁词数据
test_prohibited_words = [
    {"word": "第一", "category": "marketing", "risk_level": 2},
    {"word": "最好", "category": "marketing", "risk_level": 3},
    {"word": "最有效", "category": "marketing", "risk_level": 3},
    {"word": "包治百病", "category": "medical", "risk_level": 3},
    {"word": "减肥药", "category": "medical", "risk_level": 3},
    {"word": "微商", "category": "commercial", "risk_level": 2},
    {"word": "广告", "category": "commercial", "risk_level": 2},
    {"word": "推广", "category": "commercial", "risk_level": 2},
    {"word": "绝对", "category": "exaggeration", "risk_level": 2},
    {"word": "100%", "category": "exaggeration", "risk_level": 2},
]

# 插入测试数据
for word_data in test_prohibited_words:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO prohibited_words (word, category, risk_level, status, created_by)
            VALUES (?, ?, ?, 1, 'system')
        """, (word_data["word"], word_data["category"], word_data["risk_level"]))
    except Exception as e:
        print(f"插入 {word_data['word']} 失败: {e}")

conn.commit()
conn.close()

print("✅ 测试违禁词数据添加完成！")
print("📊 添加的违禁词：")
for word in test_prohibited_words:
    print(f"  - {word['word']} (风险等级: {word['risk_level']})")