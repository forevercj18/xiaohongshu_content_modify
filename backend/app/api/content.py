"""
内容处理相关API
"""
import json
import time
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_database
from app.models.database import UserContentHistory
from app.core.algorithms.content_analyzer import ContentAnalyzer
from app.core.algorithms.content_optimizer import ContentOptimizer

router = APIRouter()


class ContentRequest(BaseModel):
    content: str
    user_session: Optional[str] = None


class DetectedIssue(BaseModel):
    type: str
    word: str
    position: int
    risk_level: int
    suggestions: List[str]


class OptimizationSuggestion(BaseModel):
    type: str
    title: str
    description: str
    priority: str


class ContentAnalysisResponse(BaseModel):
    detected_issues: List[DetectedIssue]
    content_score: int
    suggestions: List[OptimizationSuggestion]
    processing_time: float


class ContentOptimizeRequest(BaseModel):
    content: str
    apply_suggestions: List[str] = []
    user_session: Optional[str] = None


class ContentOptimizeResponse(BaseModel):
    optimized_content: str
    applied_changes: List[dict]
    score_improvement: int
    processing_time: float


class HistoryItem(BaseModel):
    id: int
    original_content: str
    optimized_content: Optional[str]
    content_score_before: Optional[int]
    content_score_after: Optional[int]
    created_at: str


@router.post("/analyze", response_model=ContentAnalysisResponse)
async def analyze_content(
    request: ContentRequest,
    db: Session = Depends(get_database)
):
    """分析内容"""
    start_time = time.time()
    
    try:
        # 初始化分析器
        analyzer = ContentAnalyzer(db)
        
        # 执行分析
        analysis_result = await analyzer.analyze_content(request.content)
        
        processing_time = time.time() - start_time
        
        # 保存到历史记录
        user_session = request.user_session or str(uuid.uuid4())
        history = UserContentHistory(
            user_session=user_session,
            original_content=request.content,
            detected_issues=json.dumps(analysis_result["issues"], ensure_ascii=False),
            content_score_before=analysis_result["score"],
            processing_time=processing_time,
            is_optimized=0
        )
        db.add(history)
        db.commit()
        
        return ContentAnalysisResponse(
            detected_issues=[
                DetectedIssue(
                    type=issue["type"],
                    word=issue["word"],
                    position=issue["position"],
                    risk_level=issue["risk_level"],
                    suggestions=issue["suggestions"]
                ) for issue in analysis_result["issues"]
            ],
            content_score=analysis_result["score"],
            suggestions=[
                OptimizationSuggestion(
                    type=sugg["type"],
                    title=sugg["title"],
                    description=sugg["description"],
                    priority=sugg["priority"]
                ) for sugg in analysis_result["suggestions"]
            ],
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内容分析失败: {str(e)}")


@router.post("/optimize", response_model=ContentOptimizeResponse)
async def optimize_content(
    request: ContentOptimizeRequest,
    db: Session = Depends(get_database)
):
    """优化内容"""
    start_time = time.time()
    
    try:
        # 初始化优化器
        optimizer = ContentOptimizer(db)
        
        # 执行优化
        optimization_result = await optimizer.optimize_content(
            request.content,
            apply_suggestions=request.apply_suggestions
        )
        
        processing_time = time.time() - start_time
        
        # 更新历史记录
        user_session = request.user_session or str(uuid.uuid4())
        
        # 查找最近的分析记录
        recent_history = db.query(UserContentHistory).filter(
            UserContentHistory.user_session == user_session,
            UserContentHistory.original_content == request.content
        ).order_by(UserContentHistory.created_at.desc()).first()
        
        if recent_history:
            # 更新现有记录
            recent_history.optimized_content = optimization_result["optimized_content"]
            recent_history.applied_optimizations = json.dumps(optimization_result["applied_changes"], ensure_ascii=False)
            recent_history.content_score_after = optimization_result["score_after"]
            recent_history.is_optimized = 1
        else:
            # 创建新记录
            history = UserContentHistory(
                user_session=user_session,
                original_content=request.content,
                optimized_content=optimization_result["optimized_content"],
                applied_optimizations=json.dumps(optimization_result["applied_changes"], ensure_ascii=False),
                content_score_after=optimization_result["score_after"],
                processing_time=processing_time,
                is_optimized=1
            )
            db.add(history)
        
        db.commit()
        
        return ContentOptimizeResponse(
            optimized_content=optimization_result["optimized_content"],
            applied_changes=optimization_result["applied_changes"],
            score_improvement=optimization_result["score_improvement"],
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内容优化失败: {str(e)}")


@router.get("/history", response_model=List[HistoryItem])
async def get_content_history(
    user_session: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_database)
):
    """获取内容历史记录"""
    query = db.query(UserContentHistory)
    
    if user_session:
        query = query.filter(UserContentHistory.user_session == user_session)
    
    histories = query.order_by(UserContentHistory.created_at.desc()).limit(limit).all()
    
    return [
        HistoryItem(
            id=h.id,
            original_content=h.original_content,
            optimized_content=h.optimized_content,
            content_score_before=h.content_score_before,
            content_score_after=h.content_score_after,
            created_at=h.created_at.isoformat()
        ) for h in histories
    ]