@echo off
echo 启动知识库管理后端服务 (Python版本)
echo =====================================

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo.
echo 检查依赖包...
pip show Flask >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖包安装失败
        pause
        exit /b 1
    )
)

echo.
echo 启动服务...
echo 服务地址: http://localhost:3000
echo 按 Ctrl+C 停止服务
echo.
python app.py

pause