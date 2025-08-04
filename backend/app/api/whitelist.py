"""
白名单管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import re

from app.database.connection import get_database
from app.models.database import WhitelistPattern
from app.api.auth import get_current_admin

router = APIRouter(prefix="/admin/whitelist", tags=["白名单管理"])


# Pydantic模型
class WhitelistPatternCreate(BaseModel):
    prohibited_word: str
    pattern: str
    description: Optional[str] = None
    category: Optional[str] = None
    example: Optional[str] = None
    priority: Optional[int] = 1


class WhitelistPatternUpdate(BaseModel):
    pattern: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    example: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[int] = None


class WhitelistPatternResponse(BaseModel):
    id: int
    prohibited_word: str
    pattern: str
    description: Optional[str]
    category: Optional[str]
    example: Optional[str]
    is_active: int
    priority: int
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WhitelistListResponse(BaseModel):
    patterns: List[WhitelistPatternResponse]
    pagination: dict


@router.get("/list", response_model=WhitelistListResponse)
async def get_whitelist_patterns(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    prohibited_word: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_active: Optional[int] = Query(None),
    db: Session = Depends(get_database),
    current_admin = Depends(get_current_admin)
):
    """获取白名单模式列表"""
    try:
        # 构建查询
        query = db.query(WhitelistPattern)
        
        # 筛选条件
        if prohibited_word:
            query = query.filter(WhitelistPattern.prohibited_word.like(f"%{prohibited_word}%"))
        if category:
            query = query.filter(WhitelistPattern.category == category)  
        if is_active is not None:
            query = query.filter(WhitelistPattern.is_active == is_active)
        
        # 总数
        total = query.count()
        
        # 分页查询
        patterns = query.order_by(WhitelistPattern.priority.desc(), WhitelistPattern.id.desc()).offset((page - 1) * size).limit(size).all()
        
        return WhitelistListResponse(
            patterns=patterns,
            pagination={
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取白名单列表失败: {str(e)}")


@router.post("/create", response_model=WhitelistPatternResponse)
async def create_whitelist_pattern(
    pattern_data: WhitelistPatternCreate,
    db: Session = Depends(get_database),
    current_admin = Depends(get_current_admin)
):
    """创建白名单模式"""
    try:
        # 验证正则表达式
        try:
            re.compile(pattern_data.pattern)
        except re.error as e:
            raise HTTPException(status_code=400, detail=f"无效的正则表达式: {str(e)}")
        
        # 检查是否已存在相同的模式
        existing = db.query(WhitelistPattern).filter(
            WhitelistPattern.prohibited_word == pattern_data.prohibited_word,
            WhitelistPattern.pattern == pattern_data.pattern
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="该白名单模式已存在")
        
        # 创建新模式
        new_pattern = WhitelistPattern(
            prohibited_word=pattern_data.prohibited_word,
            pattern=pattern_data.pattern,
            description=pattern_data.description,
            category=pattern_data.category,
            example=pattern_data.example,
            priority=pattern_data.priority,
            is_active=1,
            created_by=current_admin.username if hasattr(current_admin, 'username') else "admin"
        )
        
        db.add(new_pattern)
        db.commit()
        db.refresh(new_pattern)
        
        return new_pattern
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建白名单模式失败: {str(e)}")


@router.put("/{pattern_id}", response_model=WhitelistPatternResponse)
async def update_whitelist_pattern(
    pattern_id: int,
    pattern_data: WhitelistPatternUpdate,
    db: Session = Depends(get_database),
    current_admin = Depends(get_current_admin)
):
    """更新白名单模式"""
    try:
        # 查找模式
        pattern = db.query(WhitelistPattern).filter(WhitelistPattern.id == pattern_id).first()
        if not pattern:
            raise HTTPException(status_code=404, detail="白名单模式不存在")
        
        # 验证正则表达式
        if pattern_data.pattern:
            try:
                re.compile(pattern_data.pattern)
            except re.error as e:
                raise HTTPException(status_code=400, detail=f"无效的正则表达式: {str(e)}")
        
        # 更新字段
        update_data = pattern_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pattern, field, value)
        
        pattern.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(pattern)
        
        return pattern
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新白名单模式失败: {str(e)}")


@router.delete("/{pattern_id}")
async def delete_whitelist_pattern(
    pattern_id: int,
    db: Session = Depends(get_database),
    current_admin = Depends(get_current_admin)
):
    """删除白名单模式"""
    try:
        # 查找模式
        pattern = db.query(WhitelistPattern).filter(WhitelistPattern.id == pattern_id).first()
        if not pattern:
            raise HTTPException(status_code=404, detail="白名单模式不存在")
        
        db.delete(pattern)
        db.commit()
        
        return {"message": "白名单模式删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除白名单模式失败: {str(e)}")


@router.get("/categories")
async def get_whitelist_categories(
    db: Session = Depends(get_database),
    current_admin = Depends(get_current_admin)
):
    """获取白名单分类列表"""
    try:
        categories = db.query(WhitelistPattern.category).filter(
            WhitelistPattern.category.isnot(None),
            WhitelistPattern.is_active == 1
        ).distinct().all()
        
        return {
            "categories": [cat[0] for cat in categories if cat[0]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")


@router.post("/test")
async def test_whitelist_pattern(
    pattern: str,
    test_text: str,
    db: Session = Depends(get_database),
    current_admin = Depends(get_current_admin)
):
    """测试白名单模式"""
    try:
        # 验证正则表达式
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise HTTPException(status_code=400, detail=f"无效的正则表达式: {str(e)}")
        
        # 测试匹配
        matches = compiled_pattern.findall(test_text)
        is_match = bool(matches)
        
        return {
            "pattern": pattern,
            "test_text": test_text,
            "is_match": is_match,
            "matches": matches,
            "match_positions": [m.span() for m in compiled_pattern.finditer(test_text)]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.get("/stats")
async def get_whitelist_stats(
    db: Session = Depends(get_database),
    current_admin = Depends(get_current_admin)
):
    """获取白名单统计信息"""
    try:
        total = db.query(WhitelistPattern).count()
        active = db.query(WhitelistPattern).filter(WhitelistPattern.is_active == 1).count()
        inactive = total - active
        
        # 按分类统计
        from sqlalchemy import func
        category_stats = db.query(
            WhitelistPattern.category,
            func.count(WhitelistPattern.id).label('count')
        ).filter(
            WhitelistPattern.is_active == 1
        ).group_by(WhitelistPattern.category).all()
        
        # 按违禁词统计
        word_stats = db.query(
            WhitelistPattern.prohibited_word,
            func.count(WhitelistPattern.id).label('count')
        ).filter(
            WhitelistPattern.is_active == 1
        ).group_by(WhitelistPattern.prohibited_word).all()
        
        return {
            "overview": {
                "total_patterns": total,
                "active_patterns": active,
                "inactive_patterns": inactive
            },
            "by_category": [{"category": cat or "未分类", "count": count} for cat, count in category_stats],
            "by_word": [{"word": word, "count": count} for word, count in word_stats]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")