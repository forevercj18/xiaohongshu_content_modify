"""
表情符号智能插入器
"""
import json
import os
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from sqlalchemy.orm import Session


class EmojiInserter:
    """表情符号智能插入器"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.emoji_data = self._load_emoji_data()
        self.content_mapping = self._build_content_mapping()
    
    def _load_emoji_data(self) -> Dict[str, Any]:
        """从数据库加载表情符号数据"""
        if not self.db:
            return self._get_fallback_emoji_data()
        
        try:
            from app.models.database import XiaohongshuEmoji
            
            emojis = self.db.query(XiaohongshuEmoji).filter(
                XiaohongshuEmoji.status == 1
            ).all()
            
            # 构建表情数据结构
            emoji_data = {
                "分类": {},
                "智能推荐规则": {
                    "内容类型": {},
                    "情感基调": {}
                }
            }
            
            # 按分类组织表情
            for emoji in emojis:
                category = emoji.category
                if category not in emoji_data["分类"]:
                    emoji_data["分类"][category] = {}
                
                subcategory = emoji.subcategory or "默认"
                if subcategory not in emoji_data["分类"][category]:
                    emoji_data["分类"][category][subcategory] = []
                
                emoji_data["分类"][category][subcategory].append({
                    "emoji": emoji.code,
                    "name": emoji.name,
                    "keywords": json.loads(emoji.keywords) if emoji.keywords else []
                })
            
            return emoji_data
            
        except Exception as e:
            print(f"从数据库加载表情数据失败: {e}")
            return self._get_fallback_emoji_data()
    
    def _get_fallback_emoji_data(self) -> Dict[str, Any]:
        """获取后备表情数据（当数据库不可用时）"""
        return {
            "分类": {
                "basic_emotions": {
                    "正面情绪": [
                        {"emoji": "[开心R]", "name": "开心", "keywords": ["开心", "快乐"]},
                        {"emoji": "[得意R]", "name": "得意", "keywords": ["得意", "自豪"]}
                    ],
                    "负面情绪": [
                        {"emoji": "[难过R]", "name": "难过", "keywords": ["难过", "伤心"]},
                        {"emoji": "[生气R]", "name": "生气", "keywords": ["生气", "愤怒"]}
                    ]
                }
            },
            "智能推荐规则": {
                "内容类型": {
                    "美妆护肤": ["[开心R]", "[得意R]"],
                    "美食分享": ["[开心R]", "[吃瓜R]"],
                    "购物种草": ["[开心R]", "[得意R]"]
                },
                "情感基调": {
                    "开心快乐": ["[开心R]", "[得意R]"],
                    "惊喜兴奋": ["[惊讶R]", "[开心R]"]
                }
            }
        }
    
    def _build_content_mapping(self) -> Dict[str, List[str]]:
        """构建内容类型到表情的映射"""
        if not self.emoji_data:
            return {}
        
        # 基于数据库表情构建智能推荐映射
        content_mapping = {
            "美妆护肤": [],
            "美食分享": [],
            "购物种草": [],
            "穿搭时尚": [],
            "居家生活": [],
            "学习工作": []
        }
        
        # 从表情数据中提取适合的表情代码
        for category_name, category_data in self.emoji_data.get("分类", {}).items():
            for subcategory_name, emojis in category_data.items():
                for emoji in emojis:
                    emoji_code = emoji["emoji"]
                    keywords = emoji.get("keywords", [])
                    
                    # 根据关键词分配到不同内容类型
                    if any(k in keywords for k in ["开心", "快乐", "好"]):
                        for content_type in content_mapping.keys():
                            if len(content_mapping[content_type]) < 3:
                                content_mapping[content_type].append(emoji_code)
        
        # 确保每个类型至少有一个表情
        default_emoji = "[开心R]"
        for content_type in content_mapping:
            if not content_mapping[content_type]:
                content_mapping[content_type] = [default_emoji]
        
        return content_mapping
    
    def analyze_content_and_insert_emojis(self, content: str) -> Tuple[str, List[Dict]]:
        """分析内容并智能插入表情符号"""
        optimized_content = content
        applied_changes = []
        
        # 检测内容类型
        content_type = self._detect_content_type(content)
        
        # 检测情感基调
        emotion_tone = self._detect_emotion_tone(content)
        
        # 获取推荐表情
        recommended_emojis = self._get_recommended_emojis(content_type, emotion_tone)
        
        if not recommended_emojis:
            return optimized_content, applied_changes
        
        # 智能插入表情
        optimized_content, changes = self._smart_insert_emojis(
            optimized_content, 
            recommended_emojis, 
            content_type,
            emotion_tone
        )
        
        applied_changes.extend(changes)
        
        return optimized_content, applied_changes
    
    def _detect_content_type(self, content: str) -> str:
        """检测内容类型"""
        type_keywords = {
            "美妆护肤": ["护肤", "面膜", "化妆", "口红", "粉底", "精华", "美妆", "彩妆", "保养", "护肤品", "化妆品"],
            "美食分享": ["美食", "好吃", "食物", "餐厅", "菜", "味道", "香", "甜", "酸", "辣", "烹饪", "早餐", "午餐", "晚餐", "下午茶"],
            "购物种草": ["买", "购物", "种草", "推荐", "好物", "折扣", "优惠", "性价比", "值得", "入手", "剁手", "囤货"],
            "穿搭时尚": ["穿搭", "搭配", "衣服", "裙子", "包包", "鞋子", "配饰", "时尚", "风格", "outfit"],
            "居家生活": ["居家", "生活", "家", "房间", "装饰", "收纳", "清洁", "整理", "温馨", "舒适"],
            "学习工作": ["学习", "工作", "读书", "笔记", "效率", "时间管理", "成长", "进步", "努力", "坚持"]
        }
        
        # 计算每个类型的关键词匹配度
        scores = {}
        for content_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                scores[content_type] = score
        
        # 返回得分最高的类型
        if scores:
            return max(scores.keys(), key=lambda k: scores[k])
        
        return "生活日常"
    
    def _detect_emotion_tone(self, content: str) -> str:
        """检测情感基调"""
        emotion_keywords = {
            "开心快乐": ["开心", "快乐", "高兴", "喜欢", "爱了", "太棒", "完美", "满意", "幸福", "美好"],
            "惊喜兴奋": ["惊喜", "震撼", "厉害", "绝了", "炸了", "amazing", "incredible", "哇", "天哪", "不敢相信"],
            "温馨治愈": ["温馨", "治愈", "舒服", "放松", "安静", "平静", "温暖", "柔和", "gentle"],
            "活力满满": ["活力", "精神", "充满", "满满", "元气", "能量", "动力", "活跃", "积极"]
        }
        
        scores = {}
        for tone, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                scores[tone] = score
        
        if scores:
            return max(scores.keys(), key=lambda k: scores[k])
        
        return "开心快乐"  # 默认积极情感
    
    def _get_recommended_emojis(self, content_type: str, emotion_tone: str) -> List[str]:
        """获取推荐表情符号"""
        emojis = set()
        
        # 基于内容类型推荐
        if content_type in self.content_mapping:
            emojis.update(self.content_mapping[content_type][:3])
        
        # 基于情感基调推荐
        emotion_mapping = self.emoji_data.get("智能推荐规则", {}).get("情感基调", {})
        if emotion_tone in emotion_mapping:
            emojis.update(emotion_mapping[emotion_tone][:2])
        
        return list(emojis)[:4]  # 最多4个表情
    
    def _smart_insert_emojis(self, content: str, emojis: List[str], content_type: str, emotion_tone: str) -> Tuple[str, List[Dict]]:
        """智能插入表情符号"""
        if not emojis:
            return content, []
        
        optimized_content = content
        applied_changes = []
        
        # 策略1: 在标题或开头添加主题表情
        if len(content) > 0:
            sentences = re.split(r'[。！？\n]', optimized_content)
            if sentences and len(sentences[0]) < 30:  # 可能是标题
                theme_emoji = self._get_theme_emoji(content_type, emojis)
                if theme_emoji:
                    first_sentence = sentences[0]
                    if not self._has_emoji_at_start(first_sentence):
                        optimized_content = optimized_content.replace(
                            first_sentence, 
                            f"{theme_emoji} {first_sentence.strip()}",
                            1
                        )
                        applied_changes.append({
                            "type": "emoji_insertion",
                            "position": "title",
                            "emoji": theme_emoji,
                            "reason": f"为{content_type}内容添加主题表情"
                        })
        
        # 策略2: 在结尾添加情感表情
        if not self._has_emoji_at_end(optimized_content):
            emotion_emoji = self._get_emotion_emoji(emotion_tone, emojis)
            if emotion_emoji:
                optimized_content = optimized_content.rstrip() + f" {emotion_emoji}"
                applied_changes.append({
                    "type": "emoji_insertion",
                    "position": "ending",
                    "emoji": emotion_emoji,
                    "reason": f"添加{emotion_tone}情感表情"
                })
        
        # 策略3: 在重点词汇后添加强调表情
        emphasis_patterns = [
            (r'(推荐|安利|种草)', '⭐'),
            (r'(超级|特别|非常)好', '✨'),
            (r'(必买|值得)', '💎'),
            (r'(完美|满分)', '💯')
        ]
        
        for pattern, emoji in emphasis_patterns:
            if re.search(pattern, optimized_content) and emoji in emojis:
                optimized_content = re.sub(
                    pattern, 
                    lambda m: f"{m.group()}{emoji}",
                    optimized_content,
                    count=1
                )
                applied_changes.append({
                    "type": "emoji_insertion",
                    "position": "emphasis",
                    "emoji": emoji,
                    "reason": "强调重点内容"
                })
                break
        
        return optimized_content, applied_changes
    
    def _get_theme_emoji(self, content_type: str, available_emojis: List[str]) -> str:
        """获取主题表情"""
        theme_priority = {
            "美妆护肤": ["💄", "✨", "💫"],
            "美食分享": ["🍰", "☕", "🥤"],
            "购物种草": ["🛍️", "💎", "⭐"],
            "穿搭时尚": ["👗", "👠", "✨"],
            "居家生活": ["🏠", "🌸", "💫"],
            "学习工作": ["📚", "💻", "✨"]
        }
        
        if content_type in theme_priority:
            for emoji in theme_priority[content_type]:
                if emoji in available_emojis:
                    return emoji
        
        return available_emojis[0] if available_emojis else ""
    
    def _get_emotion_emoji(self, emotion_tone: str, available_emojis: List[str]) -> str:
        """获取情感表情"""
        emotion_priority = {
            "开心快乐": ["😊", "😄", "🥰"],
            "惊喜兴奋": ["😱", "🤯", "🥳"],
            "温馨治愈": ["💫", "🌸", "✨"],
            "活力满满": ["💪", "🔥", "⭐"]
        }
        
        if emotion_tone in emotion_priority:
            for emoji in emotion_priority[emotion_tone]:
                if emoji in available_emojis:
                    return emoji
        
        return available_emojis[-1] if available_emojis else ""
    
    def _has_emoji_at_start(self, text: str) -> bool:
        """检查文本开头是否有表情"""
        emoji_pattern = r'^[\u263a-\U0001f645]'
        return bool(re.match(emoji_pattern, text.strip()))
    
    def _has_emoji_at_end(self, text: str) -> bool:
        """检查文本结尾是否有表情"""
        emoji_pattern = r'[\u263a-\U0001f645]\s*$'
        return bool(re.search(emoji_pattern, text.strip()))
    
    def get_content_type_emojis(self, content_type: str) -> List[str]:
        """获取指定内容类型的推荐表情"""
        return self.content_mapping.get(content_type, [])