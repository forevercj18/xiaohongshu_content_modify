#!/usr/bin/env python3
"""
测试智能违禁词检测器
"""
import sys
import os
sys.path.append('backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.algorithms.smart_prohibited_detector import SmartProhibitedDetector

# 数据库连接
engine = create_engine(f'sqlite:///backend/data/content_optimizer.db')
Session = sessionmaker(bind=engine)
db = Session()

# 创建智能检测器
detector = SmartProhibitedDetector(db)

# 测试用例
test_cases = [
    {
        "content": "这是我第一次来这里，感觉很不错",
        "description": "正常使用'第一次' - 应该不被标记"
    },
    {
        "content": "我们是第一品牌，第一选择",
        "description": "营销推广使用'第一' - 应该被标记"
    },
    {
        "content": "这是最近很流行的产品",
        "description": "正常使用'最' - 应该不被标记"
    },
    {
        "content": "这是最好的产品，效果最有效",
        "description": "夸大宣传使用'最' - 应该被标记"
    },
    {
        "content": "今天第一天上班，有点紧张",
        "description": "正常使用'第一天' - 应该不被标记"
    },
    {
        "content": "这个减肥方法很健康，我正在减肥中",
        "description": "正常讨论减肥 - 应该不被标记"
    },
    {
        "content": "这个减肥药效果绝对好，包治百病",
        "description": "医疗承诺 - 应该被标记"
    },
    {
        "content": "不是微商，只是朋友推荐的好产品",
        "description": "否定用法 - 应该不被标记"
    }
]

print("🔍 智能违禁词检测器测试")
print("=" * 50)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n【测试 {i}】: {test_case['description']}")
    print(f"📝 内容: {test_case['content']}")
    
    # 执行检测
    issues = detector.detect_prohibited_words(test_case['content'])
    
    if issues:
        print(f"⚠️  检测到 {len(issues)} 个问题:")
        for issue in issues:
            print(f"   - 违禁词: '{issue['word']}'")
            print(f"     风险等级: {issue['risk_level']}")
            print(f"     置信度: {issue['confidence']:.2f}")
            print(f"     分析: {issue['analysis']}")
            if issue['suggestions']:
                print(f"     建议替换: {', '.join(issue['suggestions'])}")
    else:
        print("✅ 未检测到违禁词问题")

print("\n" + "=" * 50)
print("🎯 测试完成！")

# 关闭数据库连接
db.close()