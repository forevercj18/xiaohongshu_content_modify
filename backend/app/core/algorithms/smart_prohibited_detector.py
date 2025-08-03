"""
智能违禁词检测器 - 基于上下文语义分析
"""
import re
import jieba
from typing import List, Dict, Any, Tuple, Set
from sqlalchemy.orm import Session

from app.models.database import ProhibitedWord


class SmartProhibitedDetector:
    """智能违禁词检测器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.prohibited_words = self._load_prohibited_words()
        self.whitelist_patterns = self._build_whitelist_patterns()
        self.context_rules = self._build_context_rules()
    
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
    
    def _build_whitelist_patterns(self) -> Dict[str, List[str]]:
        """构建白名单模式 - 包含违禁词但语义正常的表达"""
        return {
            "第一": [
                r"第一次",
                r"第一步",
                r"第一天",
                r"第一个",
                r"第一名",
                r"第一季",
                r"第一期",
                r"第一章",
                r"第一级",
                r"第一层",
                r"第一道",
                r"第一款",
                r"第一批",
                r"第一部",
                r"第一集",
                r"第一阶段",
                r"第一印象",
                r"第一感觉",
                r"第一眼",
                r"第一反应",
                r"第一时间",
                r"第一年",
                r"第一月",
                r"第一周",
                r"排名第一",
                r"世界第一",
                r"全国第一",
                r"行业第一"
            ],
            "最": [
                r"最近",
                r"最新",
                r"最后",
                r"最初",
                r"最终",
                r"最基本",
                r"最常见",
                r"最重要",
                r"最简单",
                r"最复杂",
                r"最大限度",
                r"最小化",
                r"最优化",
                r"最适合",
                r"最合适",
                r"最理想",
                r"最完美",
                r"最精准",
                r"最准确",
                r"最有效",
                r"最安全",
                r"最健康",
                r"最天然",
                r"最纯净"
            ],
            "包治": [
                r"包装治疗",
                r"包含治疗",
                r"不包治",
                r"非包治"
            ],
            "减肥": [
                r"减肥餐",
                r"减肥食谱",
                r"减肥运动",
                r"减肥方法",
                r"健康减肥",
                r"科学减肥",
                r"减肥心得",
                r"减肥经验",
                r"减肥日记",
                r"减肥过程",
                r"减肥成功",
                r"减肥失败",
                r"想要减肥",
                r"准备减肥",
                r"开始减肥",
                r"正在减肥"
            ],
            "微商": [
                r"不是微商",
                r"拒绝微商",
                r"远离微商",
                r"讨厌微商",
                r"反对微商"
            ]
        }
    
    def _build_context_rules(self) -> Dict[str, Dict]:
        """构建上下文规则"""
        return {
            "第一": {
                "safe_contexts": [
                    "序数词用法",  # 第一次、第一个、第一天等
                    "排名表达",    # 排名第一、世界第一等
                    "时间顺序",    # 第一时间、第一印象等
                ],
                "dangerous_contexts": [
                    "营销推广",    # 第一品牌、第一选择等
                    "效果夸大"     # 第一神器等
                ]
            },
            "最": {
                "safe_contexts": [
                    "时间副词",    # 最近、最新、最后等
                    "程度副词",    # 最基本、最常见等
                    "客观描述"     # 最大、最小等
                ],
                "dangerous_contexts": [
                    "绝对化宣传",  # 最好、最强、最有效等
                    "夸大效果"     # 最神奇、最厉害等
                ]
            },
            "包治": {
                "safe_contexts": [
                    "否定用法",    # 不包治、非包治等
                    "医学术语"     # 包装治疗等
                ],
                "dangerous_contexts": [
                    "医疗承诺"     # 包治百病等
                ]
            }
        }
    
    def detect_prohibited_words(self, content: str) -> List[Dict]:
        """智能检测违禁词"""
        issues = []
        
        # 分词处理
        words = list(jieba.cut(content))
        
        for word_info in self.prohibited_words:
            prohibited_word = word_info["word"]
            
            # 查找所有匹配位置
            matches = list(re.finditer(re.escape(prohibited_word), content, re.IGNORECASE))
            
            for match in matches:
                start_pos = match.start()
                end_pos = match.end()
                
                # 提取上下文
                context = self._extract_context(content, start_pos, end_pos)
                
                # 检查是否在白名单中
                if self._is_in_whitelist(prohibited_word, context):
                    continue
                
                # 进行上下文语义分析
                risk_assessment = self._analyze_context_risk(
                    prohibited_word, 
                    context, 
                    word_info
                )
                
                if risk_assessment["is_violation"]:
                    issues.append({
                        "type": "prohibited_word",
                        "word": prohibited_word,
                        "position": start_pos,
                        "risk_level": risk_assessment["adjusted_risk_level"],
                        "category": word_info["category"],
                        "context": context["full_context"],
                        "analysis": risk_assessment["analysis"],
                        "confidence": risk_assessment["confidence"],
                        "suggestions": self._get_contextual_suggestions(prohibited_word, context)
                    })
        
        return issues
    
    def _extract_context(self, content: str, start_pos: int, end_pos: int) -> Dict[str, str]:
        """提取上下文信息"""
        # 提取前后各20个字符作为局部上下文
        local_start = max(0, start_pos - 20)
        local_end = min(len(content), end_pos + 20)
        local_context = content[local_start:local_end]
        
        # 提取句子级别的上下文
        sentences = re.split(r'[。！？\n]', content)
        current_sentence = ""
        
        for sentence in sentences:
            if start_pos >= content.find(sentence) and start_pos < content.find(sentence) + len(sentence):
                current_sentence = sentence.strip()
                break
        
        # 提取段落级别的上下文
        paragraphs = content.split('\n')
        current_paragraph = ""
        
        for paragraph in paragraphs:
            if start_pos >= content.find(paragraph) and start_pos < content.find(paragraph) + len(paragraph):
                current_paragraph = paragraph.strip()
                break
        
        return {
            "local_context": local_context,
            "sentence_context": current_sentence,
            "paragraph_context": current_paragraph,
            "full_context": content
        }
    
    def _is_in_whitelist(self, prohibited_word: str, context: Dict[str, str]) -> bool:
        """检查是否在白名单中"""
        if prohibited_word not in self.whitelist_patterns:
            return False
        
        patterns = self.whitelist_patterns[prohibited_word]
        local_context = context["local_context"]
        
        for pattern in patterns:
            if re.search(pattern, local_context, re.IGNORECASE):
                return True
        
        return False
    
    def _analyze_context_risk(self, prohibited_word: str, context: Dict[str, str], word_info: Dict) -> Dict:
        """分析上下文风险"""
        sentence = context["sentence_context"]
        local_context = context["local_context"]
        
        # 基础风险等级
        base_risk = word_info["risk_level"]
        
        # 上下文分析
        risk_indicators = self._get_risk_indicators(prohibited_word, sentence, local_context)
        safety_indicators = self._get_safety_indicators(prohibited_word, sentence, local_context)
        
        # 计算风险调整
        risk_adjustment = 0
        confidence = 0.7  # 基础置信度
        
        if safety_indicators["count"] > risk_indicators["count"]:
            # 安全指示器更多，降低风险
            risk_adjustment = -1
            confidence = min(0.9, confidence + 0.2)
            is_violation = False
            analysis = f"上下文分析：检测到安全用法，{safety_indicators['details']}"
        elif risk_indicators["count"] > 0:
            # 存在风险指示器，提高风险
            risk_adjustment = min(1, risk_indicators["count"] - safety_indicators["count"])
            confidence = min(0.95, confidence + 0.1 * risk_indicators["count"])
            is_violation = True
            analysis = f"上下文分析：检测到风险用法，{risk_indicators['details']}"
        else:
            # 中性上下文，保持原有风险级别
            is_violation = base_risk >= 2  # 中风险以上才认为是违规
            analysis = "上下文分析：中性用法，按原有风险级别处理"
        
        adjusted_risk_level = max(1, min(3, base_risk + risk_adjustment))
        
        return {
            "is_violation": is_violation,
            "adjusted_risk_level": adjusted_risk_level,
            "confidence": confidence,
            "analysis": analysis,
            "risk_indicators": risk_indicators,
            "safety_indicators": safety_indicators
        }
    
    def _get_risk_indicators(self, word: str, sentence: str, local_context: str) -> Dict:
        """获取风险指示器"""
        risk_patterns = {
            "营销推广": [r"推荐", r"安利", r"种草", r"必买", r"限时", r"特价", r"优惠"],
            "绝对化表达": [r"绝对", r"100%", r"百分百", r"完全", r"彻底"],
            "医疗承诺": [r"治疗", r"治愈", r"康复", r"根治", r"药效", r"疗效"],
            "夸大宣传": [r"神奇", r"奇迹", r"秘密", r"独家", r"专利", r"权威"],
            "紧迫感营销": [r"马上", r"立即", r"赶紧", r"抓紧", r"仅限", r"名额有限"]
        }
        
        indicators = []
        for category, patterns in risk_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sentence + local_context, re.IGNORECASE):
                    indicators.append(category)
        
        return {
            "count": len(indicators),
            "details": "、".join(set(indicators)) if indicators else "无特定风险指示器"
        }
    
    def _get_safety_indicators(self, word: str, sentence: str, local_context: str) -> Dict:
        """获取安全指示器"""
        safety_patterns = {
            "客观描述": [r"介绍", r"分享", r"体验", r"感受", r"记录"],
            "时间表达": [r"最近", r"昨天", r"今天", r"明天", r"第一次", r"第一天"],
            "否定用法": [r"不是", r"并非", r"没有", r"不会", r"拒绝"],
            "疑问表达": [r"是否", r"会不会", r"有没有", r"？", r"\?"],
            "比较表达": [r"相比", r"比较", r"对比", r"差别", r"区别"]
        }
        
        indicators = []
        for category, patterns in safety_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sentence + local_context, re.IGNORECASE):
                    indicators.append(category)
        
        return {
            "count": len(indicators),
            "details": "、".join(set(indicators)) if indicators else "无特定安全指示器"
        }
    
    def _get_contextual_suggestions(self, word: str, context: Dict[str, str]) -> List[str]:
        """根据上下文提供替换建议"""
        suggestions = []
        
        # 基于上下文的智能建议
        if "第一" in word:
            if re.search(r"第一次|第一天|第一个", context["local_context"]):
                # 序数词用法，建议保持或轻微修改
                suggestions.extend(["初次", "首次", "头一次"])
            else:
                # 可能的营销用法，建议更保守的表达
                suggestions.extend(["优秀", "领先", "推荐"])
        
        elif "最" in word:
            suggestions.extend(["很", "非常", "十分", "相当"])
        
        elif "减肥" in word:
            suggestions.extend(["塑形", "瘦身", "体重管理", "健康管理"])
        
        elif "微商" in word:
            suggestions.extend(["个人代购", "朋友推荐", "个人分享"])
        
        # 通用替换建议
        if not suggestions:
            # 符号分隔
            if len(word) > 1:
                suggestions.append(word[0] + "*" + word[1:])
                suggestions.append(word[0] + " " + word[1:])
        
        return suggestions[:3]  # 最多返回3个建议