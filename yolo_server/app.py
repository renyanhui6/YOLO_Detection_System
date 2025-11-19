import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
import os
import tempfile
import uuid
import time
from ultralytics import YOLO
import sys

# 添加数据库模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from server_python.database.database import save_detection_result, init_detect_result_table

app = Flask(__name__)
CORS(app)

# 全局变量存储模型
model = None

def load_model():
    """加载YOLO模型"""
    global model
    try:
        # 尝试加载YOLOv8n模型
        model = YOLO('yolov8n.pt')
        print("YOLO模型加载成功")
        return True
    except Exception as e:
        print(f"模型加载失败: {e}")
        return False

def resolve_model_path(model_name):
    """智能解析模型路径"""
    # 如果是绝对路径且文件存在，直接返回
    if os.path.isabs(model_name) and os.path.exists(model_name):
        return model_name
    
    # 如果是相对路径且在当前目录存在，直接返回
    if os.path.exists(model_name):
        return model_name
    
    # 如果只是文件名，在常见的模型目录中查找
    if not ('/' in model_name or '\\' in model_name):
        # 获取项目根目录（yolo_server的上级目录）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 常见的模型路径
        common_paths = [
            # 当前YOLO服务目录
            os.path.join(os.path.dirname(__file__), model_name),
            # 项目根目录
            os.path.join(project_root, model_name),
            # server_python目录
            os.path.join(project_root, 'server_python', model_name),
            # 训练结果目录模式：server_python/runs/train/*/weights/
            os.path.join(project_root, 'server_python', 'runs', 'train', '*', 'weights', model_name),
            # 其他可能的位置
            os.path.join(project_root, 'runs', 'train', '*', 'weights', model_name),
        ]
        
        # 导入glob用于模式匹配
        import glob
        
        for path_pattern in common_paths:
            if '*' in path_pattern:
                # 使用glob匹配模式
                matches = glob.glob(path_pattern)
                if matches:
                    # 返回最新的匹配文件（按修改时间排序）
                    latest_match = max(matches, key=os.path.getmtime)
                    print(f"找到模型文件: {latest_match}")
                    return latest_match
            else:
                # 直接检查路径
                if os.path.exists(path_pattern):
                    print(f"找到模型文件: {path_pattern}")
                    return path_pattern
        
        # 如果都没找到，显示搜索的路径用于调试
        print(f"未找到模型文件 '{model_name}'，已搜索以下位置:")
        for path_pattern in common_paths:
            if '*' not in path_pattern:
                print(f"  - {path_pattern}")
            else:
                matches = glob.glob(path_pattern)
                print(f"  - {path_pattern} (匹配: {matches})")
    
    # 返回原始路径，让YOLO尝试加载（可能会失败）
    return model_name



def base64_to_image(base64_string):
    """将base64字符串转换为PIL图像"""
    try:
        # 移除data:image/jpeg;base64,前缀（如果存在）
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # 解码base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # 确保图像是RGB格式（YOLO模型需要3通道）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception as e:
        print(f"Base64转图像失败: {e}")
        return None

def image_to_base64(image):
    """将PIL图像转换为base64字符串"""
    try:
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"图像转Base64失败: {e}")
        return None

def extract_video_frames(video_path, max_frames=30, interval=1):
    """从视频中提取帧"""
    try:
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_positions = []  # 记录每个提取帧在原视频中的位置
        frame_count = 0
        extracted_count = 0

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"视频信息：总帧数={total_frames}, FPS={fps}, 时长={total_frames/fps:.2f}秒")
        print(f"提取参数：最大帧数={max_frames}, 间隔={interval}")

        # 使用用户指定的间隔，而不是自动计算
        # 如果interval太小导致帧数过多，则调整间隔
        if total_frames // interval > max_frames:
            calculated_interval = max(1, total_frames // max_frames)
            print(f"调整间隔从 {interval} 到 {calculated_interval} 以控制最大帧数")
            interval = calculated_interval

        while cap.isOpened() and extracted_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % interval == 0:
                # 转换BGR到RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
                frame_positions.append(frame_count)  # 记录原始帧位置
                extracted_count += 1
                print(f"提取第 {extracted_count} 帧，源帧号: {frame_count}, 时间: {frame_count/fps:.2f}s")

            frame_count += 1

        cap.release()
        print(f"总共提取了 {len(frames)} 帧")
        return frames, fps, frame_positions
    except Exception as e:
        print(f"视频帧提取失败: {e}")
        return [], 0, []



@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'message': 'YOLO检测服务运行正常',
        'model_loaded': model is not None
    })

@app.route('/api/detect/image', methods=['POST'])
def detect_image():
    """图像检测接口"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': '缺少图像数据'}), 400
        
        # 获取配置参数
        config = data.get('config', {})
        model_name = config.get('model', 'yolov8n')
        confidence = config.get('confidence', 0.5)
        iou_threshold = config.get('iou', 0.45)
        max_detections = config.get('max_detections', 100)
        
        # 检查模型是否需要重新加载
        current_model = model
        if model_name != 'yolov8n' or model is None:
            try:
                if model_name.endswith('.pt') or '/' in model_name or '\\' in model_name:
                    # 自定义模型路径 - 使用智能路径解析
                    resolved_path = resolve_model_path(model_name)
                    print(f"尝试加载模型: {model_name} -> {resolved_path}")
                    current_model = YOLO(resolved_path)
                else:
                    # 预定义模型
                    current_model = YOLO(f'{model_name}.pt')
            except Exception as e:
                print(f"加载模型失败: {e}")
                current_model = model  # 使用默认模型
        
        if current_model is None:
            return jsonify({'success': False, 'error': '模型未加载'}), 500
        
        # 转换base64为图像
        image = base64_to_image(data['image'])
        if image is None:
            return jsonify({'success': False, 'error': '图像格式错误'}), 400
        
        # 转换为numpy数组
        img_array = np.array(image)
        
        # 进行检测，应用配置参数
        results = current_model(img_array, conf=confidence, iou=iou_threshold, max_det=max_detections)
        
        # 解析检测结果
        objects = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    # 获取置信度
                    confidence = float(box.conf[0].cpu().numpy())
                    # 获取类别
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = current_model.names[class_id]
                    
                    objects.append({
                        'name': class_name,
                        'confidence': round(confidence * 100, 2),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })
        
        # 生成标注图像
        annotated_image = None
        try:
            # 使用YOLO的plot方法生成标注图像
            annotated_result = results[0].plot()
            # 转换BGR到RGB
            annotated_rgb = cv2.cvtColor(annotated_result, cv2.COLOR_BGR2RGB)
            annotated_pil = Image.fromarray(annotated_rgb)
            annotated_image = image_to_base64(annotated_pil)
        except Exception as e:
            print(f"生成标注图像失败: {e}")
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 构建检测结果
        detection_result = {
            'success': True,
            'objectCount': len(objects),
            'objects': objects,
            'annotatedImage': annotated_image,
            'timestamp': int(time.time() * 1000),
            'processingTime': round(processing_time, 3)
        }
        
        # 保存检测结果到数据库
        try:
            file_name = data.get('fileName', f'image_{int(time.time())}.jpg')
            save_detection_result(
                detection_type='image',
                file_name=file_name,
                file_path=None,  # 前端上传的base64图像没有文件路径
                detection_result=detection_result,
                processing_time=processing_time
            )
        except Exception as e:
            print(f"保存检测结果到数据库失败: {e}")
            # 不影响检测结果返回
        
        return jsonify(detection_result)
        
    except Exception as e:
        print(f"检测过程出错: {e}")
        return jsonify({'success': False, 'error': f'检测失败: {str(e)}'}), 500

@app.route('/api/detect/video', methods=['POST'])
def detect_video():
    """视频检测接口"""
    start_time = time.time()
    
    try:
        # 检查是否有文件上传
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': '缺少视频文件'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'success': False, 'error': '未选择文件'}), 400
        
        # 获取配置参数
        config_str = request.form.get('config', '{}')
        try:
            config = eval(config_str) if config_str != '{}' else {}
        except:
            config = {}
        
        model_name = config.get('model', 'yolov8n')
        confidence = config.get('confidence', 0.5)
        iou_threshold = config.get('iou', 0.45)
        max_detections = config.get('max_detections', 100)
        sampling_rate = config.get('sampling_rate', 2.0)
        frame_skip = config.get('frame_skip', 15)
        
        # 检查模型是否需要重新加载
        current_model = model
        if model_name != 'yolov8n' or model is None:
            try:
                if model_name.endswith('.pt') or '/' in model_name or '\\' in model_name:
                    # 自定义模型路径 - 使用智能路径解析
                    resolved_path = resolve_model_path(model_name)
                    print(f"尝试加载模型: {model_name} -> {resolved_path}")
                    current_model = YOLO(resolved_path)
                else:
                    # 预定义模型
                    current_model = YOLO(f'{model_name}.pt')
            except Exception as e:
                print(f"加载模型失败: {e}")
                current_model = model  # 使用默认模型
        
        if current_model is None:
            return jsonify({'success': False, 'error': '模型未加载'}), 500
        
        # 保存临时文件
        temp_dir = tempfile.gettempdir()
        temp_filename = f"video_{uuid.uuid4().hex}.{video_file.filename.split('.')[-1]}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        try:
            video_file.save(temp_path)
            
            # 提取视频帧，应用采样频率
            # 计算基于视频时长和采样频率的最大帧数
            fps = cv2.VideoCapture(temp_path).get(cv2.CAP_PROP_FPS)
            total_frames = int(cv2.VideoCapture(temp_path).get(cv2.CAP_PROP_FRAME_COUNT))
            video_duration = total_frames / fps if fps > 0 else 30

            # 基于采样频率计算目标帧数，同时设置合理的上限
            target_frames = min(int(sampling_rate * video_duration), 300)  # 最多300帧
            max_frames = max(target_frames, 30)  # 至少30帧

            print(f"视频时长: {video_duration:.2f}秒, 采样频率: {sampling_rate}, 目标帧数: {target_frames}, 最大帧数: {max_frames}")

            frames, fps, frame_positions = extract_video_frames(temp_path, max_frames=max_frames, interval=frame_skip)
            
            if not frames:
                return jsonify({'success': False, 'error': '无法提取视频帧'}), 400
            
            # 对每一帧进行检测
            frame_results = []
            total_objects = 0
            
            for i, (frame, original_frame_position) in enumerate(zip(frames, frame_positions)):
                try:
                    # 进行检测，应用配置参数
                    results = current_model(frame, conf=confidence, iou=iou_threshold, max_det=max_detections)

                    # 解析检测结果
                    frame_objects = []
                    for result in results:
                        boxes = result.boxes
                        if boxes is not None:
                            for box in boxes:
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                confidence = float(box.conf[0].cpu().numpy())
                                class_id = int(box.cls[0].cpu().numpy())
                                class_name = current_model.names[class_id]

                                frame_objects.append({
                                    'name': class_name,
                                    'confidence': round(confidence * 100, 2),
                                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                                })

                    # 生成标注帧（可选）
                    annotated_frame = None
                    try:
                        annotated_result = results[0].plot()
                        annotated_rgb = cv2.cvtColor(annotated_result, cv2.COLOR_BGR2RGB)
                        annotated_pil = Image.fromarray(annotated_rgb)
                        annotated_frame = image_to_base64(annotated_pil)
                    except:
                        pass

                    # 使用原始帧位置计算正确的时间戳
                    timestamp = original_frame_position / fps if fps > 0 else original_frame_position

                    frame_results.append({
                        'frameIndex': original_frame_position,  # 使用原始帧位置
                        'timestamp': round(timestamp, 2),
                        'objectCount': len(frame_objects),
                        'objects': frame_objects,
                        'annotatedFrame': annotated_frame
                    })

                    total_objects += len(frame_objects)

                except Exception as e:
                    print(f"处理第{i}帧时出错: {e}")
                    continue
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 构建检测结果
            detection_result = {
                'success': True,
                'totalFrames': total_frames,  # 原视频总帧数
                'processedFrames': len(frame_results),
                'totalObjects': total_objects,
                'fps': fps,
                'frames': frame_results,
                'timestamp': int(time.time() * 1000),
                'processingTime': round(processing_time, 3)
            }
            
            # 保存检测结果到数据库
            try:
                save_detection_result(
                    detection_type='video',
                    file_name=video_file.filename,
                    file_path=temp_path,
                    detection_result=detection_result,
                    processing_time=processing_time
                )
            except Exception as e:
                print(f"保存视频检测结果到数据库失败: {e}")
                # 不影响检测结果返回
            
            return jsonify(detection_result)
            
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
                
    except Exception as e:
        print(f"视频检测过程出错: {e}")
        return jsonify({'success': False, 'error': f'视频检测失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("正在启动YOLO检测服务...")

    # 初始化数据库表
    print("正在初始化数据库表...")
    if init_detect_result_table():
        print("数据库表初始化成功")
    else:
        print("数据库表初始化失败，但服务将继续运行")

    # 加载模型
    if load_model():
        print("服务启动成功，监听端口5001")
        app.run(host='0.0.0.0', port=5001, debug=True)
    else:
        print("模型加载失败，服务启动失败")
        # 即使模型加载失败也启动服务，用于调试
        app.run(host='0.0.0.0', port=5001, debug=True)