# =======================
# Frontend build stage
# =======================
FROM node:18 AS frontend-builder
WORKDIR /frontend

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# =======================
# Runtime stage
# =======================
FROM python:3.10-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_DEFAULT_TIMEOUT=300

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    http_proxy=${HTTP_PROXY} \
    https_proxy=${HTTPS_PROXY} \
    PIP_INDEX_URL=${PIP_INDEX_URL} \
    PIP_DEFAULT_TIMEOUT=${PIP_DEFAULT_TIMEOUT}

RUN set -eux; \
    codename="$(. /etc/os-release && echo "$VERSION_CODENAME")"; \
    rm -f /etc/apt/sources.list /etc/apt/sources.list.d/* /etc/apt/sources.list.d/debian.sources; \
    echo "deb https://mirrors.aliyun.com/debian ${codename} main contrib non-free non-free-firmware" > /etc/apt/sources.list; \
    echo "deb https://mirrors.aliyun.com/debian ${codename}-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.aliyun.com/debian-security ${codename}-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    apt-get -o Acquire::Retries=5 -o Acquire::http::Pipeline-Depth=0 -o Acquire::http::No-Cache=true update; \
    apt-get -o Acquire::Retries=5 -o Acquire::http::Pipeline-Depth=0 -o Acquire::http::No-Cache=true install -y --no-install-recommends \
        build-essential ffmpeg libgl1 libglib2.0-0 nginx supervisor; \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app

# 安装Python依赖
COPY server_python/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --retries 5 --timeout 300 -r /tmp/requirements.txt


# 复制项目源码
COPY . /app

# 拷贝前端构建产物到Nginx目录
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

# 自定义Nginx与Supervisor配置
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh && mkdir -p static/uploads static/results runs

EXPOSE 80 3000 5001 5002

CMD ["/start.sh"]
