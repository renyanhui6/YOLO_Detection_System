@echo off
echo Starting servers...

echo Starting Knowledge Base Service...
start cmd /k "cd server_python && python app.py"

echo Starting API Server...
start cmd /k "cd server_python && python api_server.py"

echo Starting YOLO Detection Service...
start cmd /k "cd yolo_server && python app.py"

echo.
echo All servers are starting in separate windows.
echo Ports: 3000, 5002, 5001
echo.
pause