"""
内容分析器 - 违禁词检测和内容质量分析
"""
import re
import jieba
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.database import ProhibitedWord
from app.core.algorithms.smart_prohibited_detector import SmartProhibitedDetector


class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.prohibited_words = self._load_prohibited_words()
        self.smart_detector = SmartProhibitedDetector(db)
    
    def _load_prohibited_words(self) -> List[Dict]:
        """加载违禁词库"""
        words = self.db.query(ProhibitedWord).filter(ProhibitedWord.status == 1).all()
        return [
            {
                "word": word.word,
                "category": word.category,
                "risk_level": word.risk_level
            }
            for word in words
        ]
    
    async def analyze_content(self, content: str) -> Dict[str, Any]:
        """分析内容"""
        # 使用智能违禁词检测器
        detected_issues = self.smart_detector.detect_prohibited_words(content)
        
        # 计算内容质量评分
        content_score = self._calculate_content_score(content, detected_issues)
        
        # 生成优化建议
        suggestions = self._generate_suggestions(content, detected_issues)
        
        return {
            "issues": detected_issues,
            "score": content_score,
            "suggestions": suggestions
        }
    
    def _detect_prohibited_words(self, content: str) -> List[Dict]:
        """检测违禁词"""
        issues = []
        
        for word_info in self.prohibited_words:
            word = word_info["word"]
            
            # 精确匹配
            for match in re.finditer(re.escape(word), content, re.IGNORECASE):
                issues.append({
                    "type": "prohibited_word",
                    "word": word,
                    "position": match.start(),
                    "risk_level": word_info["risk_level"],
                    "category": word_info["category"],
                    "suggestions": self._get_replacement_suggestions(word)
                })
            
            # 变形词检测（简单实现）
            variations = self._generate_word_variations(word)
            for variation in variations:
                for match in re.finditer(re.escape(variation), content, re.IGNORECASE):
                    issues.append({
                        "type": "prohibited_word_variation",
                        "word": variation,
                        "original_word": word,
                        "position": match.start(),
                        "risk_level": word_info["risk_level"],
                        "category": word_info["category"],
                        "suggestions": self._get_replacement_suggestions(word)
                    })
        
        return issues
    
    def _generate_word_variations(self, word: str) -> List[str]:
        """生成词汇变形（简单版本）"""
        variations = []
        
        # 添加空格和符号分隔
        if len(word) > 1:
            for i in range(1, len(word)):
                variations.append(word[:i] + " " + word[i:])
                variations.append(word[:i] + "*" + word[i:])
                variations.append(word[:i] + "." + word[i:])
        
        return variations
    
    def _get_replacement_suggestions(self, word: str) -> List[str]:
        """获取替换建议（从谐音词库获取）"""
        suggestions = []
        
        # 从谐音词库获取替换建议
        from app.models.database import OriginalWord, HomophoneReplacement
        
        original_word = self.db.query(OriginalWord).filter(
            OriginalWord.word == word,
            OriginalWord.status == 1
        ).first()
        
        if original_word:
            # 获取该词的谐音替换
            replacements = self.db.query(HomophoneReplacement).filter(
                HomophoneReplacement.original_word_id == original_word.id,
                HomophoneReplacement.status == 1
            ).order_by(
                HomophoneReplacement.priority.desc(),
                HomophoneReplacement.confidence_score.desc()
            ).limit(3).all()
            
            suggestions.extend([r.replacement_word for r in replacements])
        
        # 如果没有找到谐音词，提供基础替换建议
        if not suggestions and len(word) > 1:
            # 符号分隔
            suggestions.append(word[0] + "*" + word[1:])
            # 空格分隔
            suggestions.append(word[0] + " " + word[1:])
            # 拼音替换
            suggestions.append(word[0] + "x" + word[1:])
        
        return suggestions[:3]  # 最多返回3个建议
    
    def _calculate_content_score(self, content: str, issues: List[Dict]) -> int:
        """计算内容质量评分（0-100分）"""
        base_score = 100
        
        # 根据违禁词扣分
        for issue in issues:
            risk_level = issue.get("risk_level", 1)
            if risk_level == 3:  # 高风险
                base_score -= 20
            elif risk_level == 2:  # 中风险
                base_score -= 10
            else:  # 低风险
                base_score -= 5
        
        # 内容长度评分
        content_length = len(content)
        if content_length < 50:
            base_score -= 10  # 内容太短
        elif content_length > 1000:
            base_score -= 5   # 内容过长
        
        # 段落结构评分
        paragraphs = content.split('\n')
        if len(paragraphs) == 1 and len(content) > 200:
            base_score -= 5  # 缺少段落分隔
        
        return max(0, min(100, base_score))
    
    def _generate_suggestions(self, content: str, issues: List[Dict]) -> List[Dict]:
        """生成优化建议"""
        suggestions = []
        
        # 违禁词替换建议
        if issues:
            suggestions.append({
                "type": "prohibited_words",
                "title": "违禁词替换",
                "description": f"发现 {len(issues)} 个需要替换的词汇，建议使用谐音词或其他表达方式。",
                "priority": "high"
            })
        
        # 内容长度建议
        content_length = len(content)
        if content_length < 50:
            suggestions.append({
                "type": "content_length",
                "title": "增加内容长度",
                "description": "内容较短，建议增加更多细节和描述，提升内容丰富度。",
                "priority": "medium"
            })
        elif content_length > 1000:
            suggestions.append({
                "type": "content_length",
                "title": "精简内容",
                "description": "内容较长，建议精简表达，突出重点信息。",
                "priority": "low"
            })
        
        # 段落结构建议
        paragraphs = content.split('\n')
        if len(paragraphs) == 1 and len(content) > 200:
            suggestions.append({
                "type": "paragraph_structure",
                "title": "优化段落结构",
                "description": "建议将长段落分解为多个短段落，提高可读性。",
                "priority": "medium"
            })
        
        # 表情符号建议
        emoji_count = len(re.findall(r'[😀-🙏]', content))
        if emoji_count == 0:
            suggestions.append({
                "type": "emoji",
                "title": "添加表情符号",
                "description": "适当添加表情符号可以增加内容的亲和力和趣味性。",
                "priority": "low"
            })
        
        # 互动元素建议
        question_count = content.count('?') + content.count('？')
        if question_count == 0:
            suggestions.append({
                "type": "interaction",
                "title": "增加互动元素",
                "description": "添加问句可以提升用户互动，增加评论和点赞。",
                "priority": "medium"
            })
        
        return suggestions