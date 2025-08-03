# 小红书内容检查和优化工具 - 详细设计文档

## 1. 项目背景与目标

### 1.1 项目背景
小红书作为生活方式分享平台，对内容有严格的审核机制。用户经常面临以下问题：
- 内容因违禁词被限流或删除
- 不知道如何优化内容结构提高曝光
- 需要手动查找和替换敏感词汇
- 缺乏专业的内容优化指导

### 1.2 项目目标
开发一个智能化的内容检查和优化工具，帮助用户：
- 自动检测和替换违禁词
- 优化内容结构提高流量
- 提供专业的内容优化建议
- 提升内容质量和通过率

## 2. 功能需求分析

### 2.1 核心功能

#### 2.1.1 违禁词检测
- **功能描述**: 扫描文本中的违禁词汇
- **检测范围**: 
  - 政治敏感词
  - 色情低俗词汇
  - 暴力血腥用词
  - 虚假宣传词汇
  - 医疗保健违规词
  - 金融投资风险词
  - 品牌侵权词汇
- **检测方式**: 
  - 精确匹配
  - 模糊匹配（处理变形词）
  - 语义匹配（上下文分析）

#### 2.1.2 谐音词智能替换
- **替换策略**:
  - 保持语义完整性
  - 维持阅读流畅性
  - 确保替换词的合理性
- **替换方法**:
  - 同音字替换：例如 "减肥" → "减费"
  - 形近字替换：例如 "药物" → "要物"
  - 符号分隔：例如 "广告" → "广*告"
  - 英文混用：例如 "推广" → "推guang"
  - 表情符号：例如 "赚钱" → "赚💰"

#### 2.1.3 内容结构优化
- **标题优化**:
  - 关键词密度分析
  - 标题长度建议
  - 热门标签推荐
  - 话题热度分析
- **正文优化**:
  - 段落结构调整
  - 关键词分布优化
  - 可读性分析
  - 互动元素建议
- **标签优化**:
  - 热门标签推荐
  - 标签搭配建议
  - 标签热度分析

### 2.2 辅助功能

#### 2.2.1 内容分析报告
- 违禁词风险评估
- 内容质量评分
- 优化建议清单
- 预期流量评估

#### 2.2.2 数据管理
- 违禁词库管理
- 谐音词库维护
- 用户历史记录
- 优化效果统计

## 3. 技术架构设计

### 3.1 本地化Web前后端架构

```
┌─────────────────────────────────────────────────────────────┐
│                    本地Web应用系统                           │
├─────────────────────────┬───────────────────────────────────┤
│       前端Web应用       │          后端API服务             │
│                         │                                   │
│ ┌─────────────────────┐ │ ┌───────────────────────────────┐ │
│ │   Vue.js 3 SPA      │ │ │      FastAPI服务器           │ │
│ │ - 响应式界面        │ │ │ - RESTful API接口             │ │
│ │ - 实时内容检测      │◄┼►│ - 内容分析引擎                │ │
│ │ - 结果可视化        │ │ │ - 违禁词检测器                │ │
│ │ - 用户交互          │ │ │ - 谐音词生成器                │ │
│ │                     │ │ │ - 结构优化器                  │ │
│ └─────────────────────┘ │ └───────────────────────────────┘ │
│                         │                                   │
│ 端口: 3000              │ 端口: 8000                        │
└─────────────────────────┴───────────────────────────────────┘
                           │
                    ┌─────────────────┐
                    │   本地数据层    │
                    │                 │
                    │ - SQLite数据库  │
                    │ - 违禁词库      │
                    │ - 谐音词库      │
                    │ - 配置文件      │
                    │ - 日志文件      │
                    └─────────────────┘
```

### 3.2 技术栈选择

#### 3.2.1 Web技术栈选择

**前端技术栈**
- **框架**: Vue.js 3 + TypeScript
- **构建工具**: Vite (快速开发和构建)
- **UI框架**: Headless UI + 自定义组件
- **样式方案**: SCSS + CSS变量 + 现代化设计系统
- **图标库**: Lucide Icons (轻量级SVG图标)
- **状态管理**: Pinia (轻量级状态管理)
- **HTTP客户端**: Axios (API请求)
- **动画方案**: CSS Transitions + 微妙的动画效果
- **工具链**: ESLint + Prettier + Husky

**后端技术栈**
- **框架**: FastAPI (高性能Python Web框架)
- **数据库**: SQLite + SQLAlchemy ORM
- **文本处理**: 
  - jieba (中文分词)
  - pypinyin (拼音处理)
  - 自研算法库
- **异步支持**: asyncio + uvicorn
- **数据验证**: Pydantic

#### 3.2.2 本地化Web优势
- **无需安装**: 直接通过浏览器访问
- **跨平台**: 支持所有现代浏览器
- **响应式**: 自适应不同屏幕尺寸
- **离线运行**: 本地服务器，无需联网
- **易于维护**: 前后端分离，便于开发和调试
- **数据安全**: 所有数据处理在本地进行

#### 3.2.3 部署和启动方案
- **一键启动**: 双击运行脚本启动服务
- **自动打开**: 启动后自动打开浏览器
- **端口检测**: 自动检测可用端口
- **绿色便携**: 整个项目文件夹即为完整应用
- **停止服务**: 关闭命令行窗口即停止服务

### 3.3 数据库设计

#### 3.3.1 完整的SQLite数据库设计

**管理员用户表 (admin_users)**
```sql
CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT NOT NULL DEFAULT 'admin',    -- admin, super_admin
    permissions TEXT,                      -- JSON格式权限配置
    status INTEGER DEFAULT 1,             -- 1-启用, 0-禁用
    last_login_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**违禁词表 (prohibited_words)**
```sql
CREATE TABLE prohibited_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,               -- 政治、医疗、虚假宣传等
    risk_level INTEGER NOT NULL,          -- 1-低, 2-中, 3-高
    status INTEGER DEFAULT 1,             -- 1-启用, 0-禁用
    created_by TEXT,                      -- 创建人
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**原词表 (original_words)**
```sql
CREATE TABLE original_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    category TEXT,
    status INTEGER DEFAULT 1,
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**谐音词替换表 (homophone_replacements)**
```sql
CREATE TABLE homophone_replacements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_word_id INTEGER NOT NULL,
    replacement_word TEXT NOT NULL,
    replacement_type TEXT NOT NULL,       -- 同音字、形近字、符号分隔等
    priority INTEGER DEFAULT 0,          -- 优先级：1-百分百推荐, 0-随机匹配
    confidence_score REAL DEFAULT 0.8,   -- 替换可信度
    usage_count INTEGER DEFAULT 0,       -- 使用次数统计
    status INTEGER DEFAULT 1,            -- 1-启用, 0-禁用
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_word_id) REFERENCES original_words(id)
);
```

**用户内容历史表 (user_content_history)**
```sql
CREATE TABLE user_content_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_session TEXT,                    -- 用户会话标识
    original_content TEXT NOT NULL,
    optimized_content TEXT,
    detected_issues TEXT,                 -- JSON格式存储检测问题
    applied_optimizations TEXT,           -- JSON格式存储应用的优化
    content_score_before INTEGER,
    content_score_after INTEGER,
    processing_time REAL,                 -- 处理耗时（秒）
    is_optimized INTEGER DEFAULT 0,       -- 是否已优化（影响词库更新策略）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**操作日志表 (admin_logs)**
```sql
CREATE TABLE admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,                 -- 操作类型
    target_type TEXT NOT NULL,            -- 操作对象类型
    target_id INTEGER,                    -- 操作对象ID
    old_data TEXT,                        -- 修改前数据（JSON）
    new_data TEXT,                        -- 修改后数据（JSON）
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admin_users(id)
);
```

## 4. 核心算法设计

### 4.1 违禁词检测算法

#### 4.1.1 多层检测机制
1. **基础字符串匹配**: 使用Aho-Corasick算法进行高效多模式匹配
2. **变形词检测**: 处理特殊字符、数字、英文混用的变形词
3. **语义相似度检测**: 使用BERT等预训练模型进行语义匹配
4. **上下文分析**: 结合上下文判断词汇的真实含义

#### 4.1.2 算法流程
```python
def detect_prohibited_words(text: str) -> List[ProhibitedWordResult]:
    results = []
    
    # 1. 预处理文本
    cleaned_text = preprocess_text(text)
    
    # 2. 基础匹配
    basic_matches = aho_corasick_search(cleaned_text)
    results.extend(basic_matches)
    
    # 3. 变形词检测
    variant_matches = detect_variant_words(cleaned_text)
    results.extend(variant_matches)
    
    # 4. 语义匹配
    semantic_matches = semantic_similarity_search(cleaned_text)
    results.extend(semantic_matches)
    
    # 5. 去重和排序
    return deduplicate_and_rank(results)
```

### 4.2 谐音词生成算法

#### 4.2.1 生成策略
1. **拼音相似度**: 基于拼音的音韵相似度计算
2. **字形相似度**: 基于汉字结构的相似度计算
3. **语义保持度**: 确保替换后语义基本不变
4. **使用频率**: 优先选择常用的替换词

#### 4.2.2 评分机制
```python
def calculate_replacement_score(original: str, replacement: str) -> float:
    # 拼音相似度 (40%)
    pinyin_score = calculate_pinyin_similarity(original, replacement)
    
    # 字形相似度 (30%)
    shape_score = calculate_shape_similarity(original, replacement)
    
    # 语义保持度 (20%)
    semantic_score = calculate_semantic_preservation(original, replacement)
    
    # 使用频率 (10%)
    frequency_score = get_usage_frequency_score(replacement)
    
    total_score = (pinyin_score * 0.4 + 
                   shape_score * 0.3 + 
                   semantic_score * 0.2 + 
                   frequency_score * 0.1)
    
    return total_score
```

### 4.3 内容结构分析算法

#### 4.3.1 结构要素分析
- **标题分析**: 长度、关键词密度、情感色彩
- **段落分析**: 段落数量、长度分布、逻辑结构
- **标签分析**: 标签数量、热度、相关性
- **互动元素**: 问句、Call-to-Action、表情使用

#### 4.3.2 优化建议生成
基于平台数据和最佳实践，生成针对性的优化建议。

## 5. 现代化用户界面设计

### 5.1 现代化设计理念

#### 5.1.1 设计原则
- **极简主义**: 内容优先，减少视觉噪音
- **功能性**: 每个元素都有明确目的
- **优雅感**: 微妙的细节，自然的过渡
- **可用性**: 直观易懂，降低学习成本

#### 5.1.2 现代化色彩体系
```scss
// 主色调 - 更加内敛优雅
$primary: #2563eb;        // 蓝色主调
$primary-hover: #1d4ed8;  // 悬停状态
$accent: #6366f1;         // 紫色点缀

// 语义色彩 - 自然柔和
$success: #10b981;        // 绿色
$warning: #f59e0b;        // 橙色  
$danger: #ef4444;         // 红色
$info: #3b82f6;           // 蓝色

// 中性色系 - 现代感
$gray-50: #f9fafb;
$gray-100: #f3f4f6;
$gray-200: #e5e7eb;
$gray-300: #d1d5db;
$gray-400: #9ca3af;
$gray-500: #6b7280;
$gray-600: #4b5563;
$gray-700: #374151;
$gray-800: #1f2937;
$gray-900: #111827;

// 背景色 - 简洁清爽
$bg-light: #ffffff;
$bg-light-secondary: #f8fafc;
$bg-dark: #0f172a;
$bg-dark-secondary: #1e293b;
```

### 5.2 主界面布局设计

#### 5.2.1 现代化布局结构 (参考Notion/Linear风格)
```html
<div class="app-container">
  <!-- 简洁顶部导航 -->
  <header class="top-nav">
    <div class="nav-left">
      <div class="logo">
        <span class="logo-icon">✨</span>
        <span class="logo-text">小红书内容优化</span>
      </div>
    </div>
    <div class="nav-right">
      <button class="nav-btn">历史记录</button>
      <button class="nav-btn">设置</button>
    </div>
  </header>

  <!-- 主工作区 - 聚焦内容编辑 -->
  <main class="main-content">
    <div class="content-wrapper">
      
      <!-- 主编辑区域 -->
      <section class="editor-section">
        <div class="editor-header">
          <h2 class="section-title">内容编辑器</h2>
          <div class="editor-stats">
            <span class="char-count">0 / 1000</span>
            <div class="status-indicator success">
              <span class="status-dot"></span>
              <span>准备就绪</span>
            </div>
          </div>
        </div>
        
        <div class="editor-container">
          <textarea 
            class="main-editor" 
            placeholder="在这里输入您的小红书内容..."
            spellcheck="false">
          </textarea>
          
          <!-- 工具栏 -->
          <div class="editor-toolbar">
            <div class="toolbar-left">
              <button class="tool-btn">
                <i class="icon-upload"></i>
                <span>导入</span>
              </button>
              <button class="tool-btn">
                <i class="icon-paste"></i>
                <span>粘贴</span>
              </button>
            </div>
            <div class="toolbar-right">
              <button class="btn btn-secondary">
                <i class="icon-search"></i>
                <span>检测内容</span>
              </button>
              <button class="btn btn-primary">
                <i class="icon-wand"></i>
                <span>智能优化</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 侧边检测面板 -->
      <aside class="detection-sidebar">
        <div class="sidebar-header">
          <h3>检测结果</h3>
          <button class="collapse-btn">
            <i class="icon-chevron-right"></i>
          </button>
        </div>
        
        <div class="detection-cards">
          <!-- 违禁词检测卡片 -->
          <div class="detection-card">
            <div class="card-header">
              <div class="card-icon warning">
                <i class="icon-alert-triangle"></i>
              </div>
              <div class="card-info">
                <h4>违禁词检测</h4>
                <span class="card-status">发现 2 个问题</span>
              </div>
            </div>
            <div class="card-content">
              <div class="issue-list">
                <!-- 问题列表 -->
              </div>
            </div>
          </div>

          <!-- 结构优化卡片 -->
          <div class="detection-card">
            <div class="card-header">
              <div class="card-icon info">
                <i class="icon-target"></i>
              </div>
              <div class="card-info">
                <h4>结构分析</h4>
                <span class="score">85分</span>
              </div>
            </div>
            <div class="card-content">
              <!-- 分析结果 -->
            </div>
          </div>

          <!-- 优化建议卡片 -->
          <div class="detection-card">
            <div class="card-header">
              <div class="card-icon success">
                <i class="icon-lightbulb"></i>
              </div>
              <div class="card-info">
                <h4>优化建议</h4>
                <span class="ai-tag">AI生成</span>
              </div>
            </div>
            <div class="card-content">
              <!-- 建议内容 -->
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- 底部结果区域 -->
    <section class="results-section">
      <div class="results-header">
        <h3>优化后内容</h3>
        <div class="results-actions">
          <button class="btn btn-outline">
            <i class="icon-copy"></i>
            <span>复制</span>
          </button>
          <button class="btn btn-outline">
            <i class="icon-download"></i>
            <span>导出</span>
          </button>
        </div>
      </div>
      <div class="results-content">
        <div class="optimized-text">
          <!-- 优化后的内容展示 -->
        </div>
      </div>
    </section>
  </main>
</div>
```

#### 5.2.2 现代化样式设计
```scss
// 全局容器 - 简洁清爽
.app-container {
  background: var(--bg-primary);
  min-height: 100vh;
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

// 顶部导航 - 简约风格
.top-nav {
  height: 64px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  
  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    font-size: 16px;
  }
  
  .nav-btn {
    padding: 8px 16px;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.2s ease;
    
    &:hover {
      background: var(--hover-bg);
    }
  }
}

// 主编辑器 - 内容优先
.main-editor {
  width: 100%;
  min-height: 400px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  font-size: 16px;
  line-height: 1.6;
  background: var(--bg-primary);
  color: var(--text-primary);
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-10);
  }
}

// 现代化按钮设计
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 6px;
  border: 1px solid transparent;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &.btn-primary {
    background: var(--primary);
    color: white;
    
    &:hover {
      background: var(--primary-hover);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px var(--primary-20);
    }
  }
  
  &.btn-secondary {
    background: var(--gray-100);
    color: var(--gray-700);
    
    &:hover {
      background: var(--gray-200);
    }
  }
  
  &.btn-outline {
    border-color: var(--border-color);
    background: transparent;
    
    &:hover {
      background: var(--hover-bg);
    }
  }
}

// 检测卡片 - 轻量设计
.detection-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  transition: border-color 0.2s ease;
  
  &:hover {
    border-color: var(--primary-30);
  }
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    
    .card-icon {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      
      &.warning { background: var(--warning-10); color: var(--warning); }
      &.info { background: var(--info-10); color: var(--info); }
      &.success { background: var(--success-10); color: var(--success); }
    }
  }
}

// 状态指示器
.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  
  &.success {
    background: var(--success-10);
    color: var(--success);
  }
  
  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
  }
}

// 响应式布局
.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    .detection-sidebar {
      order: -1;
    }
  }
}

// CSS变量定义
:root {
  // 颜色系统
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --primary-10: rgba(37, 99, 235, 0.1);
  --primary-20: rgba(37, 99, 235, 0.2);
  --primary-30: rgba(37, 99, 235, 0.3);
  
  --success: #10b981;
  --success-10: rgba(16, 185, 129, 0.1);
  --warning: #f59e0b;
  --warning-10: rgba(245, 158, 11, 0.1);
  --info: #3b82f6;
  --info-10: rgba(59, 130, 246, 0.1);
  
  // 背景和边框
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --border-color: #e5e7eb;
  --hover-bg: #f3f4f6;
  
  // 文字颜色
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
}

// 深色主题
[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --border-color: #334155;
  --hover-bg: #1e293b;
  
  --text-primary: #f1f5f9;
  --text-secondary: #cbd5e1;
  --text-muted: #64748b;
}
```

### 5.3 现代化交互设计

#### 5.3.1 微妙而有意义的动画
```scss
// 自然的过渡动画
.smooth-transition {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

// 按钮交互 - 轻微提升
.btn:hover {
  transform: translateY(-1px);
  transition: transform 0.15s ease;
}

// 卡片悬停 - 边框变化
.detection-card:hover {
  border-color: var(--primary-30);
  transition: border-color 0.2s ease;
}

// 输入焦点 - 柔和发光
.main-editor:focus {
  box-shadow: 0 0 0 3px var(--primary-10);
  transition: box-shadow 0.2s ease;
}
```

#### 5.3.2 实时状态反馈
- **输入状态**: 字符计数实时更新，状态点颜色变化
- **检测进行中**: 简洁的线性进度指示器
- **结果展示**: 内容平滑显示，避免突兀的弹出

#### 5.3.3 现代化加载状态
```scss
// 骨架屏加载
.skeleton {
  background: linear-gradient(90deg, 
    var(--gray-200) 25%, 
    var(--gray-100) 50%, 
    var(--gray-200) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

// 简洁的旋转加载
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--gray-300);
  border-top: 2px solid var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### 5.4 现代化响应式设计

#### 5.4.1 桌面端布局 (1024px+)
```scss
.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
```
- 主编辑区 + 侧边检测面板
- 充分利用大屏幕空间
- 信息密度适中，避免过于分散

#### 5.4.2 平板端布局 (768px - 1023px)
```scss
@media (max-width: 1023px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px;
  }
  
  .detection-sidebar {
    order: -1; // 检测结果移到上方
  }
}
```
- 垂直堆叠布局
- 检测结果置顶显示
- 保持内容的可读性

#### 5.4.3 移动端布局 (320px - 767px)
```scss
@media (max-width: 767px) {
  .top-nav {
    padding: 0 16px;
    
    .logo-text {
      display: none; // 隐藏文字，仅显示图标
    }
  }
  
  .main-editor {
    min-height: 300px;
    font-size: 16px; // 防止iOS缩放
  }
  
  .editor-toolbar {
    flex-direction: column;
    gap: 12px;
  }
}
```
- 单栏设计，内容优先
- 触摸友好的按钮尺寸
- 优化输入体验

### 5.5 优雅的主题系统

#### 5.5.1 浅色主题 (默认)
```scss
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --text-primary: #1f2937;
  --border-color: #e5e7eb;
}
```
- 清爽的白色背景
- 高对比度文字
- 现代化边框设计

#### 5.5.2 深色主题
```scss
[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f1f5f9;
  --border-color: #334155;
}
```
- 深蓝色调背景
- 护眼的文字颜色
- 保持良好对比度

#### 5.5.3 主题切换实现
```javascript
// 主题切换逻辑
const themeToggle = () => {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}

// 系统主题检测
const detectSystemTheme = () => {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}
```

### 5.6 可访问性设计

#### 5.6.1 键盘导航支持
```scss
// 焦点指示器
*:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  border-radius: 4px;
}

// 跳过链接
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary);
  color: white;
  padding: 8px;
  text-decoration: none;
  
  &:focus {
    top: 6px;
  }
}
```

#### 5.6.2 语义化HTML
- 使用正确的HTML标签结构
- 为图标添加适当的aria-label
- 保证屏幕阅读器的可访问性

## 6. 本地化Web开发实施计划

### 6.1 项目文件结构
```
xiaohongshu_content_modify/
├── backend/                    # 后端FastAPI服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── models/            # 数据模型
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心算法
│   │   ├── database/          # 数据库相关
│   │   └── utils/             # 工具函数
│   ├── data/                  # 数据文件
│   │   ├── prohibited_words.json
│   │   ├── homophone_words.json
│   │   └── content_templates.json
│   ├── requirements.txt       # Python依赖
│   └── run.py                 # 启动脚本
├── frontend/                   # 前端Vue.js应用
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   ├── views/             # 页面视图
│   │   ├── store/             # Pinia状态管理
│   │   ├── api/               # API调用
│   │   └── utils/             # 工具函数
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── start.bat                  # Windows启动脚本
├── start.sh                   # Linux/Mac启动脚本
└── README.md                  # 使用说明
```

### 6.2 开发阶段划分

#### 第一阶段：后端API开发 (2-3周)
- FastAPI项目结构搭建
- SQLite数据库设计和初始化
- 违禁词检测API接口
- 谐音词替换API接口
- 内容分析API接口
- 预置数据准备和导入

#### 第二阶段：前端界面开发 (2-3周)
- Vue.js项目初始化
- 主界面组件开发
- 内容输入和结果展示组件
- API集成和状态管理
- 响应式设计和样式优化

#### 第三阶段：集成和优化 (1-2周)
- 前后端联调测试
- 性能优化和错误处理
- 启动脚本编写
- 用户文档和部署指南
- 跨平台兼容性测试

### 6.3 启动方案设计

#### 6.3.1 自动启动脚本

**Windows启动脚本 (start.bat)**
```batch
@echo off
echo 正在启动小红书内容优化工具...
cd backend
start "后端服务" python run.py
timeout /t 3 /nobreak > nul
cd ../frontend
start "前端服务" npm run dev
timeout /t 5 /nobreak > nul
start http://localhost:3000
echo 工具已启动，浏览器将自动打开
pause
```

**Linux/Mac启动脚本 (start.sh)**
```bash
#!/bin/bash
echo "正在启动小红书内容优化工具..."
cd backend
python run.py &
BACKEND_PID=$!
sleep 3
cd ../frontend
npm run dev &
FRONTEND_PID=$!
sleep 5
open http://localhost:3000  # macOS
# xdg-open http://localhost:3000  # Linux
echo "工具已启动，浏览器将自动打开"
echo "按 Ctrl+C 停止服务"
wait
```

### 6.2 技术难点和解决方案

#### 6.2.1 违禁词检测准确性
- **难点**: 变形词、上下文相关词的准确识别
- **解决方案**: 多层检测机制 + 机器学习模型

#### 6.2.2 谐音词替换质量
- **难点**: 保持语义完整性和阅读体验
- **解决方案**: 多维度评分机制 + 人工校验

#### 6.2.3 性能优化
- **难点**: 大文本的实时处理
- **解决方案**: 算法优化 + 缓存机制 + 异步处理

## 7. 风险评估和应对策略

### 7.1 技术风险
- **数据准确性**: 建立持续更新机制
- **性能瓶颈**: 分布式处理和缓存优化
- **算法误判**: 多重验证和人工审核

### 7.2 业务风险
- **平台政策变化**: 灵活的配置机制
- **用户需求变化**: 模块化设计便于扩展
- **竞品影响**: 持续功能创新和优化

## 8. 后续扩展规划

### 8.1 功能扩展
- 多平台支持 (抖音、微博等)
- AI内容生成
- 数据分析和报表
- 团队协作功能

### 8.2 技术演进
- 深度学习模型集成
- 自然语言生成技术
- 实时流处理
- 移动端原生应用

## 9. 总结

本设计文档详细规划了小红书内容检查和优化工具的各个方面，从需求分析到技术实现，从用户界面到开发计划。该工具将帮助用户有效提升内容质量，降低违规风险，提高内容在平台上的表现。

通过模块化的设计和灵活的架构，该工具具备良好的扩展性和维护性，能够适应平台规则的变化和用户需求的演进。