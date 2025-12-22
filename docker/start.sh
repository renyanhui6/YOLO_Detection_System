#!/usr/bin/env bash
set -euo pipefail

# 确保必要的目录存在（静态上传/运行日志等）
mkdir -p /app/static/uploads /app/static/results /app/runs

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
