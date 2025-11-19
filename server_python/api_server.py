from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import os
from database.database import (
    query_detection_results, delete_detection_result, 
    query_knowledge, delete_knowledge, add_knowledge, 
    update_knowledge, get_knowledge_by_id, get_knowledge_categories
)
from yolo_trainer import trainer

app = Flask(__name__)
CORS(app)

# 静态文件目录配置
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')

@app.route('/static/<path:subpath>/<filename>')
def serve_static_files(subpath, filename):
    """提供静态文件服务"""
    try:
        static_path = os.path.join(STATIC_DIR, subpath)
        return send_from_directory(static_path, filename)
    except Exception as e:
        print(f"静态文件访问失败: {e}")
        return jsonify({'error': '文件不存在'}), 404

@app.route('/api/detection-results', methods=['GET'])
def get_detection_results():
    """获取检测结果列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        detection_type = request.args.get('type', None)
        sort_order = request.args.get('sort', 'desc')  # 排序顺序
        order_by = request.args.get('order_by', 'create_time')  # 排序字段

        # 如果没有指定页大小限制，获取所有记录
        limit = request.args.get('limit')
        if limit is None and not request.args.get('pageSize'):
            page_size = 1000  # 减少默认值，避免排序缓冲区问题
        
        # 查询数据
        result = query_detection_results(page, page_size, detection_type, sort_order, order_by)
        
        if result is None:
            return jsonify({
                'success': False,
                'error': '查询失败'
            }), 500
        
        return jsonify({
            'success': True,
            'data': result['data'],  # 直接返回数据数组
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'pageSize': result['page_size'],
                'totalPages': result['total_pages']
            }
        })
        
    except Exception as e:
        print(f"获取检测结果失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取检测结果失败: {str(e)}'
        }), 500

@app.route('/api/detection-results/<int:result_id>', methods=['DELETE'])
def delete_detection_result_api(result_id):
    """删除检测结果"""
    try:
        success = delete_detection_result(result_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '删除失败，记录不存在'
            }), 404
            
    except Exception as e:
        print(f"删除检测结果失败: {e}")
        return jsonify({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }), 500

@app.route('/api/detection-results/<int:result_id>', methods=['GET'])
def get_detection_result_detail(result_id):
    """获取检测结果详情"""
    try:
        # 查询单条记录
        result = query_detection_results(page=1, page_size=1)
        
        if result and result['data']:
            # 查找指定ID的记录
            for item in result['data']:
                if item['id'] == result_id:
                    return jsonify({
                        'success': True,
                        'data': item
                    })
        
        return jsonify({
            'success': False,
            'error': '记录不存在'
        }), 404
        
    except Exception as e:
        print(f"获取检测结果详情失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取详情失败: {str(e)}'
        }), 500

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    """获取知识库数据（来自数据库），支持关键词和分类搜索"""
    try:
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        
        data = query_knowledge(
            search if search else None,
            category if category else None
        )
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        print(f"获取知识库数据失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取知识库数据失败: {str(e)}'
        }), 500

@app.route('/api/knowledge', methods=['POST'])
def add_knowledge_api():
    """添加知识库记录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category = data.get('category', '未分类').strip()
        keywords = data.get('keywords', [])
        
        if not title:
            return jsonify({'success': False, 'error': '标题不能为空'}), 400
        
        if not content:
            return jsonify({'success': False, 'error': '内容不能为空'}), 400
        
        success = add_knowledge(title, content, category, keywords)
        
        if success:
            return jsonify({'success': True, 'message': '添加成功'})
        else:
            return jsonify({'success': False, 'error': '添加失败'}), 500
            
    except Exception as e:
        print(f"添加知识库记录失败: {e}")
        return jsonify({'success': False, 'error': f'添加失败: {str(e)}'}), 500

@app.route('/api/knowledge/<int:knowledge_id>', methods=['GET'])
def get_knowledge_detail(knowledge_id):
    """获取知识库记录详情"""
    try:
        data = get_knowledge_by_id(knowledge_id)
        if data:
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': False, 'error': '记录不存在'}), 404
    except Exception as e:
        print(f"获取知识库记录详情失败: {e}")
        return jsonify({'success': False, 'error': f'获取失败: {str(e)}'}), 500

@app.route('/api/knowledge/<int:knowledge_id>', methods=['PUT'])
def update_knowledge_api(knowledge_id):
    """更新知识库记录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category = data.get('category', '未分类').strip()
        keywords = data.get('keywords', [])
        
        if not title:
            return jsonify({'success': False, 'error': '标题不能为空'}), 400
        
        if not content:
            return jsonify({'success': False, 'error': '内容不能为空'}), 400
        
        success = update_knowledge(knowledge_id, title, content, category, keywords)
        
        if success:
            return jsonify({'success': True, 'message': '更新成功'})
        else:
            return jsonify({'success': False, 'error': '更新失败，记录不存在'}), 404
            
    except Exception as e:
        print(f"更新知识库记录失败: {e}")
        return jsonify({'success': False, 'error': f'更新失败: {str(e)}'}), 500

@app.route('/api/knowledge/<int:knowledge_id>', methods=['DELETE'])
def delete_knowledge_api(knowledge_id: int):
    """删除知识库记录（数据库）"""
    try:
        ok = delete_knowledge(knowledge_id)
        if ok:
            return jsonify({'success': True, 'message': '删除成功'})
        return jsonify({'success': False, 'error': '记录不存在'}), 404
    except Exception as e:
        print(f"删除知识库记录失败: {e}")
        return jsonify({'success': False, 'error': f'删除失败: {str(e)}'}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取知识分类列表（从数据库知识数据获取）"""
    try:
        categories = get_knowledge_categories()
        return jsonify({'success': True, 'data': categories})
    except Exception as e:
        print(f"获取分类失败: {e}")
        return jsonify({'success': False, 'error': f'获取分类失败: {str(e)}'}), 500

@app.route('/api/knowledge/import', methods=['POST'])
def import_knowledge():
    """批量导入知识库数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        # 验证数据格式
        if not isinstance(data, list):
            return jsonify({'success': False, 'error': '数据格式错误，应为数组格式'}), 400
        
        success_count = 0
        error_count = 0
        errors = []
        
        for i, item in enumerate(data):
            try:
                # 验证必需字段
                if not isinstance(item, dict):
                    errors.append(f"第{i+1}条记录：数据格式错误，应为对象格式")
                    error_count += 1
                    continue
                
                title = item.get('title', '').strip()
                content = item.get('content', '').strip()
                category = item.get('category', '未分类').strip()
                keywords = item.get('keywords', [])
                
                if not title:
                    errors.append(f"第{i+1}条记录：标题不能为空")
                    error_count += 1
                    continue
                
                if not content:
                    errors.append(f"第{i+1}条记录：内容不能为空")
                    error_count += 1
                    continue
                
                # 验证关键词格式
                if not isinstance(keywords, list):
                    keywords = []
                
                # 添加到数据库
                success = add_knowledge(title, content, category, keywords)
                
                if success:
                    success_count += 1
                else:
                    errors.append(f"第{i+1}条记录：数据库添加失败")
                    error_count += 1
                    
            except Exception as e:
                errors.append(f"第{i+1}条记录：处理失败 - {str(e)}")
                error_count += 1
        
        # 返回导入结果
        result = {
            'success': True,
            'message': f'导入完成：成功 {success_count} 条，失败 {error_count} 条',
            'data': {
                'successCount': success_count,
                'errorCount': error_count,
                'totalCount': len(data),
                'errors': errors[:10]  # 最多返回前10个错误
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"导入知识库失败: {e}")
        return jsonify({'success': False, 'error': f'导入失败: {str(e)}'}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    try:
        # 获取图像检测统计
        image_results = query_detection_results(page=1, page_size=1000, detection_type='image')
        video_results = query_detection_results(page=1, page_size=1000, detection_type='video')
        
        image_count = image_results['total'] if image_results else 0
        video_count = video_results['total'] if video_results else 0
        
        # 计算总对象数
        total_objects = 0
        if image_results and image_results['data']:
            for item in image_results['data']:
                total_objects += item.get('object_count', 0)
        
        if video_results and video_results['data']:
            for item in video_results['data']:
                total_objects += item.get('object_count', 0)
        
        return jsonify({
            'success': True,
            'data': {
                'totalDetections': image_count + video_count,
                'imageDetections': image_count,
                'videoDetections': video_count,
                'totalObjects': total_objects
            }
        })
        
    except Exception as e:
        print(f"获取统计信息失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取统计信息失败: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'message': 'API服务运行正常',
        'timestamp': int(time.time() * 1000)
    })

# 模型训练相关API
@app.route('/api/training/start', methods=['POST'])
def start_training():
    """开始模型训练"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        success, message = trainer.start_training(data)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        print(f"开始训练失败: {e}")
        return jsonify({'success': False, 'error': f'开始训练失败: {str(e)}'}), 500

@app.route('/api/training/stop', methods=['POST'])
def stop_training():
    """停止模型训练"""
    try:
        success, message = trainer.stop_training()
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        print(f"停止训练失败: {e}")
        return jsonify({'success': False, 'error': f'停止训练失败: {str(e)}'}), 500

@app.route('/api/training/status', methods=['GET'])
def get_training_status():
    """获取训练状态"""
    try:
        status = trainer.get_training_status()
        return jsonify({'success': True, 'data': status})
        
    except Exception as e:
        print(f"获取训练状态失败: {e}")
        return jsonify({'success': False, 'error': f'获取训练状态失败: {str(e)}'}), 500

@app.route('/api/training/logs', methods=['GET'])
def get_training_logs():
    """获取训练日志"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = trainer.get_training_logs(limit)
        return jsonify({'success': True, 'data': logs})
        
    except Exception as e:
        print(f"获取训练日志失败: {e}")
        return jsonify({'success': False, 'error': f'获取训练日志失败: {str(e)}'}), 500

@app.route('/api/training/logs/clear', methods=['POST'])
def clear_training_logs():
    """清空训练日志"""
    try:
        success, message = trainer.clear_logs()
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        print(f"清空日志失败: {e}")
        return jsonify({'success': False, 'error': f'清空日志失败: {str(e)}'}), 500

# 文件系统浏览API
@app.route('/api/fs/list', methods=['GET'])
def list_directories():
    """列出指定路径下的子目录，用于数据集浏览弹窗"""
    try:
        # 项目根目录下的 datasets 作为基础目录
        base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets'))
        req_path = request.args.get('path', '').strip()

        # 解析当前路径
        if req_path:
            current_path = os.path.abspath(req_path)
        else:
            current_path = base_dir

        # 校验当前路径存在且为目录
        if not os.path.isdir(current_path):
            return jsonify({'success': False, 'error': '目录不存在'}), 400

        # 安全校验：仅允许访问 base_dir 及其子目录
        if os.path.commonpath([base_dir, current_path]) != base_dir:
            return jsonify({'success': False, 'error': '不允许访问该目录'}), 403

        # 计算父目录与是否可返回上级
        parent_path = os.path.dirname(current_path)
        can_go_up = current_path != base_dir and os.path.commonpath([base_dir, parent_path]) == base_dir

        # 收集子目录信息
        directories = []
        try:
            for name in sorted(os.listdir(current_path)):
                full = os.path.join(current_path, name)
                if os.path.isdir(full):
                    # 数据集结构提示：是否存在 data.yaml、images、labels 等
                    has_yaml = os.path.isfile(os.path.join(full, 'data.yaml'))
                    # 兼容常见结构：images/train 或 train 目录
                    has_images = os.path.isdir(os.path.join(full, 'images')) or os.path.isdir(os.path.join(full, 'train'))
                    # 兼容常见结构：labels/train 或 valid/valid 目录
                    has_labels = os.path.isdir(os.path.join(full, 'labels')) or os.path.isdir(os.path.join(full, 'valid')) or os.path.isdir(os.path.join(full, 'valid'))

                    directories.append({
                        'name': name,
                        'path': full,
                        'hasYaml': has_yaml,
                        'hasImages': has_images,
                        'hasLabels': has_labels
                    })
        except PermissionError:
            # 某些目录可能无权限访问
            pass

        data = {
            'currentPath': current_path,
            'basePath': base_dir,
            'parentPath': parent_path if can_go_up else '',
            'canGoUp': can_go_up,
            'directories': directories
        }
        return jsonify({'success': True, 'data': data})

    except Exception as e:
        print(f"目录读取失败: {e}")
        return jsonify({'success': False, 'error': f'目录读取失败: {str(e)}'}), 500

@app.route('/api/dataset/info', methods=['GET'])
def get_dataset_info():
    """获取数据集信息，包括类别数量和类别名称"""
    try:
        dataset_path = request.args.get('path', '').strip()
        if not dataset_path:
            return jsonify({'success': False, 'error': '数据集路径不能为空'}), 400
        
        # 校验路径存在
        if not os.path.isdir(dataset_path):
            return jsonify({'success': False, 'error': '数据集路径不存在'}), 400
        
        # 查找 data.yaml 文件
        data_yaml_path = os.path.join(dataset_path, 'data.yaml')
        if not os.path.isfile(data_yaml_path):
            return jsonify({'success': False, 'error': '数据集目录中未找到 data.yaml 文件'}), 400
        
        # 解析 data.yaml 文件
        try:
            import yaml
            with open(data_yaml_path, 'r', encoding='utf-8') as f:
                data_config = yaml.safe_load(f)
            
            # 提取类别信息
            num_classes = data_config.get('nc', 0)
            class_names = data_config.get('names', [])
            
            # 处理不同格式的 names 字段
            if isinstance(class_names, dict):
                # 如果是字典格式 {0: 'class1', 1: 'class2'}
                class_names = [class_names[i] for i in sorted(class_names.keys())]
            elif isinstance(class_names, list):
                # 如果是列表格式 ['class1', 'class2']
                pass
            else:
                class_names = []
            
            # 如果没有明确的 nc 字段，从 names 推断
            if num_classes == 0 and class_names:
                num_classes = len(class_names)
            
            return jsonify({
                'success': True,
                'data': {
                    'numClasses': num_classes,
                    'classNames': class_names,
                    'datasetPath': dataset_path
                }
            })
            
        except yaml.YAMLError as e:
            return jsonify({'success': False, 'error': f'data.yaml 文件格式错误: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': f'解析 data.yaml 文件失败: {str(e)}'}), 500
    
    except Exception as e:
        print(f"获取数据集信息失败: {e}")
        return jsonify({'success': False, 'error': f'获取数据集信息失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("正在启动API服务...")
    app.run(host='0.0.0.0', port=5002, debug=True)