#!/usr/bin/env python3
"""
测试 API 中的智能违禁词检测
"""
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8000"

# 测试用例
test_cases = [
    {
        "content": "这是我第一次来这里，感觉很不错",
        "expected": "正常使用'第一次' - 应该不被标记为违禁"
    },
    {
        "content": "我们是第一品牌，第一选择，绝对是最好的",
        "expected": "营销推广使用'第一'、'绝对'、'最好' - 应该被标记"
    },
    {
        "content": "今天第一天上班，感觉最近工作压力很大",
        "expected": "正常使用'第一天'、'最近' - 应该不被标记"
    },
    {
        "content": "这个减肥药效果绝对好，包治百病",
        "expected": "医疗承诺 - 应该被标记"
    }
]

def test_content_analysis(content: str) -> dict:
    """测试内容分析 API"""
    url = f"{BASE_URL}/api/content/analyze"
    payload = {
        "content": content,
        "user_session": "test_session"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API 错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

print("🧪 API 智能违禁词检测测试")
print("=" * 60)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n【测试 {i}】")
    print(f"📝 内容: {test_case['content']}")
    print(f"🎯 预期: {test_case['expected']}")
    
    result = test_content_analysis(test_case['content'])
    
    if result:
        detected_issues = result.get('detected_issues', [])
        content_score = result.get('content_score', 0)
        
        print(f"📊 内容评分: {content_score}")
        
        if detected_issues:
            print(f"⚠️  检测到 {len(detected_issues)} 个问题:")
            for issue in detected_issues:
                print(f"   - 违禁词: '{issue.get('word', 'N/A')}'")
                print(f"     风险等级: {issue.get('risk_level', 'N/A')}")
                print(f"     置信度: {issue.get('confidence', 'N/A')}")
                print(f"     分析: {issue.get('analysis', 'N/A')}")
        else:
            print("✅ 未检测到违禁词问题")
    else:
        print("❌ API 测试失败")

print("\n" + "=" * 60)
print("🎯 API 测试完成！")