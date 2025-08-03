#!/usr/bin/env python3
"""
测试小红书表情API功能
"""
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8000"

def test_emoji_list():
    """测试获取表情列表"""
    print("🧪 测试表情列表API")
    url = f"{BASE_URL}/api/emoji/list"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取 {data['total']} 个表情")
            
            # 显示前5个表情
            for emoji in data['emojis'][:5]:
                print(f"   - {emoji['code']} ({emoji['name']}) - {emoji['emoji_type']}系列")
                
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_emoji_categories():
    """测试获取表情分类"""
    print("\n🧪 测试表情分类API")
    url = f"{BASE_URL}/api/emoji/categories"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取 {len(data['categories'])} 个分类")
            
            for category in data['categories']:
                print(f"   - {category['display_name']} ({category['emoji_count']} 个表情)")
                
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_emoji_search():
    """测试表情搜索"""
    print("\n🧪 测试表情搜索API")
    
    # 测试不同的搜索关键词
    keywords = ["开心", "R", "情绪"]
    
    for keyword in keywords:
        url = f"{BASE_URL}/api/emoji/search"
        params = {"q": keyword}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 搜索 '{keyword}': 找到 {data['total']} 个结果")
                
                # 显示搜索结果
                for emoji in data['emojis'][:3]:
                    print(f"     - {emoji['code']} ({emoji['name']})")
            else:
                print(f"❌ 搜索失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 搜索失败: {e}")

def test_emoji_usage_log():
    """测试表情使用记录"""
    print("\n🧪 测试表情使用记录API")
    url = f"{BASE_URL}/api/emoji/usage"
    
    # 模拟使用记录
    data = {
        "emoji_id": 1,
        "usage_type": "manual",
        "user_session": "test_session_001",
        "position": 10,
        "context": "这是一个测试内容，用户手动插入了表情"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 使用记录保存成功: {result['emoji_code']}")
            return True
        else:
            print(f"❌ 使用记录保存失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_category_filter():
    """测试分类筛选"""
    print("\n🧪 测试分类筛选")
    
    # 测试按分类筛选
    categories = ["basic_emotions", "reactions", "actions"]
    
    for category in categories:
        url = f"{BASE_URL}/api/emoji/list"
        params = {"category": category, "limit": 5}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 分类 '{category}': {data['total']} 个表情")
                
                for emoji in data['emojis']:
                    print(f"     - {emoji['code']} ({emoji['name']})")
            else:
                print(f"❌ 筛选失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def test_emoji_type_filter():
    """测试表情类型筛选"""
    print("\n🧪 测试表情类型筛选")
    
    # 测试R系列和H系列
    for emoji_type in ["R", "H"]:
        url = f"{BASE_URL}/api/emoji/list"
        params = {"emoji_type": emoji_type}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {emoji_type}系列: {data['total']} 个表情")
                
                for emoji in data['emojis'][:3]:
                    print(f"     - {emoji['code']} ({emoji['name']})")
            else:
                print(f"❌ 筛选失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 小红书表情API功能测试")
    print("=" * 60)
    
    # 基础功能测试
    success_count = 0
    total_tests = 3
    
    if test_emoji_list():
        success_count += 1
    
    if test_emoji_categories():
        success_count += 1
    
    if test_emoji_usage_log():
        success_count += 1
    
    # 高级功能测试
    test_emoji_search()
    test_category_filter()
    test_emoji_type_filter()
    
    # 测试总结
    print("\n" + "=" * 60)
    print(f"🎯 测试完成！基础功能: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("✅ 所有基础功能测试通过！小红书表情系统运行正常")
    else:
        print("⚠️ 部分测试失败，请检查API服务状态")

if __name__ == "__main__":
    main()