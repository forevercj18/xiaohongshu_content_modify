"""
统计相关API
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database.connection import get_database
from app.models.database import UserContentHistory, ProhibitedWord, HomophoneReplacement, AdminLog

router = APIRouter()


class DashboardStats(BaseModel):
    total_detections: int
    total_optimizations: int
    total_prohibited_words: int
    total_homophone_words: int
    avg_score_improvement: float
    recent_activity: List[Dict[str, Any]]


class UsageStats(BaseModel):
    date: str
    detections: int
    optimizations: int
    avg_processing_time: float


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_database)):
    """获取仪表板统计数据"""
    
    # 基础统计
    total_detections = db.query(UserContentHistory).count()
    total_optimizations = db.query(UserContentHistory).filter(UserContentHistory.is_optimized == 1).count()
    total_prohibited_words = db.query(ProhibitedWord).filter(ProhibitedWord.status == 1).count()
    total_homophone_words = db.query(HomophoneReplacement).filter(HomophoneReplacement.status == 1).count()
    
    # 平均分数提升
    score_improvements = db.query(
        (UserContentHistory.content_score_after - UserContentHistory.content_score_before).label('improvement')
    ).filter(
        UserContentHistory.content_score_after.isnot(None),
        UserContentHistory.content_score_before.isnot(None)
    ).all()
    
    avg_score_improvement = 0
    if score_improvements:
        improvements = [s.improvement for s in score_improvements if s.improvement]
        avg_score_improvement = sum(improvements) / len(improvements) if improvements else 0
    
    # 最近活动
    recent_histories = db.query(UserContentHistory).order_by(desc(UserContentHistory.created_at)).limit(5).all()
    recent_activity = []
    for history in recent_histories:
        activity = {
            "type": "optimization" if history.is_optimized else "detection",
            "content_preview": history.original_content[:50] + "..." if len(history.original_content) > 50 else history.original_content,
            "score_before": history.content_score_before,
            "score_after": history.content_score_after,
            "created_at": history.created_at.isoformat()
        }
        recent_activity.append(activity)
    
    return DashboardStats(
        total_detections=total_detections,
        total_optimizations=total_optimizations,
        total_prohibited_words=total_prohibited_words,
        total_homophone_words=total_homophone_words,
        avg_score_improvement=round(avg_score_improvement, 2),
        recent_activity=recent_activity
    )


@router.get("/usage", response_model=List[UsageStats])
async def get_usage_stats(days: int = 7, db: Session = Depends(get_database)):
    """获取使用统计（按日期）"""
    
    # 计算日期范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # 按日期统计用户内容历史
    stats = db.query(
        func.date(UserContentHistory.created_at).label('date'),
        func.count(UserContentHistory.id).label('detections'),
        func.sum(UserContentHistory.is_optimized).label('optimizations'),
        func.avg(UserContentHistory.processing_time).label('avg_processing_time')
    ).filter(
        func.date(UserContentHistory.created_at) >= start_date,
        func.date(UserContentHistory.created_at) <= end_date
    ).group_by(
        func.date(UserContentHistory.created_at)
    ).order_by(
        func.date(UserContentHistory.created_at)
    ).all()
    
    # 填充缺失的日期
    result = []
    current_date = start_date
    stats_dict = {stat.date: stat for stat in stats}
    
    while current_date <= end_date:
        # 将date对象转换为字符串进行匹配
        current_date_str = current_date.isoformat()
        if current_date_str in stats_dict:
            stat = stats_dict[current_date_str]
            result.append(UsageStats(
                date=current_date_str,
                detections=stat.detections or 0,
                optimizations=stat.optimizations or 0,
                avg_processing_time=round(stat.avg_processing_time or 0, 3)
            ))
        else:
            result.append(UsageStats(
                date=current_date_str,
                detections=0,
                optimizations=0,
                avg_processing_time=0
            ))
        current_date += timedelta(days=1)
    
    return result


@router.get("/prohibited-words/categories")
async def get_prohibited_word_categories(db: Session = Depends(get_database)):
    """获取违禁词分类统计"""
    
    categories = db.query(
        ProhibitedWord.category,
        func.count(ProhibitedWord.id).label('count')
    ).filter(
        ProhibitedWord.status == 1
    ).group_by(
        ProhibitedWord.category
    ).all()
    
    return [{"category": cat.category, "count": cat.count} for cat in categories]


@router.get("/homophone-words/usage")
async def get_homophone_usage_stats(db: Session = Depends(get_database)):
    """获取谐音词使用统计"""
    
    # 最常用的谐音词
    top_used = db.query(HomophoneReplacement).filter(
        HomophoneReplacement.status == 1
    ).order_by(desc(HomophoneReplacement.usage_count)).limit(10).all()
    
    result = []
    for replacement in top_used:
        result.append({
            "original_word": replacement.original.word,
            "replacement_word": replacement.replacement_word,
            "usage_count": replacement.usage_count,
            "replacement_type": replacement.replacement_type
        })
    
    return result