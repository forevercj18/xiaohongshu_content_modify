@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   小红书内容优化工具 - 启动脚本
echo ========================================
echo.

echo [1/4] 检查 Python 环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python 环境检查通过

echo.
echo [2/4] 检查 Node.js 环境...
node --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)
echo ✅ Node.js 环境检查通过

echo.
echo [3/4] 安装依赖包...
cd backend
if not exist "venv" (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt > nul 2>&1
if errorlevel 1 (
    echo ❌ Python 依赖安装失败
    pause
    exit /b 1
)
echo ✅ Python 依赖安装完成

cd ..\frontend
if not exist "node_modules" (
    echo 安装前端依赖...
    npm install > nul 2>&1
    if errorlevel 1 (
        echo ❌ 前端依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ 前端依赖安装完成

echo.
echo [4/4] 启动服务...
cd ..\backend
start "小红书内容优化工具 - 后端服务" cmd /k "venv\Scripts\activate && python run.py"
timeout /t 3 /nobreak > nul

cd ..\frontend
start "小红书内容优化工具 - 前端服务" cmd /k "npm run dev"
timeout /t 5 /nobreak > nul

echo.
echo 🚀 应用启动完成！
echo.
echo 📱 前端地址: http://localhost:3000
echo 📡 后端地址: http://localhost:8000
echo 📋 API文档: http://localhost:8000/docs
echo.
echo 默认管理员账户: admin / admin123
echo.
echo 按任意键关闭此窗口...
pause > nul