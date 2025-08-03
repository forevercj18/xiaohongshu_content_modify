"""
智能表情推荐API
根据内容分析推荐合适的小红书表情
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import re
import json
from collections import Counter

from app.database.connection import get_database as get_db
from app.models.database import XiaohongshuEmoji

router = APIRouter(prefix="/api/emoji", tags=["表情推荐"])


class EmojiRecommendationEngine:
    """表情推荐引擎"""
    
    def __init__(self):
        # 内容类型关键词映射
        self.content_type_keywords = {
            "美妆": ["化妆", "护肤", "美妆", "口红", "粉底", "眉毛", "眼影", "腮红", "素颜", "卸妆"],
            "美食": ["好吃", "美味", "餐厅", "美食", "做饭", "烹饪", "菜谱", "零食", "甜品", "饮品"],
            "穿搭": ["穿搭", "衣服", "搭配", "时尚", "裙子", "鞋子", "包包", "饰品", "风格", "款式"],
            "生活": ["日常", "生活", "家居", "收纳", "清洁", "整理", "装修", "植物", "宠物", "旅行"],
            "学习": ["学习", "读书", "考试", "课程", "笔记", "知识", "技能", "工作", "效率", "思考"],
            "健身": ["健身", "运动", "瑜伽", "减肥", "锻炼", "体重", "马甲线", "肌肉", "跑步", "游泳"],
            "情感": ["开心", "难过", "激动", "感动", "紧张", "焦虑", "温暖", "感谢", "爱情", "友情"]
        }
        
        # 情感词汇映射
        self.emotion_keywords = {
            "开心": ["开心", "快乐", "高兴", "兴奋", "愉快", "满足", "幸福", "欢喜"],
            "难过": ["难过", "伤心", "失落", "沮丧", "郁闷", "痛苦", "悲伤"],
            "惊讶": ["惊讶", "震惊", "意外", "不敢相信", "没想到", "太神奇"],
            "鄙视": ["鄙视", "看不起", "讨厌", "无语", "生气", "愤怒"],
            "尴尬": ["尴尬", "不好意思", "害羞", "社死", "丢脸"],
            "疑惑": ["疑惑", "不懂", "困惑", "奇怪", "为什么"],
            "赞美": ["太棒了", "厉害", "赞", "好评", "推荐", "优秀", "完美"]
        }
    
    def analyze_content_type(self, content: str) -> List[str]:
        """分析内容类型"""
        content_types = []
        for content_type, keywords in self.content_type_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    content_types.append(content_type)
                    break
        return content_types
    
    def analyze_emotions(self, content: str) -> List[str]:
        """分析内容情感"""
        emotions = []
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    emotions.append(emotion)
                    break
        return emotions
    
    def extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（可以使用jieba等更高级的工具）
        keywords = []
        
        # 提取形容词和名词性词汇
        common_keywords = [
            "好看", "漂亮", "美丽", "可爱", "温柔", "优雅", "时尚", "简约",
            "实用", "方便", "舒适", "温暖", "清新", "自然", "健康", "美味",
            "香甜", "清爽", "丰富", "有趣", "好玩", "刺激", "放松", "治愈"
        ]
        
        for keyword in common_keywords:
            if keyword in content:
                keywords.append(keyword)
        
        return keywords
    
    def recommend_emojis(self, content: str, emojis: List[XiaohongshuEmoji]) -> List[dict]:
        """根据内容推荐表情"""
        content_types = self.analyze_content_type(content)
        emotions = self.analyze_emotions(content)
        keywords = self.extract_keywords(content)
        
        recommendations = []
        
        # 基于内容类型推荐
        for content_type in content_types:
            type_emojis = [e for e in emojis if content_type in (e.description or "")]
            for emoji in type_emojis[:2]:  # 每个类型推荐2个
                recommendations.append({
                    "emoji": emoji,
                    "reason": f"适合{content_type}类内容",
                    "confidence": 0.8,
                    "category": "内容匹配"
                })
        
        # 基于情感推荐
        for emotion in emotions:
            emotion_emojis = [e for e in emojis if emotion in e.name or emotion in (e.keywords or "")]
            for emoji in emotion_emojis[:1]:  # 每个情感推荐1个
                recommendations.append({
                    "emoji": emoji,
                    "reason": f"表达{emotion}情感",
                    "confidence": 0.9,
                    "category": "情感匹配"
                })
        
        # 基于关键词推荐
        for keyword in keywords[:3]:  # 最多推荐3个关键词相关的
            keyword_emojis = [e for e in emojis if keyword in (e.keywords or "") or keyword in (e.description or "")]
            for emoji in keyword_emojis[:1]:
                recommendations.append({
                    "emoji": emoji,
                    "reason": f"与{keyword}相关",
                    "confidence": 0.7,
                    "category": "关键词匹配"
                })
        
        # 去重并按置信度排序
        seen_codes = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec["emoji"].code not in seen_codes:
                seen_codes.add(rec["emoji"].code)
                unique_recommendations.append(rec)
        
        unique_recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return unique_recommendations[:8]  # 最多返回8个推荐


@router.post("/recommend", summary="智能表情推荐")
async def recommend_emojis(
    content: str,
    limit: int = 8,
    db: Session = Depends(get_db)
):
    """
    根据内容智能推荐表情
    """
    if not content.strip():
        return {
            "recommendations": [],
            "message": "请输入内容以获取表情推荐"
        }
    
    # 获取所有活跃表情
    emojis = db.query(XiaohongshuEmoji).filter(
        XiaohongshuEmoji.status == 1
    ).order_by(
        XiaohongshuEmoji.priority.desc(),
        XiaohongshuEmoji.usage_count.desc()
    ).all()
    
    if not emojis:
        return {
            "recommendations": [],
            "message": "暂无可用表情"
        }
    
    # 初始化推荐引擎
    engine = EmojiRecommendationEngine()
    
    # 获取推荐结果
    recommendations = engine.recommend_emojis(content, emojis)
    
    # 格式化返回结果
    formatted_recommendations = []
    for rec in recommendations:
        emoji = rec["emoji"]
        formatted_recommendations.append({
            "code": emoji.code,
            "name": emoji.name,
            "emoji_type": emoji.emoji_type,
            "category": emoji.category,
            "description": emoji.description,
            "keywords": json.loads(emoji.keywords or "[]"),
            "reason": rec["reason"],
            "confidence": rec["confidence"],
            "match_category": rec["category"],
            "usage_count": emoji.usage_count,
            "priority": emoji.priority
        })
    
    return {
        "recommendations": formatted_recommendations[:limit],
        "content_analysis": {
            "content_types": engine.analyze_content_type(content),
            "emotions": engine.analyze_emotions(content),
            "keywords": engine.extract_keywords(content)
        },
        "total": len(formatted_recommendations)
    }


@router.post("/suggest", summary="内容优化表情建议")
async def suggest_emojis_for_optimization(
    original_content: str,
    optimized_content: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    为内容优化提供表情建议
    """
    content_to_analyze = optimized_content if optimized_content else original_content
    
    if not content_to_analyze.strip():
        return {
            "suggestions": [],
            "message": "请提供内容以获取表情建议"
        }
    
    # 获取推荐结果
    recommendations_response = await recommend_emojis(content_to_analyze, limit=5, db=db)
    recommendations = recommendations_response["recommendations"]
    
    # 转换为EmojiSuggestionCard组件需要的格式
    suggestions = []
    for rec in recommendations:
        suggestions.append({
            "描述": rec["name"],
            "建议": f"使用 {rec['code']} 表情",
            "场景": [rec["category"], rec["match_category"]],
            "推荐理由": rec["reason"],
            "置信度": rec["confidence"]
        })
    
    return {
        "suggestions": suggestions,
        "analysis": recommendations_response.get("content_analysis", {}),
        "message": f"为您推荐了 {len(suggestions)} 个表情" if suggestions else "暂无合适的表情推荐"
    }