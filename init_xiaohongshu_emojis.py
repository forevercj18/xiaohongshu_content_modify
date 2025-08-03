#!/usr/bin/env python3
"""
初始化小红书表情数据
基于从CSDN博客发现的真实表情代码
"""
import sys
import os
sys.path.append('backend')

import sqlite3
import json
from datetime import datetime

# 连接数据库
db_path = 'backend/data/content_optimizer.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建小红书表情表
cursor.execute('''
CREATE TABLE IF NOT EXISTS xiaohongshu_emojis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    emoji_type TEXT NOT NULL,
    image_url TEXT,
    preview_image TEXT,
    category TEXT NOT NULL,
    subcategory TEXT,
    description TEXT,
    keywords TEXT,
    usage_count INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 1,
    is_verified INTEGER DEFAULT 0,
    status INTEGER DEFAULT 1,
    created_by TEXT,
    updated_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 创建表情分类表
cursor.execute('''
CREATE TABLE IF NOT EXISTS emoji_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    sort_order INTEGER DEFAULT 0,
    emoji_count INTEGER DEFAULT 0,
    status INTEGER DEFAULT 1,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 创建表情使用日志表
cursor.execute('''
CREATE TABLE IF NOT EXISTS emoji_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emoji_id INTEGER NOT NULL,
    user_session TEXT,
    content_id INTEGER,
    usage_type TEXT NOT NULL,
    position INTEGER,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emoji_id) REFERENCES xiaohongshu_emojis (id),
    FOREIGN KEY (content_id) REFERENCES user_content_history (id)
)
''')

# 表情分类数据
emoji_categories = [
    {
        "name": "basic_emotions",
        "display_name": "基础情绪",
        "description": "开心、难过、生气等基础情感表达",
        "icon": "😊",
        "sort_order": 1
    },
    {
        "name": "reactions",
        "display_name": "反应表情",
        "description": "鄙视、惊讶、无语等反应表情",
        "icon": "😲",
        "sort_order": 2
    },
    {
        "name": "actions",
        "display_name": "动作表情",
        "description": "吃瓜、观察、扯脸等动作表情",
        "icon": "👀",
        "sort_order": 3
    },
    {
        "name": "social",
        "display_name": "社交表情",
        "description": "互动、社交场景专用表情",
        "icon": "🤝",
        "sort_order": 4
    }
]

# 基于发现的真实小红书表情代码
xiaohongshu_emojis = [
    # R系列表情（基于CSDN博客发现的真实数据）
    {
        "code": "[开心R]",
        "name": "开心",
        "emoji_type": "R",
        "category": "basic_emotions",
        "subcategory": "正面情绪",
        "description": "表达开心、快乐、愉悦的心情",
        "keywords": json.dumps(["开心", "快乐", "高兴", "愉悦", "心情好"], ensure_ascii=False),
        "priority": 5
    },
    {
        "code": "[鄙视R]",
        "name": "鄙视",
        "emoji_type": "R",
        "category": "reactions",
        "subcategory": "负面反应",
        "description": "表达鄙视、不屑、看不起的态度",
        "keywords": json.dumps(["鄙视", "不屑", "看不起", "嫌弃"], ensure_ascii=False),
        "priority": 3
    },
    {
        "code": "[吃瓜R]",
        "name": "吃瓜",
        "emoji_type": "R",
        "category": "actions",
        "subcategory": "观看动作",
        "description": "表达吃瓜看戏、围观的态度",
        "keywords": json.dumps(["吃瓜", "围观", "看戏", "八卦"], ensure_ascii=False),
        "priority": 4
    },
    {
        "code": "[暗中观察R]",
        "name": "暗中观察",
        "emoji_type": "R",
        "category": "actions",
        "subcategory": "观看动作",
        "description": "表达暗中观察、偷看的状态",
        "keywords": json.dumps(["观察", "偷看", "暗中", "注视"], ensure_ascii=False),
        "priority": 4
    },
    {
        "code": "[吧唧R]",
        "name": "吧唧",
        "emoji_type": "R",
        "category": "actions",
        "subcategory": "声音动作",
        "description": "表达亲吻、吧唧声音",
        "keywords": json.dumps(["亲吻", "吧唧", "声音", "可爱"], ensure_ascii=False),
        "priority": 3
    },
    {
        "code": "[生气R]",
        "name": "生气",
        "emoji_type": "R",
        "category": "basic_emotions",
        "subcategory": "负面情绪",
        "description": "表达生气、愤怒的情绪",
        "keywords": json.dumps(["生气", "愤怒", "不爽", "恼火"], ensure_ascii=False),
        "priority": 4
    },
    {
        "code": "[难过R]",
        "name": "难过",
        "emoji_type": "R",
        "category": "basic_emotions",
        "subcategory": "负面情绪",
        "description": "表达难过、伤心的情绪",
        "keywords": json.dumps(["难过", "伤心", "悲伤", "沮丧"], ensure_ascii=False),
        "priority": 4
    },
    {
        "code": "[无语R]",
        "name": "无语",
        "emoji_type": "R",
        "category": "reactions",
        "subcategory": "中性反应",
        "description": "表达无语、无奈的状态",
        "keywords": json.dumps(["无语", "无奈", "无话可说", "speechless"], ensure_ascii=False),
        "priority": 4
    },
    {
        "code": "[惊讶R]",
        "name": "惊讶",
        "emoji_type": "R",
        "category": "reactions",
        "subcategory": "惊讶反应",
        "description": "表达惊讶、意外的反应",
        "keywords": json.dumps(["惊讶", "意外", "震惊", "吃惊"], ensure_ascii=False),
        "priority": 4
    },
    {
        "code": "[得意R]",
        "name": "得意",
        "emoji_type": "R",
        "category": "basic_emotions",
        "subcategory": "正面情绪",
        "description": "表达得意、自豪的情绪",
        "keywords": json.dumps(["得意", "自豪", "骄傲", "满意"], ensure_ascii=False),
        "priority": 3
    },
    
    # H系列表情
    {
        "code": "[扯脸H]",
        "name": "扯脸",
        "emoji_type": "H",
        "category": "actions",
        "subcategory": "夸张动作",
        "description": "表达扯脸、夸张的动作",
        "keywords": json.dumps(["扯脸", "夸张", "搞怪", "好笑"], ensure_ascii=False),
        "priority": 3
    },
    {
        "code": "[惊吓H]",
        "name": "惊吓",
        "emoji_type": "H",
        "category": "reactions",
        "subcategory": "惊讶反应",
        "description": "表达被惊吓、害怕的反应",
        "keywords": json.dumps(["惊吓", "害怕", "恐惧", "吓到"], ensure_ascii=False),
        "priority": 3
    },
    {
        "code": "[哭泣H]",
        "name": "哭泣",
        "emoji_type": "H",
        "category": "basic_emotions",
        "subcategory": "负面情绪",
        "description": "表达哭泣、非常伤心的情绪",
        "keywords": json.dumps(["哭泣", "大哭", "伤心", "眼泪"], ensure_ascii=False),
        "priority": 3
    },
    {
        "code": "[大笑H]",
        "name": "大笑",
        "emoji_type": "H",
        "category": "basic_emotions",
        "subcategory": "正面情绪",
        "description": "表达大笑、非常开心的情绪",
        "keywords": json.dumps(["大笑", "爆笑", "哈哈", "好笑"], ensure_ascii=False),
        "priority": 4
    },
    {
        "code": "[抠鼻H]",
        "name": "抠鼻",
        "emoji_type": "H",
        "category": "actions",
        "subcategory": "日常动作",
        "description": "表达抠鼻、无聊的动作",
        "keywords": json.dumps(["抠鼻", "无聊", "习惯", "日常"], ensure_ascii=False),
        "priority": 2
    }
]

# 插入分类数据
for category in emoji_categories:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO emoji_categories 
            (name, display_name, description, icon, sort_order, created_by)
            VALUES (?, ?, ?, ?, ?, 'system')
        """, (
            category["name"], 
            category["display_name"], 
            category["description"],
            category["icon"],
            category["sort_order"]
        ))
    except Exception as e:
        print(f"插入分类 {category['name']} 失败: {e}")

# 插入表情数据
for emoji in xiaohongshu_emojis:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO xiaohongshu_emojis 
            (code, name, emoji_type, category, subcategory, description, keywords, priority, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'system')
        """, (
            emoji["code"],
            emoji["name"],
            emoji["emoji_type"],
            emoji["category"],
            emoji["subcategory"],
            emoji["description"],
            emoji["keywords"],
            emoji["priority"]
        ))
    except Exception as e:
        print(f"插入表情 {emoji['code']} 失败: {e}")

# 更新分类中的表情数量
cursor.execute("""
    UPDATE emoji_categories 
    SET emoji_count = (
        SELECT COUNT(*) 
        FROM xiaohongshu_emojis 
        WHERE category = emoji_categories.name 
        AND status = 1
    )
""")

conn.commit()
conn.close()

print("✅ 小红书表情数据初始化完成！")
print("\n📊 初始化统计：")
print(f"  - 表情分类: {len(emoji_categories)} 个")
print(f"  - 表情数量: {len(xiaohongshu_emojis)} 个")
print(f"  - R系列表情: {len([e for e in xiaohongshu_emojis if e['emoji_type'] == 'R'])} 个")
print(f"  - H系列表情: {len([e for e in xiaohongshu_emojis if e['emoji_type'] == 'H'])} 个")

print("\n🎯 表情代码示例：")
for emoji in xiaohongshu_emojis[:5]:
    print(f"  - {emoji['code']} ({emoji['name']})")
print("  - ...")