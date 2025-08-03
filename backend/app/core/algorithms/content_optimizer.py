"""
内容优化器 - 谐音词替换和内容优化
"""
import re
import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.database import OriginalWord, HomophoneReplacement
from app.core.algorithms.emoji_inserter import EmojiInserter


class ContentOptimizer:
    """内容优化器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.homophone_mappings = self._load_homophone_mappings()
        self.emoji_inserter = EmojiInserter(db)
    
    def _load_homophone_mappings(self) -> Dict[str, List[Dict]]:
        """加载谐音词映射"""
        mappings = {}
        
        # 查询所有启用的谐音词替换
        replacements = self.db.query(HomophoneReplacement).join(OriginalWord).filter(
            HomophoneReplacement.status == 1,
            OriginalWord.status == 1
        ).all()
        
        for replacement in replacements:
            original_word = replacement.original.word
            if original_word not in mappings:
                mappings[original_word] = []
            
            mappings[original_word].append({
                "replacement": replacement.replacement_word,
                "type": replacement.replacement_type,
                "priority": replacement.priority,
                "confidence": replacement.confidence_score,
                "usage_count": replacement.usage_count,
                "id": replacement.id
            })
        
        return mappings
    
    async def optimize_content(self, content: str, apply_suggestions: List[str] = None) -> Dict[str, Any]:
        """优化内容"""
        optimized_content = content
        applied_changes = []
        
        # 应用谐音词替换
        if not apply_suggestions or "homophone_replacement" in apply_suggestions:
            optimized_content, changes = self._apply_homophone_replacements(optimized_content)
            applied_changes.extend(changes)
        
        # 应用其他优化
        if not apply_suggestions or "structure_optimization" in apply_suggestions:
            optimized_content, changes = self._apply_structure_optimization(optimized_content)
            applied_changes.extend(changes)
        
        # 应用表情符号优化
        if not apply_suggestions or "emoji_optimization" in apply_suggestions:
            optimized_content, changes = self.emoji_inserter.analyze_content_and_insert_emojis(optimized_content)
            applied_changes.extend(changes)
        
        # 计算优化后的分数
        from app.core.algorithms.content_analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer(self.db)
        
        # 分析原始内容
        original_analysis = await analyzer.analyze_content(content)
        original_score = original_analysis["score"]
        
        # 分析优化后内容
        optimized_analysis = await analyzer.analyze_content(optimized_content)
        optimized_score = optimized_analysis["score"]
        
        # 更新使用统计
        self._update_usage_statistics(applied_changes)
        
        return {
            "optimized_content": optimized_content,
            "applied_changes": applied_changes,
            "score_before": original_score,
            "score_after": optimized_score,
            "score_improvement": optimized_score - original_score
        }
    
    def _apply_homophone_replacements(self, content: str) -> tuple[str, List[Dict]]:
        """应用谐音词替换"""
        optimized_content = content
        applied_changes = []
        
        for original_word, replacements in self.homophone_mappings.items():
            if original_word in optimized_content:
                # 选择替换词
                replacement_info = self._select_replacement(replacements)
                if replacement_info:
                    replacement_word = replacement_info["replacement"]
                    
                    # 执行替换
                    old_content = optimized_content
                    optimized_content = optimized_content.replace(original_word, replacement_word)
                    
                    if old_content != optimized_content:
                        applied_changes.append({
                            "type": "homophone_replacement",
                            "original_word": original_word,
                            "replacement_word": replacement_word,
                            "replacement_type": replacement_info["type"],
                            "replacement_id": replacement_info["id"],
                            "positions": self._find_word_positions(old_content, original_word)
                        })
        
        return optimized_content, applied_changes
    
    def _select_replacement(self, replacements: List[Dict]) -> Optional[Dict]:
        """选择谐音词替换"""
        if not replacements:
            return None
        
        # 优先选择priority=1的词汇
        priority_words = [r for r in replacements if r["priority"] == 1]
        if priority_words:
            return random.choice(priority_words)
        
        # 如果没有高优先级词汇，按置信度加权随机选择
        weights = [r["confidence"] for r in replacements]
        return random.choices(replacements, weights=weights)[0]
    
    def _find_word_positions(self, content: str, word: str) -> List[int]:
        """查找词汇在内容中的位置"""
        positions = []
        start = 0
        while True:
            pos = content.find(word, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        return positions
    
    def _apply_structure_optimization(self, content: str) -> tuple[str, List[Dict]]:
        """应用结构优化"""
        optimized_content = content
        applied_changes = []
        
        # 段落优化
        if len(content) > 200 and '\n' not in content:
            # 简单的段落分割（在句号后分割）
            sentences = re.split(r'([。！？])', content)
            if len(sentences) > 3:
                # 每2-3句组成一个段落
                paragraphs = []
                current_paragraph = ""
                sentence_count = 0
                
                for i in range(0, len(sentences) - 1, 2):
                    if i + 1 < len(sentences):
                        sentence = sentences[i] + sentences[i + 1]
                        current_paragraph += sentence
                        sentence_count += 1
                        
                        if sentence_count >= 2 or len(current_paragraph) > 100:
                            paragraphs.append(current_paragraph.strip())
                            current_paragraph = ""
                            sentence_count = 0
                
                if current_paragraph.strip():
                    paragraphs.append(current_paragraph.strip())
                
                if len(paragraphs) > 1:
                    optimized_content = '\n\n'.join(paragraphs)
                    applied_changes.append({
                        "type": "paragraph_structure",
                        "description": f"将长段落分解为 {len(paragraphs)} 个段落",
                        "paragraphs_count": len(paragraphs)
                    })
        
        # 表情符号优化（简单示例）
        emoji_count = len(re.findall(r'[😀-🙏]', content))
        if emoji_count == 0 and len(content) > 50:
            # 在内容末尾添加适当的表情符号
            positive_emojis = ['✨', '👍', '💫', '🌟', '😊']
            selected_emoji = random.choice(positive_emojis)
            optimized_content += f" {selected_emoji}"
            
            applied_changes.append({
                "type": "emoji_addition",
                "description": f"添加表情符号: {selected_emoji}",
                "emoji": selected_emoji
            })
        
        return optimized_content, applied_changes
    
    def _update_usage_statistics(self, applied_changes: List[Dict]):
        """更新使用统计"""
        for change in applied_changes:
            if change["type"] == "homophone_replacement":
                replacement_id = change.get("replacement_id")
                if replacement_id:
                    # 更新谐音词使用次数
                    replacement = self.db.query(HomophoneReplacement).filter(
                        HomophoneReplacement.id == replacement_id
                    ).first()
                    if replacement:
                        replacement.usage_count += 1
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"更新使用统计失败: {e}")
    
    def get_replacement_suggestions(self, word: str) -> List[Dict]:
        """获取指定词汇的替换建议"""
        if word in self.homophone_mappings:
            replacements = self.homophone_mappings[word]
            return sorted(replacements, key=lambda x: (x["priority"], x["confidence"]), reverse=True)
        return []