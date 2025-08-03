#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo "  小红书内容优化工具 - 启动脚本"
echo "========================================"
echo -e "${NC}"

# 检查 Python
echo -e "${YELLOW}[1/4] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ 未找到 Python，请先安装 Python 3.8+${NC}"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi
echo -e "${GREEN}✅ Python 环境检查通过${NC}"

# 检查 Node.js
echo -e "${YELLOW}[2/4] 检查 Node.js 环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 未找到 Node.js，请先安装 Node.js 16+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js 环境检查通过${NC}"

# 安装依赖
echo -e "${YELLOW}[3/4] 安装依赖包...${NC}"

# Python 依赖
cd backend
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Python 依赖安装失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 依赖安装完成${NC}"

# 前端依赖
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 前端依赖安装失败${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ 前端依赖安装完成${NC}"

# 启动服务
echo -e "${YELLOW}[4/4] 启动服务...${NC}"

# 启动后端
cd ../backend
source venv/bin/activate
$PYTHON_CMD run.py &
BACKEND_PID=$!
echo "后端服务 PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 启动前端
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "前端服务 PID: $FRONTEND_PID"

# 等待前端启动
sleep 5

echo -e "${GREEN}"
echo "🚀 应用启动完成！"
echo ""
echo "📱 前端地址: http://localhost:3000"
echo "📡 后端地址: http://localhost:8000"
echo "📋 API文档: http://localhost:8000/docs"
echo ""
echo "默认管理员账户: admin / admin123"
echo -e "${NC}"

# 尝试打开浏览器
if command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
fi

echo "按 Ctrl+C 停止服务"

# 等待中断信号
trap 'echo -e "\n正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

wait