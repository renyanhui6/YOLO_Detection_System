from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import io
import json
import os
import requests
import zipfile
from datetime import datetime
from xml.etree import ElementTree as ET
from database.database import (
    query_detection_results, 
    query_knowledge, 
    add_knowledge, 
    update_knowledge as db_update_knowledge,
    delete_knowledge as db_delete_knowledge,
    get_knowledge_by_id,
    get_knowledge_categories,
    init_knowledge_table
)

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 初始化数据库表
init_knowledge_table()

# DeepSeek API配置
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
DEEPSEEK_API_URL = f"{DEEPSEEK_API_BASE}/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODELS = {"deepseek-chat", "deepseek-reasoner"}

def normalize_deepseek_model(model_name: str) -> str:
    if model_name in DEEPSEEK_MODELS:
        return model_name
    return "deepseek-chat"

def decode_text_file(file_bytes):
    for encoding in ("utf-8", "utf-8-sig", "gbk", "gb18030", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="ignore")

def sanitize_text(text):
    cleaned = []
    for char in text:
        if char.isprintable() or char in "\n\r\t":
            cleaned.append(char)
        else:
            cleaned.append(" ")
    return "".join(cleaned)

def extract_docx_text(file_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zip_file:
            if "word/document.xml" not in zip_file.namelist():
                return None
            xml_data = zip_file.read("word/document.xml")

        root = ET.fromstring(xml_data)
        texts = []
        for element in root.iter():
            if element.tag.endswith("}t") and element.text:
                texts.append(element.text)
        return "\n".join(texts).strip()
    except Exception:
        return None

def extract_file_text(filename, file_bytes):
    _, ext = os.path.splitext(filename.lower())
    if ext in (".md", ".dic"):
        return decode_text_file(file_bytes).strip()
    if ext in (".dicx", ".docx"):
        docx_text = extract_docx_text(file_bytes)
        if docx_text:
            return docx_text
        return decode_text_file(file_bytes).strip()
    if ext == ".doc":
        raw_text = decode_text_file(file_bytes)
        return sanitize_text(raw_text).strip()
    return None

def call_deepseek_api(message, conversation_history=None, model=None):
    """调用DeepSeek API"""
    if not DEEPSEEK_API_KEY:
        return {
            "success": False,
            "error": "未配置DEEPSEEK_API_KEY"
        }

    try:
        messages = []

        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append(msg)

        user_message = {"role": "user", "content": message}

        messages.append(user_message)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }

        model_name = normalize_deepseek_model(model)

        data = {
            "model": model_name,
            "messages": messages
        }

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": model_name
            }
        if response.status_code == 401:
            return {
                "success": False,
                "error": "API密钥无效，请检查DEEPSEEK_API_KEY"
            }
        if response.status_code == 429:
            return {
                "success": False,
                "error": "请求过于频繁，请稍后再试"
            }

        try:
            error_detail = response.json().get("error", {}).get("message", "")
        except Exception:
            error_detail = response.text

        return {
            "success": False,
            "error": f"API调用失败: {response.status_code} - {error_detail}"
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "网络连接失败，请检查网络连接后重试"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "请求超时，请稍后重试"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"调用失败: {str(e)}"
        }

def stream_deepseek_api(message, conversation_history=None, model=None):
    if not DEEPSEEK_API_KEY:
        yield {"error": "未配置DEEPSEEK_API_KEY"}
        return

    try:
        messages = []

        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append(msg)

        messages.append({"role": "user", "content": message})

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }

        model_name = normalize_deepseek_model(model)

        data = {
            "model": model_name,
            "messages": messages,
            "stream": True
        }

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60, stream=True)

        if response.status_code != 200:
            if response.status_code == 401:
                yield {"error": "API密钥无效，请检查DEEPSEEK_API_KEY"}
                return
            if response.status_code == 429:
                yield {"error": "请求过于频繁，请稍后再试"}
                return

            try:
                error_detail = response.json().get("error", {}).get("message", "")
            except Exception:
                error_detail = response.text
            yield {"error": f"API调用失败: {response.status_code} - {error_detail}"}
            return

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                data_json = json.loads(payload)
            except json.JSONDecodeError:
                continue

            choices = data_json.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            content = delta.get("content")
            if content:
                yield {"content": content}

    except requests.exceptions.ConnectionError:
        yield {"error": "网络连接失败，请检查网络连接后重试"}
    except requests.exceptions.Timeout:
        yield {"error": "请求超时，请稍后再试"}
    except Exception as e:
        yield {"error": f"调用失败: {str(e)}"}

def build_knowledge_fallback(question: str) -> str:
    data = query_knowledge(search=question) or []
    if not data:
        return "未找到相关知识库内容，建议稍后重试或换个问题（本地知识库降级）"

    parts = []
    for item in data[:3]:
        title = item.get("title") or "未命名"
        summary = item.get("summary") or item.get("content") or ""
        parts.append(f"{title}：{summary}")

    return "；".join(parts) + "（本地知识库降级）"

# API路由

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'message': '服务运行正常',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge_list():
    """获取所有知识条目"""
    try:
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        
        # 使用数据库查询
        data = query_knowledge(search=search if search else None, category=category if category else None)
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '获取数据失败',
            'error': str(e)
        }), 500

@app.route('/api/knowledge/<int:knowledge_id>', methods=['GET'])
def get_knowledge_item(knowledge_id):
    """获取单个知识条目"""
    try:
        item = get_knowledge_by_id(knowledge_id)
        
        if not item:
            return jsonify({
                'success': False,
                'message': '知识条目不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': item
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '获取数据失败',
            'error': str(e)
        }), 500

@app.route('/api/knowledge', methods=['POST'])
def create_knowledge():
    """创建知识条目"""
    try:
        request_data = request.get_json()
        
        # 验证必填字段
        required_fields = ['title', 'content']
        for field in required_fields:
            if not request_data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field}为必填字段'
                }), 400
        
        # 使用数据库添加
        success = add_knowledge(
            title=request_data['title'],
            content=request_data['content'],
            category=request_data.get('category', '未分类'),
            keywords=request_data.get('keywords', [])
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '创建成功'
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '保存失败'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '创建失败',
            'error': str(e)
        }), 500

@app.route('/api/knowledge/<int:knowledge_id>', methods=['PUT'])
def update_knowledge_route(knowledge_id):
    """更新知识条目"""
    try:
        request_data = request.get_json()
        
        # 验证必填字段
        required_fields = ['title', 'content']
        for field in required_fields:
            if not request_data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field}为必填字段'
                }), 400
        
        # 使用数据库更新
        success = db_update_knowledge(
            knowledge_id=knowledge_id,
            title=request_data['title'],
            content=request_data['content'],
            category=request_data.get('category', '未分类'),
            keywords=request_data.get('keywords', [])
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '知识条目不存在或更新失败'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '更新失败',
            'error': str(e)
        }), 500

@app.route('/api/knowledge/<int:knowledge_id>', methods=['DELETE'])
def delete_knowledge_route(knowledge_id):
    """删除知识条目"""
    try:
        success = db_delete_knowledge(knowledge_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '知识条目不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '删除失败',
            'error': str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    try:
        categories = get_knowledge_categories()
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '获取分类失败',
            'error': str(e)
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    try:
        # 使用数据库查询获取知识库统计信息
        data = query_knowledge()
        total_knowledge = len(data)
        categories = get_knowledge_categories()
        total_categories = len(categories)
        
        # 模拟检测统计数据
        detection_stats = {
            'total_detections': 156,
            'today_detections': 23,
            'success_rate': 94.5
        }
        
        return jsonify({
            'success': True,
            'data': {
                'knowledge': {
                    'total': total_knowledge,
                    'categories': total_categories
                },
                'detection': detection_stats
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/detection-results', methods=['GET'])
def get_detection_results():
    """获取检测结果列表"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        detection_type = request.args.get('type', None)  # 可选的检测类型过滤
        
        # 调用数据库查询函数获取真实数据
        result = query_detection_results(page=page, page_size=limit, detection_type=detection_type)
        
        if result is not None:
            return jsonify({
                'success': True,
                'data': {
                    'results': result['data'],
                    'pagination': {
                        'current_page': result['page'],
                        'per_page': result['page_size'],
                        'total': result['total'],
                        'total_pages': result['total_pages']
                    }
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据库查询失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_deepseek():
    """智能问答接口 - 调用DeepSeek API"""
    try:
        request_data = request.get_json() or {}

        if not request_data.get('message'):
            return jsonify({
                'success': False,
                'message': '消息内容不能为空'
            }), 400

        user_message = request_data['message']
        conversation_history = request_data.get('history', [])
        model_name = request_data.get('model')

        result = call_deepseek_api(user_message, conversation_history, model=model_name)

        if not result.get('success'):
            fallback_text = build_knowledge_fallback(user_message)
            return jsonify({
                'success': True,
                'response': fallback_text,
                'data': {
                    'message': fallback_text,
                    'source': 'knowledge_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'model': normalize_deepseek_model(model_name)
                }
            })

        return jsonify({
            'success': True,
            'response': result['content'],
            'data': {
                'message': result['content'],
                'usage': result.get('usage', {}),
                'timestamp': datetime.now().isoformat(),
                'model': result.get('model')
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_with_deepseek_stream():
    """智能问答接口 - 流式输出"""
    request_data = request.get_json() or {}

    if not request_data.get('message'):
        return jsonify({
            'success': False,
            'message': '消息内容不能为空'
        }), 400

    user_message = request_data['message']
    conversation_history = request_data.get('history', [])
    model_name = request_data.get('model')

    def generate():
        try:
            has_content = False
            for event in stream_deepseek_api(user_message, conversation_history, model=model_name):
                if event.get("error"):
                    fallback_text = build_knowledge_fallback(user_message)
                    payload = {"content": fallback_text}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                content = event.get("content")
                if content:
                    has_content = True
                    payload = {"content": content}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            if not has_content:
                fallback_text = build_knowledge_fallback(user_message)
                payload = {"content": fallback_text}
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"
        except Exception:
            fallback_text = build_knowledge_fallback(user_message)
            payload = {"content": fallback_text}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"
    }
    return Response(stream_with_context(generate()), headers=headers, mimetype="text/event-stream")

@app.route('/api/chat/file', methods=['POST'])
def chat_with_deepseek_file():
    """智能问答接口 - 文件输入"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '未上传文件'
            }), 400

        upload_file = request.files['file']
        if not upload_file or upload_file.filename == '':
            return jsonify({
                'success': False,
                'message': '文件为空'
            }), 400

        file_bytes = upload_file.read()
        if not file_bytes:
            return jsonify({
                'success': False,
                'message': '文件内容为空'
            }), 400

        file_text = extract_file_text(upload_file.filename, file_bytes)
        if not file_text:
            return jsonify({
                'success': False,
                'message': '不支持的文件类型或解析失败'
            }), 400

        user_message = (request.form.get('message') or '').strip()
        if not user_message:
            user_message = '请基于附件内容回答'

        history_raw = request.form.get('history', '[]')
        try:
            conversation_history = json.loads(history_raw) if history_raw else []
        except json.JSONDecodeError:
            conversation_history = []

        model_name = request.form.get('model')

        combined_message = f"{user_message}\n\n附件内容：\n{file_text}"
        result = call_deepseek_api(combined_message, conversation_history, model=model_name)

        if not result.get('success'):
            fallback_text = build_knowledge_fallback(user_message)
            return jsonify({
                'success': True,
                'response': fallback_text,
                'data': {
                    'message': fallback_text,
                    'source': 'knowledge_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'model': normalize_deepseek_model(model_name)
                }
            })

        return jsonify({
            'success': True,
            'response': result['content'],
            'data': {
                'message': result['content'],
                'usage': result.get('usage', {}),
                'timestamp': datetime.now().isoformat(),
                'model': result.get('model')
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/api/chat/check-connection', methods=['GET'])
def check_network_connection():
    """检查网络连接状态"""
    if not DEEPSEEK_API_KEY:
        return jsonify({
            'success': True,
            'connected': False,
            'message': '未配置DEEPSEEK_API_KEY'
        })

    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        response = requests.get(f"{DEEPSEEK_API_BASE}/v1/models", headers=headers, timeout=5)

        if response.status_code == 200:
            return jsonify({
                'success': True,
                'connected': True,
                'message': '网络连接正常'
            })
        if response.status_code == 401:
            return jsonify({
                'success': True,
                'connected': False,
                'message': 'API密钥无效'
            })

        return jsonify({
            'success': True,
            'connected': False,
            'message': f'连接检查失败: {response.status_code}'
        })
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': True,
            'connected': False,
            'message': '网络连接失败'
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'connected': False,
            'message': f'连接检查失败: {str(e)}'
        })

if __name__ == '__main__':
    print('知识库管理后端服务已启动，端口: 3000')
    print('API文档: http://localhost:3000/api/health')
    app.run(host='0.0.0.0', port=3000, debug=True)
