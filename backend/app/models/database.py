"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class AdminUser(Base):
    """管理员用户表"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    role = Column(String(20), nullable=False, default="admin")
    permissions = Column(Text)  # JSON格式权限配置
    status = Column(Integer, default=1)  # 1-启用, 0-禁用
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联操作日志
    logs = relationship("AdminLog", back_populates="admin")


class ProhibitedWord(Base):
    """违禁词表"""
    __tablename__ = "prohibited_words"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    risk_level = Column(Integer, nullable=False)  # 1-低, 2-中, 3-高
    status = Column(Integer, default=1)  # 1-启用, 0-禁用
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OriginalWord(Base):
    """原词表"""
    __tablename__ = "original_words"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
    status = Column(Integer, default=1)
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联谐音词
    replacements = relationship("HomophoneReplacement", back_populates="original")


class HomophoneReplacement(Base):
    """谐音词替换表"""
    __tablename__ = "homophone_replacements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_word_id = Column(Integer, ForeignKey("original_words.id"), nullable=False)
    replacement_word = Column(String(100), nullable=False)
    replacement_type = Column(String(20), nullable=False)  # 同音字、形近字等
    priority = Column(Integer, default=0)  # 1-百分百推荐, 0-随机匹配
    confidence_score = Column(Float, default=0.8)
    usage_count = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联原词
    original = relationship("OriginalWord", back_populates="replacements")


class UserContentHistory(Base):
    """用户内容历史表"""
    __tablename__ = "user_content_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_session = Column(String(100))
    original_content = Column(Text, nullable=False)
    optimized_content = Column(Text)
    detected_issues = Column(Text)  # JSON格式
    applied_optimizations = Column(Text)  # JSON格式
    content_score_before = Column(Integer)
    content_score_after = Column(Integer)
    processing_time = Column(Float)
    is_optimized = Column(Integer, default=0)  # 是否已优化
    created_at = Column(DateTime, default=datetime.utcnow)


class AdminLog(Base):
    """操作日志表"""
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer)
    old_data = Column(Text)  # JSON格式
    new_data = Column(Text)  # JSON格式
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联管理员
    admin = relationship("AdminUser", back_populates="logs")


class SystemSetting(Base):
    """系统配置表"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    description = Column(Text)
    updated_by = Column(String(50))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class XiaohongshuEmoji(Base):
    """小红书表情包表"""
    __tablename__ = "xiaohongshu_emojis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)    # [鄙视R] [开心R] [扯脸H]
    name = Column(String(50), nullable=False)                 # 鄙视、开心、扯脸
    emoji_type = Column(String(5), nullable=False)           # R系列、H系列
    image_url = Column(String(500))                           # 小红书CDN图片链接
    preview_image = Column(String(500))                       # 本地预览图片路径
    category = Column(String(50), nullable=False)            # 表情分类
    subcategory = Column(String(50))                          # 子分类
    description = Column(Text)                                # 表情描述和使用场景
    keywords = Column(Text)                                   # 关键词（JSON格式）
    usage_count = Column(Integer, default=0)                 # 使用次数统计
    priority = Column(Integer, default=1)                    # 推荐优先级 1-5
    is_verified = Column(Integer, default=0)                 # 是否验证有效 1-已验证 0-未验证
    status = Column(Integer, default=1)                      # 1-启用 0-禁用
    created_by = Column(String(50))                          # 创建者
    updated_by = Column(String(50))                          # 更新者
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmojiCategory(Base):
    """表情分类表"""
    __tablename__ = "emoji_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)    # 分类名称
    display_name = Column(String(100), nullable=False)       # 显示名称
    description = Column(Text)                                # 分类描述
    icon = Column(String(100))                                # 分类图标
    sort_order = Column(Integer, default=0)                  # 显示顺序
    emoji_count = Column(Integer, default=0)                 # 表情数量
    status = Column(Integer, default=1)                      # 1-启用 0-禁用
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmojiUsageLog(Base):
    """表情使用日志表"""
    __tablename__ = "emoji_usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    emoji_id = Column(Integer, ForeignKey("xiaohongshu_emojis.id"), nullable=False)
    user_session = Column(String(100))                       # 用户会话
    content_id = Column(Integer, ForeignKey("user_content_history.id"))  # 关联内容
    usage_type = Column(String(20), nullable=False)         # manual-手动选择 auto-智能插入
    position = Column(Integer)                               # 插入位置
    context = Column(Text)                                   # 使用上下文
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联表情
    emoji = relationship("XiaohongshuEmoji")
    # 关联内容
    content = relationship("UserContentHistory")


class WhitelistPattern(Base):
    """白名单模式表"""
    __tablename__ = "whitelist_patterns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prohibited_word = Column(String(100), nullable=False, comment="对应的违禁词")
    pattern = Column(String(500), nullable=False, comment="白名单正则模式")
    description = Column(String(200), comment="模式描述")
    category = Column(String(50), comment="模式分类")
    example = Column(String(200), comment="示例文本")
    is_active = Column(Integer, default=1, comment="是否启用")
    priority = Column(Integer, default=1, comment="优先级")
    created_by = Column(String(50), comment="创建者")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)