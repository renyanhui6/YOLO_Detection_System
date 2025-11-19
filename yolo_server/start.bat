@echo off
echo 启动YOLO检测服务...

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查并安装依赖
echo 检查依赖包...
pip install -r requirements.txt

REM 下载YOLO模型（如果不存在）
if not exist "yolo11n.pt" (
    echo 下载YOLO11模型...
    python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"
)

REM 启动服务
echo 启动YOLO检测服务...
python app.py

pause