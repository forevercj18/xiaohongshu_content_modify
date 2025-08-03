#!/usr/bin/env python3
"""
添加测试数据脚本
"""
import sys
import os
sys.path.append('backend')

from datetime import datetime, timedelta
import sqlite3
import json

# 连接数据库
db_path = 'backend/data/content_optimizer.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建测试数据
test_data = [
    {
        'date': '2025-07-29',
        'records': [
            {
                'user_session': 'test_session_1',
                'original_content': '今天分享一个超级好用的减肥产品',
                'optimized_content': '今天分享一个超级好用的健康产品',
                'detected_issues': json.dumps([{"type": "prohibited_word", "word": "减肥", "position": 12}]),
                'applied_optimizations': json.dumps([{"type": "word_replacement", "original": "减肥", "replacement": "健康"}]),
                'content_score_before': 60,
                'content_score_after': 85,
                'processing_time': 0.003,
                'is_optimized': 1
            },
            {
                'user_session': 'test_session_2',
                'original_content': '这个广告真的很不错',
                'detected_issues': json.dumps([{"type": "prohibited_word", "word": "广告", "position": 2}]),
                'content_score_before': 50,
                'processing_time': 0.002,
                'is_optimized': 0
            }
        ]
    },
    {
        'date': '2025-07-30',
        'records': [
            {
                'user_session': 'test_session_3',
                'original_content': '微商代理招募中',
                'optimized_content': '代理招募中',
                'detected_issues': json.dumps([{"type": "prohibited_word", "word": "微商", "position": 0}]),
                'applied_optimizations': json.dumps([{"type": "word_removal", "original": "微商", "replacement": ""}]),
                'content_score_before': 40,
                'content_score_after': 70,
                'processing_time': 0.004,
                'is_optimized': 1
            }
        ]
    },
    {
        'date': '2025-08-01',
        'records': [
            {
                'user_session': 'test_session_4',
                'original_content': '推广这个新产品给大家',
                'optimized_content': '推guang这个新产品给大家',
                'detected_issues': json.dumps([{"type": "prohibited_word", "word": "推广", "position": 0}]),
                'applied_optimizations': json.dumps([{"type": "homophone_replacement", "original": "推广", "replacement": "推guang"}]),
                'content_score_before': 55,
                'content_score_after': 80,
                'processing_time': 0.005,
                'is_optimized': 1
            },
            {
                'user_session': 'test_session_5',
                'original_content': '这个内容没有问题',
                'detected_issues': json.dumps([]),
                'content_score_before': 95,
                'processing_time': 0.001,
                'is_optimized': 0
            }
        ]
    }
]

# 插入测试数据
for day_data in test_data:
    for record in day_data['records']:
        # 构造创建时间
        created_at = f"{day_data['date']} 14:30:00.000000"
        
        # 插入数据
        cursor.execute("""
            INSERT INTO user_content_history (
                user_session, original_content, optimized_content, 
                detected_issues, applied_optimizations,
                content_score_before, content_score_after,
                processing_time, is_optimized, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record['user_session'],
            record['original_content'],
            record.get('optimized_content'),
            record['detected_issues'],
            record.get('applied_optimizations'),
            record['content_score_before'],
            record.get('content_score_after'),
            record['processing_time'],
            record['is_optimized'],
            created_at
        ))

conn.commit()
conn.close()

print("✅ 测试数据添加完成！")
print("📊 数据分布：")
print("  - 2025-07-29: 2条记录 (1次检测, 1次优化)")
print("  - 2025-07-30: 1条记录 (1次检测, 1次优化)")
print("  - 2025-08-01: 2条记录 (2次检测, 1次优化)")
print("  - 2025-08-02: 11条记录 (11次检测, 6次优化)")