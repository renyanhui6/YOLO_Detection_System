from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import requests
from datetime import datetime
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

# 豆包API配置
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
# 豆包API密钥[形如xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx]
DOUBAO_API_KEY = "ad85c717-7661-4d83-bd4d-d07485c02e30"  # 填写你的密钥

def call_doubao_api(message, conversation_history=None, image_data=None):
    """调用豆包API，支持图片输入"""
    try:
        # 构建消息历史
        messages = []

        # 添加对话历史（最多保留最近5轮对话）
        if conversation_history:
            for msg in conversation_history[-10:]:  # 保留最近10条消息
                messages.append(msg)

        # 构建用户消息
        if image_data:
            # 如果有图片，使用豆包的多模态消息格式
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        else:
            # 纯文本消息
            user_message = {"role": "user", "content": message}

        messages.append(user_message)

        # 调用API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DOUBAO_API_KEY}"
        }

        # 豆包模型
        model_name = "doubao-seed-1-6-250615"

        data = {
            "model": model_name,
            "messages": messages
        }
        
        response = requests.post(DOUBAO_API_URL, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {})
            }
        elif response.status_code == 401:
            return {
                "success": False,
                "error": "API密钥无效，请检查您的豆包API密钥是否正确"
            }
        elif response.status_code == 402:
            return {
                "success": False,
                "error": "账户余额不足，请前往豆包API控制台充值后再试"
            }
        elif response.status_code == 429:
            return {
                "success": False,
                "error": "请求过于频繁，请稍后再试"
            }
        elif response.status_code == 400:
            # 可能是视觉模型的特殊错误
            error_detail = response.text
            if image_data and "model" in error_detail.lower():
                return {
                    "success": False,
                    "error": "视觉模型暂时不可用，已切换为文本分析模式"
                }
            return {
                "success": False,
                "error": f"请求参数错误: {error_detail}"
            }
        else:
            return {
                "success": False,
                "error": f"API调用失败: {response.status_code} - {response.text}"
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
def chat_with_doubao():
    """智能问答接口 - 调用豆包API，支持图片输入"""
    try:
        request_data = request.get_json()

        # 验证必填字段
        if not request_data.get('message'):
            return jsonify({
                'success': False,
                'message': '消息内容不能为空'
            }), 400

        user_message = request_data['message']
        conversation_history = request_data.get('history', [])

        # 获取图片数据（如果有）
        image_data = None
        context = request_data.get('context', {})

        # 检查是否有图片数据
        if context.get('hasImage') and request_data.get('imageUrl'):
            image_data = request_data['imageUrl']
            print(f"收到图片数据，URL长度: {len(image_data) if image_data else 0}")

        # 调用豆包API
        result = call_doubao_api(user_message, conversation_history, image_data)

        if result['success']:
            return jsonify({
                'success': True,
                'response': result['content'],  # 前端期望的字段名
                'data': {
                    'message': result['content'],
                    'usage': result.get('usage', {}),
                    'timestamp': datetime.now().isoformat(),
                    'hasImage': bool(image_data)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/api/chat/check-connection', methods=['GET'])
def check_network_connection():
    """检查网络连接状态"""
    try:
        # 尝试连接豆包API
        response = requests.get("https://ark.cn-beijing.volces.com", timeout=5)
        return jsonify({
            'success': True,
            'connected': True,
            'message': '网络连接正常'
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