# 知识库管理后端API服务 (Python版本)

这是一个基于Python Flask的知识库管理后端服务，提供完整的CRUD操作接口。

## 环境要求

- Python 3.7+
- pip

## 安装和启动

### 1. 创建虚拟环境（推荐）
```bash
cd server_python
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动服务
```bash
python app.py
```

服务将在 `http://localhost:3000` 启动

## API接口文档

### 基础信息
- 基础URL: `http://localhost:3000/api`
- 数据格式: JSON
- 编码: UTF-8

### 接口列表

#### 1. 健康检查
```
GET /api/health
```
检查服务是否正常运行

**响应示例:**
```json
{
  "success": true,
  "message": "服务运行正常",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

#### 2. 获取所有知识条目
```
GET /api/knowledge
```

**查询参数:**
- `search` (可选): 搜索关键词，会在标题、内容、摘要、关键词中搜索
- `category` (可选): 分类筛选

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "图像检测基础知识",
      "category": "图像检测",
      "summary": "介绍图像检测的基本概念和常用算法",
      "content": "详细内容...",
      "keywords": ["图像检测", "计算机视觉"],
      "updateTime": "2024-01-01T00:00:00.000000"
    }
  ],
  "total": 1
}
```

#### 3. 获取单个知识条目
```
GET /api/knowledge/<id>
```

**路径参数:**
- `id`: 知识条目ID

#### 4. 创建知识条目
```
POST /api/knowledge
```

**请求体:**
```json
{
  "title": "标题",
  "category": "分类",
  "summary": "摘要",
  "content": "详细内容",
  "keywords": ["关键词1", "关键词2"]
}
```

**必填字段:** title, category, summary, content

#### 5. 更新知识条目
```
PUT /api/knowledge/<id>
```

**路径参数:**
- `id`: 知识条目ID

**请求体:** 同创建接口

#### 6. 删除知识条目
```
DELETE /api/knowledge/<id>
```

**路径参数:**
- `id`: 知识条目ID

#### 7. 获取分类列表
```
GET /api/categories
```

获取所有已存在的分类列表

**响应示例:**
```json
{
  "success": true,
  "data": ["图像检测", "视频分析", "机器学习"]
}
```

## 数据存储

数据存储在 `server_python/data/knowledge.json` 文件中，采用JSON格式。服务启动时会自动创建初始数据。

## 错误处理

所有接口都会返回统一的错误格式：

```json
{
  "success": false,
  "message": "错误描述",
  "error": "详细错误信息（可选）"
}
```

常见HTTP状态码：
- 200: 成功
- 201: 创建成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## CORS支持

服务已配置CORS，支持跨域请求，可以直接从前端应用调用。

## 开发模式

在开发模式下，Flask会自动重载代码变更。如需关闭调试模式，请修改 `app.py` 中的 `debug=False`。

## 部署建议

生产环境建议使用 Gunicorn 或 uWSGI 等WSGI服务器：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:3000 app:app
```