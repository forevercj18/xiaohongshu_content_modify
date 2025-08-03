"""
小红书表情管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import json
from datetime import datetime

from app.database.connection import get_database as get_db
from app.models.database import XiaohongshuEmoji, EmojiCategory, EmojiUsageLog
from app.api.auth import get_current_admin

router = APIRouter(prefix="/api/emoji", tags=["表情管理"])


# ==================== 用户API (无需认证) ====================

@router.get("/list", summary="获取表情列表")
async def get_emoji_list(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="表情分类"),
    emoji_type: Optional[str] = Query(None, description="表情类型(R/H)"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    limit: int = Query(50, description="返回数量限制")
):
    """获取表情列表 - 用户端"""
    query = db.query(XiaohongshuEmoji).filter(XiaohongshuEmoji.status == 1)
    
    if category:
        query = query.filter(XiaohongshuEmoji.category == category)
    
    if emoji_type:
        query = query.filter(XiaohongshuEmoji.emoji_type == emoji_type)
    
    if keyword:
        query = query.filter(
            or_(
                XiaohongshuEmoji.name.contains(keyword),
                XiaohongshuEmoji.keywords.contains(keyword),
                XiaohongshuEmoji.description.contains(keyword)
            )
        )
    
    emojis = query.order_by(
        XiaohongshuEmoji.priority.desc(),
        XiaohongshuEmoji.usage_count.desc()
    ).limit(limit).all()
    
    return {
        "emojis": [
            {
                "id": emoji.id,
                "code": emoji.code,
                "name": emoji.name,
                "emoji_type": emoji.emoji_type,
                "category": emoji.category,
                "subcategory": emoji.subcategory,
                "description": emoji.description,
                "keywords": json.loads(emoji.keywords or "[]"),
                "usage_count": emoji.usage_count,
                "priority": emoji.priority
            }
            for emoji in emojis
        ],
        "total": len(emojis)
    }


@router.get("/categories", summary="获取表情分类")
async def get_emoji_categories(db: Session = Depends(get_db)):
    """获取表情分类列表"""
    categories = db.query(EmojiCategory).filter(
        EmojiCategory.status == 1
    ).order_by(EmojiCategory.sort_order).all()
    
    return {
        "categories": [
            {
                "id": cat.id,
                "name": cat.name,
                "display_name": cat.display_name,
                "description": cat.description,
                "icon": cat.icon,
                "emoji_count": cat.emoji_count
            }
            for cat in categories
        ]
    }


@router.get("/search", summary="搜索表情")
async def search_emojis(
    q: str = Query(..., description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """智能搜索表情"""
    emojis = db.query(XiaohongshuEmoji).filter(
        XiaohongshuEmoji.status == 1,
        or_(
            XiaohongshuEmoji.name.contains(q),
            XiaohongshuEmoji.keywords.contains(q),
            XiaohongshuEmoji.description.contains(q)
        )
    ).order_by(
        XiaohongshuEmoji.priority.desc(),
        XiaohongshuEmoji.usage_count.desc()
    ).limit(20).all()
    
    return {
        "emojis": [
            {
                "id": emoji.id,
                "code": emoji.code,
                "name": emoji.name,
                "emoji_type": emoji.emoji_type,
                "category": emoji.category,
                "description": emoji.description,
                "keywords": json.loads(emoji.keywords or "[]")
            }
            for emoji in emojis
        ],
        "keyword": q,
        "total": len(emojis)
    }


@router.post("/usage", summary="记录表情使用")
async def log_emoji_usage(
    emoji_id: int,
    usage_type: str,
    user_session: Optional[str] = None,
    content_id: Optional[int] = None,
    position: Optional[int] = None,
    context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """记录表情使用情况"""
    # 检查表情是否存在
    emoji = db.query(XiaohongshuEmoji).filter(
        XiaohongshuEmoji.id == emoji_id,
        XiaohongshuEmoji.status == 1
    ).first()
    
    if not emoji:
        raise HTTPException(status_code=404, detail="表情不存在")
    
    # 记录使用日志
    usage_log = EmojiUsageLog(
        emoji_id=emoji_id,
        user_session=user_session,
        content_id=content_id,
        usage_type=usage_type,
        position=position,
        context=context
    )
    db.add(usage_log)
    
    # 更新使用次数
    emoji.usage_count += 1
    
    db.commit()
    
    return {"message": "使用记录已保存", "emoji_code": emoji.code}


# ==================== 管理员API (需要认证) ====================

@router.get("/admin/list", summary="管理员获取表情列表")
async def admin_get_emoji_list(
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin),
    category: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """管理员获取表情列表"""
    query = db.query(XiaohongshuEmoji)
    
    if category:
        query = query.filter(XiaohongshuEmoji.category == category)
    
    if status is not None:
        query = query.filter(XiaohongshuEmoji.status == status)
    
    total = query.count()
    emojis = query.order_by(XiaohongshuEmoji.created_at.desc()).offset(
        (page - 1) * size
    ).limit(size).all()
    
    return {
        "emojis": [
            {
                "id": emoji.id,
                "code": emoji.code,
                "name": emoji.name,
                "emoji_type": emoji.emoji_type,
                "category": emoji.category,
                "subcategory": emoji.subcategory,
                "description": emoji.description,
                "keywords": json.loads(emoji.keywords or "[]"),
                "usage_count": emoji.usage_count,
                "priority": emoji.priority,
                "is_verified": emoji.is_verified,
                "status": emoji.status,
                "created_by": emoji.created_by,
                "created_at": emoji.created_at.isoformat() if emoji.created_at else None,
                "updated_at": emoji.updated_at.isoformat() if emoji.updated_at else None
            }
            for emoji in emojis
        ],
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size
        }
    }


@router.post("/admin/create", summary="创建表情")
async def admin_create_emoji(
    code: str,
    name: str,
    emoji_type: str,
    category: str,
    subcategory: Optional[str] = None,
    description: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    priority: int = 1,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """创建新表情"""
    # 检查代码是否已存在
    existing = db.query(XiaohongshuEmoji).filter(
        XiaohongshuEmoji.code == code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="表情代码已存在")
    
    emoji = XiaohongshuEmoji(
        code=code,
        name=name,
        emoji_type=emoji_type,
        category=category,
        subcategory=subcategory,
        description=description,
        keywords=json.dumps(keywords or [], ensure_ascii=False),
        priority=priority,
        created_by=admin.username
    )
    
    db.add(emoji)
    db.commit()
    db.refresh(emoji)
    
    return {
        "message": "表情创建成功",
        "emoji": {
            "id": emoji.id,
            "code": emoji.code,
            "name": emoji.name
        }
    }


@router.put("/admin/{emoji_id}", summary="更新表情")
async def admin_update_emoji(
    emoji_id: int,
    name: Optional[str] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    description: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    priority: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """更新表情信息"""
    emoji = db.query(XiaohongshuEmoji).filter(
        XiaohongshuEmoji.id == emoji_id
    ).first()
    
    if not emoji:
        raise HTTPException(status_code=404, detail="表情不存在")
    
    if name is not None:
        emoji.name = name
    if category is not None:
        emoji.category = category
    if subcategory is not None:
        emoji.subcategory = subcategory
    if description is not None:
        emoji.description = description
    if keywords is not None:
        emoji.keywords = json.dumps(keywords, ensure_ascii=False)
    if priority is not None:
        emoji.priority = priority
    if status is not None:
        emoji.status = status
    
    emoji.updated_by = admin.username
    emoji.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "表情更新成功"}


@router.delete("/admin/{emoji_id}", summary="删除表情")
async def admin_delete_emoji(
    emoji_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """删除表情"""
    emoji = db.query(XiaohongshuEmoji).filter(
        XiaohongshuEmoji.id == emoji_id
    ).first()
    
    if not emoji:
        raise HTTPException(status_code=404, detail="表情不存在")
    
    # 软删除 - 设置状态为禁用
    emoji.status = 0
    emoji.updated_by = admin.username
    emoji.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "表情删除成功"}


@router.get("/admin/stats", summary="表情使用统计")
async def admin_get_emoji_stats(
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """获取表情使用统计"""
    # 基础统计
    total_emojis = db.query(XiaohongshuEmoji).count()
    active_emojis = db.query(XiaohongshuEmoji).filter(XiaohongshuEmoji.status == 1).count()
    total_usage = db.query(EmojiUsageLog).count()
    
    # 热门表情TOP10
    popular_emojis = db.query(XiaohongshuEmoji).filter(
        XiaohongshuEmoji.status == 1
    ).order_by(XiaohongshuEmoji.usage_count.desc()).limit(10).all()
    
    # 分类统计
    category_stats = db.query(EmojiCategory).filter(
        EmojiCategory.status == 1
    ).all()
    
    return {
        "overview": {
            "total_emojis": total_emojis,
            "active_emojis": active_emojis,
            "total_usage": total_usage
        },
        "popular_emojis": [
            {
                "code": emoji.code,
                "name": emoji.name,
                "usage_count": emoji.usage_count
            }
            for emoji in popular_emojis
        ],
        "category_stats": [
            {
                "name": cat.display_name,
                "emoji_count": cat.emoji_count
            }
            for cat in category_stats
        ]
    }