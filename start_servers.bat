@echo off
echo ====================================
echo     Starting ERP AI Backend Servers
echo ====================================
echo.

echo [1/3] Starting Knowledge Base Service (Port 3000)...
start "Knowledge Service" cmd /k "cd /d "%~dp0server_python" && python app.py"
timeout /t 2 >nul

echo [2/3] Starting API Server (Port 5002)...
start "API Server" cmd /k "cd /d "%~dp0server_python" && python api_server.py"
timeout /t 2 >nul

echo [3/3] Starting YOLO Detection Service (Port 5001)...
start "YOLO Service" cmd /k "cd /d "%~dp0yolo_server" && python app.py"
timeout /t 2 >nul

echo.
echo ====================================
echo All servers are starting...
echo.
echo Server Port Information:
echo   - Knowledge Base Service: http://localhost:3000
echo   - API Server:             http://localhost:5002
echo   - YOLO Detection Service: http://localhost:5001
echo.
echo Please wait a few seconds for servers to fully start
echo To stop servers, close the corresponding command windows
echo ====================================
echo.
pause