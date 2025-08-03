# 小红书内容检查和优化工具

一个本地化的小红书内容检查和优化工具，支持违禁词检测、谐音词智能替换和内容结构优化。

## 功能特点

- 🔍 **智能违禁词检测** - 多层检测机制，准确识别敏感词汇
- 🎵 **谐音词智能替换** - 一对多谐音词库，保持语义完整性
- 📊 **内容结构优化** - 深层内容策略建议，提升流量
- 🔐 **管理员后台** - 词库维护、权限管理、操作日志
- 📱 **现代化界面** - 参考Notion/Linear的优雅设计
- 🛡️ **完全本地化** - 数据不上传，保护隐私安全

## 技术架构

- **前端**: Vue.js 3 + TypeScript + 现代化UI设计
- **后端**: FastAPI + SQLite + SQLAlchemy
- **部署**: 本地Web服务，无需安装

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- 现代浏览器

### 启动应用
```bash
# Windows
双击 start.bat

# Mac/Linux  
./start.sh
```

应用将自动启动并在浏览器中打开 `http://localhost:3000`

## 项目结构

```
xiaohongshu_content_modify/
├── backend/                    # 后端FastAPI服务
│   ├── app/
│   │   ├── api/               # API接口
│   │   ├── core/              # 核心算法
│   │   ├── models/            # 数据模型
│   │   └── database/          # 数据库操作
│   └── data/                  # 初始数据
├── frontend/                   # 前端Vue.js应用
│   ├── src/
│   │   ├── views/             # 页面视图
│   │   ├── components/        # Vue组件
│   │   └── stores/            # 状态管理
│   └── public/
├── start.bat                  # Windows启动脚本
├── start.sh                   # Linux/Mac启动脚本
└── README.md
```

## 开发计划

- [x] 系统设计和架构规划
- [ ] 后端API开发
- [ ] 前端界面开发
- [ ] 管理员后台开发
- [ ] 核心算法实现
- [ ] 集成测试和优化

## 许可证

MIT License