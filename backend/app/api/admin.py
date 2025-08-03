"""
管理员相关API
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from pydantic import BaseModel
from passlib.context import CryptContext
from functools import wraps

from app.database.connection import get_database
from app.models.database import AdminUser, ProhibitedWord, OriginalWord, HomophoneReplacement, AdminLog
from app.api.auth import get_current_admin

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


# Pydantic模型
class ProhibitedWordCreate(BaseModel):
    word: str
    category: str
    severity: str = "medium"
    description: Optional[str] = None
    is_active: bool = True


class ProhibitedWordUpdate(BaseModel):
    word: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProhibitedWordResponse(BaseModel):
    id: int
    word: str
    category: str
    severity: str
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str


class HomophoneReplacementCreate(BaseModel):
    original_word_id: int
    replacement_word: str
    priority: int = 0
    confidence_score: float = 0.8
    description: Optional[str] = None


class HomophoneReplacementUpdate(BaseModel):
    replacement_word: Optional[str] = None
    priority: Optional[int] = None
    confidence_score: Optional[float] = None
    description: Optional[str] = None


class HomophoneReplacementResponse(BaseModel):
    id: int
    replacement_word: str
    priority: int
    confidence_score: float
    usage_count: int
    description: Optional[str]
    created_at: str
    updated_at: str


class OriginalWordCreate(BaseModel):
    original_word: str
    description: Optional[str] = None


class OriginalWordUpdate(BaseModel):
    original_word: Optional[str] = None
    description: Optional[str] = None


class OriginalWordResponse(BaseModel):
    id: int
    original_word: str
    description: Optional[str]
    created_at: str
    updated_at: str
    replacements: List[HomophoneReplacementResponse] = []


class AdminLogResponse(BaseModel):
    id: int
    admin_username: str
    action: str
    target_type: str
    target_id: Optional[int]
    old_data: Optional[str]
    new_data: Optional[str]
    created_at: str


class AdminUserCreate(BaseModel):
    username: str
    password: str
    email: str
    role: str = "admin"  # admin 或 super_admin
    permissions: Optional[dict] = None


class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[dict] = None
    status: Optional[int] = None


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    permissions: Optional[dict]
    status: int
    last_login_at: Optional[str]
    created_at: str
    updated_at: str


class PasswordResetRequest(BaseModel):
    new_password: str


def require_super_admin(func):
    """装饰器：要求超级管理员权限"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 从kwargs中获取current_admin参数
        current_admin = kwargs.get('current_admin')
        if not current_admin or current_admin.role != 'super_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要超级管理员权限"
            )
        return await func(*args, **kwargs)
    return wrapper


def log_admin_action(db: Session, admin: AdminUser, action: str, target_type: str, target_id: int = None, old_data: dict = None, new_data: dict = None):
    """记录管理员操作日志"""
    log = AdminLog(
        admin_id=admin.id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        old_data=json.dumps(old_data, ensure_ascii=False) if old_data else None,
        new_data=json.dumps(new_data, ensure_ascii=False) if new_data else None
    )
    db.add(log)


# 违禁词管理
@router.get("/prohibited-words", response_model=List[ProhibitedWordResponse])
async def get_prohibited_words(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """获取违禁词列表（支持搜索和分页）"""
    query = db.query(ProhibitedWord)
    
    # 搜索过滤
    if search:
        query = query.filter(ProhibitedWord.word.contains(search))
    
    # 分类过滤
    if category:
        query = query.filter(ProhibitedWord.category == category)
    
    # 严重程度过滤
    if severity:
        risk_level = _convert_severity_to_risk_level(severity)
        query = query.filter(ProhibitedWord.risk_level == risk_level)
    
    # 分页
    offset = (page - 1) * limit
    words = query.order_by(desc(ProhibitedWord.created_at)).offset(offset).limit(limit).all()
    
    return [
        ProhibitedWordResponse(
            id=word.id,
            word=word.word,
            category=word.category,
            severity=_convert_risk_level_to_severity(word.risk_level),
            description=getattr(word, 'description', None),
            is_active=word.status == 1,
            created_at=word.created_at.isoformat(),
            updated_at=word.updated_at.isoformat()
        ) for word in words
    ]


def _convert_risk_level_to_severity(risk_level: int) -> str:
    """转换风险等级到严重程度"""
    mapping = {1: "low", 2: "medium", 3: "high"}
    return mapping.get(risk_level, "medium")


def _convert_severity_to_risk_level(severity: str) -> int:
    """转换严重程度到风险等级"""
    mapping = {"low": 1, "medium": 2, "high": 3}
    return mapping.get(severity, 2)


@router.post("/prohibited-words", response_model=ProhibitedWordResponse)
async def create_prohibited_word(
    word_data: ProhibitedWordCreate,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """创建违禁词"""
    # 检查是否已存在
    existing = db.query(ProhibitedWord).filter(ProhibitedWord.word == word_data.word).first()
    if existing:
        raise HTTPException(status_code=400, detail="该违禁词已存在")
    
    # 创建违禁词
    prohibited_word = ProhibitedWord(
        word=word_data.word,
        category=word_data.category,
        risk_level=_convert_severity_to_risk_level(word_data.severity),
        status=1 if word_data.is_active else 0,
        created_by=current_admin.username
    )
    db.add(prohibited_word)
    db.commit()
    db.refresh(prohibited_word)
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "create", "prohibited_word", 
        prohibited_word.id, None, word_data.dict()
    )
    db.commit()
    
    return ProhibitedWordResponse(
        id=prohibited_word.id,
        word=prohibited_word.word,
        category=prohibited_word.category,
        severity=word_data.severity,
        description=word_data.description,
        is_active=word_data.is_active,
        created_at=prohibited_word.created_at.isoformat(),
        updated_at=prohibited_word.updated_at.isoformat()
    )


@router.put("/prohibited-words/{word_id}", response_model=ProhibitedWordResponse)
async def update_prohibited_word(
    word_id: int,
    word_data: ProhibitedWordUpdate,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """更新违禁词"""
    # 查找违禁词
    prohibited_word = db.query(ProhibitedWord).filter(ProhibitedWord.id == word_id).first()
    if not prohibited_word:
        raise HTTPException(status_code=404, detail="违禁词不存在")
    
    # 保存旧数据用于日志
    old_data = {
        "word": prohibited_word.word,
        "category": prohibited_word.category,
        "risk_level": prohibited_word.risk_level,
        "status": prohibited_word.status
    }
    
    # 更新数据
    if word_data.word is not None:
        prohibited_word.word = word_data.word
    if word_data.category is not None:
        prohibited_word.category = word_data.category
    if word_data.severity is not None:
        prohibited_word.risk_level = _convert_severity_to_risk_level(word_data.severity)
    if word_data.is_active is not None:
        prohibited_word.status = 1 if word_data.is_active else 0
    
    db.commit()
    db.refresh(prohibited_word)
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "update", "prohibited_word", 
        word_id, old_data, word_data.dict(exclude_unset=True)
    )
    db.commit()
    
    return ProhibitedWordResponse(
        id=prohibited_word.id,
        word=prohibited_word.word,
        category=prohibited_word.category,
        severity=_convert_risk_level_to_severity(prohibited_word.risk_level),
        description=word_data.description,
        is_active=prohibited_word.status == 1,
        created_at=prohibited_word.created_at.isoformat(),
        updated_at=prohibited_word.updated_at.isoformat()
    )


@router.delete("/prohibited-words/{word_id}")
async def delete_prohibited_word(
    word_id: int,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """删除违禁词"""
    # 查找违禁词
    prohibited_word = db.query(ProhibitedWord).filter(ProhibitedWord.id == word_id).first()
    if not prohibited_word:
        raise HTTPException(status_code=404, detail="违禁词不存在")
    
    # 记录删除日志
    old_data = {
        "word": prohibited_word.word,
        "category": prohibited_word.category,
        "risk_level": prohibited_word.risk_level
    }
    log_admin_action(
        db, current_admin, "delete", "prohibited_word", 
        word_id, old_data, None
    )
    
    # 删除
    db.delete(prohibited_word)
    db.commit()
    
    return {"message": "删除成功"}


# 原词管理  
@router.get("/original-words", response_model=List[OriginalWordResponse])
async def get_original_words(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """获取原词列表（支持搜索和分页）"""
    query = db.query(OriginalWord).options(
        joinedload(OriginalWord.replacements)
    )
    
    # 搜索过滤
    if search:
        query = query.filter(OriginalWord.word.contains(search))
    
    # 分页
    offset = (page - 1) * limit
    original_words = query.order_by(desc(OriginalWord.created_at)).offset(offset).limit(limit).all()
    
    result = []
    for word in original_words:
        replacements = [
            HomophoneReplacementResponse(
                id=repl.id,
                replacement_word=repl.replacement_word,
                priority=repl.priority,
                confidence_score=repl.confidence_score,
                usage_count=repl.usage_count,
                description=getattr(repl, 'description', None),
                created_at=repl.created_at.isoformat(),
                updated_at=repl.updated_at.isoformat()
            ) for repl in word.replacements if repl.status == 1
        ]
        
        result.append(OriginalWordResponse(
            id=word.id,
            original_word=word.word,
            description=getattr(word, 'description', None),
            created_at=word.created_at.isoformat(),
            updated_at=word.updated_at.isoformat(),
            replacements=replacements
        ))
    
    return result


@router.post("/original-words", response_model=OriginalWordResponse)
async def create_original_word(
    word_data: OriginalWordCreate,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """创建原词"""
    # 检查是否已存在
    existing = db.query(OriginalWord).filter(OriginalWord.word == word_data.original_word).first()
    if existing:
        raise HTTPException(status_code=400, detail="该原词已存在")
    
    # 创建原词
    original_word = OriginalWord(
        word=word_data.original_word,
        status=1,
        created_by=current_admin.username
    )
    db.add(original_word)
    db.commit()
    db.refresh(original_word)
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "create", "original_word", 
        original_word.id, None, word_data.dict()
    )
    db.commit()
    
    return OriginalWordResponse(
        id=original_word.id,
        original_word=original_word.word,
        description=word_data.description,
        created_at=original_word.created_at.isoformat(),
        updated_at=original_word.updated_at.isoformat(),
        replacements=[]
    )


@router.put("/original-words/{word_id}", response_model=OriginalWordResponse)
async def update_original_word(
    word_id: int,
    word_data: OriginalWordUpdate,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """更新原词"""
    # 查找原词
    original_word = db.query(OriginalWord).filter(OriginalWord.id == word_id).first()
    if not original_word:
        raise HTTPException(status_code=404, detail="原词不存在")
    
    # 保存旧数据用于日志
    old_data = {
        "word": original_word.word
    }
    
    # 更新数据
    if word_data.original_word is not None:
        original_word.word = word_data.original_word
    
    db.commit()
    db.refresh(original_word)
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "update", "original_word", 
        word_id, old_data, word_data.dict(exclude_unset=True)
    )
    db.commit()
    
    return OriginalWordResponse(
        id=original_word.id,
        original_word=original_word.word,
        description=word_data.description,
        created_at=original_word.created_at.isoformat(),
        updated_at=original_word.updated_at.isoformat(),
        replacements=[]
    )


@router.delete("/original-words/{word_id}")
async def delete_original_word(
    word_id: int,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """删除原词"""
    # 查找原词
    original_word = db.query(OriginalWord).filter(OriginalWord.id == word_id).first()
    if not original_word:
        raise HTTPException(status_code=404, detail="原词不存在")
    
    # 记录删除日志
    old_data = {
        "word": original_word.word
    }
    log_admin_action(
        db, current_admin, "delete", "original_word", 
        word_id, old_data, None
    )
    
    # 删除相关的谐音词替换
    db.query(HomophoneReplacement).filter(
        HomophoneReplacement.original_word_id == word_id
    ).delete()
    
    # 删除原词
    db.delete(original_word)
    db.commit()
    
    return {"message": "删除成功"}


# 谐音词替换管理
@router.post("/homophone-replacements", response_model=HomophoneReplacementResponse)
async def create_homophone_replacement(
    replacement_data: HomophoneReplacementCreate,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """创建谐音词替换"""
    # 检查原词是否存在
    original_word = db.query(OriginalWord).filter(OriginalWord.id == replacement_data.original_word_id).first()
    if not original_word:
        raise HTTPException(status_code=404, detail="原词不存在")
    
    # 创建谐音词替换
    replacement = HomophoneReplacement(
        original_word_id=replacement_data.original_word_id,
        replacement_word=replacement_data.replacement_word,
        replacement_type="manual",  # 手动创建的类型
        priority=replacement_data.priority,
        confidence_score=replacement_data.confidence_score,
        status=1,
        created_by=current_admin.username
    )
    db.add(replacement)
    db.commit()
    db.refresh(replacement)
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "create", "homophone_replacement", 
        replacement.id, None, replacement_data.dict()
    )
    db.commit()
    
    return HomophoneReplacementResponse(
        id=replacement.id,
        replacement_word=replacement.replacement_word,
        priority=replacement.priority,
        confidence_score=replacement.confidence_score,
        usage_count=replacement.usage_count,
        description=replacement_data.description,
        created_at=replacement.created_at.isoformat(),
        updated_at=replacement.updated_at.isoformat()
    )


@router.put("/homophone-replacements/{replacement_id}", response_model=HomophoneReplacementResponse)
async def update_homophone_replacement(
    replacement_id: int,
    replacement_data: HomophoneReplacementUpdate,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """更新谐音词替换"""
    # 查找谐音词替换
    replacement = db.query(HomophoneReplacement).filter(HomophoneReplacement.id == replacement_id).first()
    if not replacement:
        raise HTTPException(status_code=404, detail="谐音词替换不存在")
    
    # 保存旧数据用于日志
    old_data = {
        "replacement_word": replacement.replacement_word,
        "priority": replacement.priority,
        "confidence_score": replacement.confidence_score
    }
    
    # 更新数据
    if replacement_data.replacement_word is not None:
        replacement.replacement_word = replacement_data.replacement_word
    if replacement_data.priority is not None:
        replacement.priority = replacement_data.priority
    if replacement_data.confidence_score is not None:
        replacement.confidence_score = replacement_data.confidence_score
    
    db.commit()
    db.refresh(replacement)
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "update", "homophone_replacement", 
        replacement_id, old_data, replacement_data.dict(exclude_unset=True)
    )
    db.commit()
    
    return HomophoneReplacementResponse(
        id=replacement.id,
        replacement_word=replacement.replacement_word,
        priority=replacement.priority,
        confidence_score=replacement.confidence_score,
        usage_count=replacement.usage_count,
        description=replacement_data.description,
        created_at=replacement.created_at.isoformat(),
        updated_at=replacement.updated_at.isoformat()
    )


@router.delete("/homophone-replacements/{replacement_id}")
async def delete_homophone_replacement(
    replacement_id: int,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """删除谐音词替换"""
    # 查找谐音词替换
    replacement = db.query(HomophoneReplacement).filter(HomophoneReplacement.id == replacement_id).first()
    if not replacement:
        raise HTTPException(status_code=404, detail="谐音词替换不存在")
    
    # 记录删除日志
    old_data = {
        "replacement_word": replacement.replacement_word,
        "original_word_id": replacement.original_word_id
    }
    log_admin_action(
        db, current_admin, "delete", "homophone_replacement", 
        replacement_id, old_data, None
    )
    
    # 删除
    db.delete(replacement)
    db.commit()
    
    return {"message": "删除成功"}


# 管理员日志管理
@router.get("/logs", response_model=List[AdminLogResponse])
async def get_admin_logs(
    page: int = 1,
    limit: int = 50,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    admin_username: Optional[str] = None,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """获取管理员操作日志"""
    query = db.query(AdminLog).join(AdminUser, AdminLog.admin_id == AdminUser.id)
    
    # 过滤条件
    if action:
        query = query.filter(AdminLog.action == action)
    if target_type:
        query = query.filter(AdminLog.target_type == target_type)
    if admin_username:
        query = query.filter(AdminUser.username.contains(admin_username))
    
    # 分页
    offset = (page - 1) * limit
    logs = query.order_by(desc(AdminLog.created_at)).offset(offset).limit(limit).all()
    
    return [
        AdminLogResponse(
            id=log.id,
            admin_username=log.admin.username,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            old_data=log.old_data,
            new_data=log.new_data,
            created_at=log.created_at.isoformat()
        ) for log in logs
    ]


@router.get("/stats/summary")
async def get_admin_stats_summary(
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """获取管理员统计概要"""
    prohibited_words_count = db.query(ProhibitedWord).filter(ProhibitedWord.status == 1).count()
    original_words_count = db.query(OriginalWord).filter(OriginalWord.status == 1).count()
    homophone_replacements_count = db.query(HomophoneReplacement).filter(HomophoneReplacement.status == 1).count()
    admin_logs_count = db.query(AdminLog).count()
    
    return {
        "prohibited_words_count": prohibited_words_count,
        "original_words_count": original_words_count,
        "homophone_replacements_count": homophone_replacements_count,
        "admin_logs_count": admin_logs_count
    }


# 管理员账号管理
@router.get("/users", response_model=List[AdminUserResponse])
@require_super_admin
async def get_admin_users(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """获取管理员列表（仅超级管理员）"""
    query = db.query(AdminUser)
    
    # 搜索过滤
    if search:
        query = query.filter(
            (AdminUser.username.contains(search)) |
            (AdminUser.email.contains(search))
        )
    
    # 角色过滤
    if role:
        query = query.filter(AdminUser.role == role)
    
    # 分页
    offset = (page - 1) * limit
    users = query.order_by(desc(AdminUser.created_at)).offset(offset).limit(limit).all()
    
    return [
        AdminUserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            permissions=json.loads(user.permissions) if user.permissions else None,
            status=user.status,
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        ) for user in users
    ]


@router.post("/users", response_model=AdminUserResponse)
@require_super_admin
async def create_admin_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """创建新管理员账号（仅超级管理员）"""
    # 检查用户名是否已存在
    existing_user = db.query(AdminUser).filter(
        (AdminUser.username == user_data.username) |
        (AdminUser.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="用户名或邮箱已存在"
        )
    
    # 设置默认权限
    if not user_data.permissions:
        if user_data.role == "super_admin":
            default_permissions = {
                "prohibited_words": {"create": True, "read": True, "update": True, "delete": True},
                "homophone_words": {"create": True, "read": True, "update": True, "delete": True},
                "user_management": {"create": True, "read": True, "update": True, "delete": True},
                "system_settings": {"read": True, "update": True}
            }
        else:  # admin
            default_permissions = {
                "prohibited_words": {"create": True, "read": True, "update": True, "delete": False},
                "homophone_words": {"create": True, "read": True, "update": True, "delete": False},
                "user_management": {"create": False, "read": False, "update": False, "delete": False},
                "system_settings": {"read": False, "update": False}
            }
    else:
        default_permissions = user_data.permissions
    
    # 创建新管理员
    new_admin = AdminUser(
        username=user_data.username,
        password_hash=pwd_context.hash(user_data.password),
        email=user_data.email,
        role=user_data.role,
        permissions=json.dumps(default_permissions, ensure_ascii=False),
        status=1
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "create", "admin_user",
        new_admin.id, None, {
            "username": user_data.username,
            "email": user_data.email,
            "role": user_data.role
        }
    )
    db.commit()
    
    return AdminUserResponse(
        id=new_admin.id,
        username=new_admin.username,
        email=new_admin.email,
        role=new_admin.role,
        permissions=default_permissions,
        status=new_admin.status,
        last_login_at=None,
        created_at=new_admin.created_at.isoformat(),
        updated_at=new_admin.updated_at.isoformat()
    )


@router.post("/users/{user_id}/reset-password")
@require_super_admin
async def reset_admin_password(
    user_id: int,
    password_data: PasswordResetRequest,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """重置管理员密码（仅超级管理员）"""
    # 查找目标用户
    target_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="管理员不存在")
    
    # 更新密码
    target_user.password_hash = pwd_context.hash(password_data.new_password)
    db.commit()
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "reset_password", "admin_user",
        user_id, None, {"action": "password_reset"}
    )
    db.commit()
    
    return {"message": "密码重置成功"}


@router.put("/users/{user_id}/status")
@require_super_admin
async def update_admin_status(
    user_id: int,
    status: int,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """启用/禁用管理员账号（仅超级管理员）"""
    # 查找目标用户
    target_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="管理员不存在")
    
    # 不能禁用自己
    if target_user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的状态")
    
    old_status = target_user.status
    target_user.status = status
    db.commit()
    
    # 记录操作日志
    log_admin_action(
        db, current_admin, "update_status", "admin_user",
        user_id, {"status": old_status}, {"status": status}
    )
    db.commit()
    
    action = "启用" if status == 1 else "禁用"
    return {"message": f"管理员账号{action}成功"}


@router.delete("/users/{user_id}")
@require_super_admin
async def delete_admin_user(
    user_id: int,
    db: Session = Depends(get_database),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """删除管理员账号（仅超级管理员）"""
    try:
        print(f"开始删除用户 ID: {user_id}")
        
        # 查找目标用户
        target_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not target_user:
            print(f"用户 {user_id} 不存在")
            raise HTTPException(status_code=404, detail="管理员不存在")
        
        print(f"找到目标用户: {target_user.username}, 角色: {target_user.role}")
        
        # 不能删除自己
        if target_user.id == current_admin.id:
            print("尝试删除自己的账号")
            raise HTTPException(status_code=400, detail="不能删除自己的账号")
        
        # 不能删除超级管理员
        if target_user.role == "super_admin":
            print("尝试删除超级管理员账号")
            raise HTTPException(status_code=400, detail="不能删除超级管理员账号")
        
        # 记录操作日志（在删除前记录）
        try:
            log_admin_action(
                db, current_admin, "delete", "admin_user",
                user_id, {
                    "username": target_user.username,
                    "email": target_user.email,
                    "role": target_user.role
                }, None
            )
            print("操作日志记录成功")
        except Exception as e:
            print(f"日志记录失败，但继续删除操作: {e}")
        
        # 先删除该用户的相关日志记录
        print("删除用户相关的日志记录...")
        db.query(AdminLog).filter(AdminLog.admin_id == user_id).delete()
        
        # 删除用户
        print("开始删除用户...")
        db.delete(target_user)
        db.commit()
        print("用户删除成功")
        
        return {"message": "管理员账号删除成功"}
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        print(f"删除用户时发生未预期错误: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")