# Windows Docker 一键启动指南（CPU/GPU）

## 适用范围
- Windows 10/11 本机一键启动
- 使用 Docker Desktop + Docker Compose
- 同时启动前端、三个后端服务与 MySQL

## 前置条件
- 已安装 Docker Desktop
- Docker Desktop 已启用 WSL2 后端（推荐）
- GPU 版本额外要求：
  - 已安装 NVIDIA 驱动
  - 已安装 NVIDIA Container Toolkit

## 步骤 1：进入项目目录
CMD：
```bat
cd /d D:\AAAA\intelligence_practice\YOLO_Detection_System
```

PowerShell：
```powershell
Set-Location D:\AAAA\intelligence_practice\YOLO_Detection_System
```

## 步骤 2：创建并填写 .env
CMD：
```bat
copy .env.example .env
```

PowerShell：
```powershell
Copy-Item .env.example .env
```

编辑 `.env`，至少填写：
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DOUBAO_API_KEY`

可选（在内网或公司网络时设置）：
- `HTTP_PROXY`
- `HTTPS_PROXY`
- `PIP_INDEX_URL`
- `PIP_TORCH_INDEX_URL`

## 步骤 3：CPU 一键启动
```bat
docker compose up --build
```

## 步骤 4：GPU 一键启动
```bat
docker compose -f docker-compose.gpu.yml up --build
```

## 访问地址
- 前端页面：`http://localhost/`
- 3000 端口：`http://localhost:3000`
- 5001 端口：`http://localhost:5001`
- 5002 端口：`http://localhost:5002`

## 停止与清理
CPU：
```bat
docker compose down
```

GPU：
```bat
docker compose -f docker-compose.gpu.yml down
```

清理数据库卷（会删除 MySQL 数据）：
```bat
docker compose down -v
```

## 常见问题
1) `cp` 不可用  
Windows CMD 没有 `cp`，请使用 `copy` 或 PowerShell 的 `Copy-Item`。

2) 构建阶段下载失败  
请在 `.env` 中设置 `HTTP_PROXY/HTTPS_PROXY`，或切换到可访问外网的网络。

3) GPU 版本无法使用显卡  
确认 NVIDIA 驱动与 NVIDIA Container Toolkit 已安装，并确保 Docker Desktop 使用 WSL2 后端。

4) 端口被占用  
请检查 80、3000、5001、5002 是否被其他程序占用，释放后重试。
