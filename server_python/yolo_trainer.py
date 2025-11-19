import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import yaml
from ultralytics import YOLO
import torch
import signal
import sys

class YOLOTrainer:
    def __init__(self):
        self.training_status = {
            'is_training': False,
            'progress': 0,
            'current_epoch': 0,
            'total_epochs': 0,
            'loss': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'map50': 0.0,
            'map95': 0.0,
            'start_time': None,
            'end_time': None,
            'error': None
        }
        self.training_logs = []
        self.training_thread = None
        self.stop_training_flag = False
        self.current_trainer = None  # 保存当前的YOLO训练器实例
        
    def add_log(self, message, level='info'):
        """添加训练日志"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': level,
            'message': message
        }
        self.training_logs.append(log_entry)
        print(f"[{log_entry['timestamp']}] {level.upper()}: {message}")
        
    def validate_config(self, config):
        """验证训练配置"""
        required_fields = ['dataset_path', 'model_type', 'epochs', 'batch_size', 'learning_rate', 'image_size']
        
        for field in required_fields:
            if field not in config:
                return False, f"缺少必需字段: {field}"
                
        # 验证数据集路径
        dataset_path = config['dataset_path']
        if not os.path.exists(dataset_path):
            return False, f"数据集路径不存在: {dataset_path}"
            
        # 检查data.yaml文件
        data_yaml_path = os.path.join(dataset_path, 'data.yaml')
        if not os.path.exists(data_yaml_path):
            return False, f"数据集配置文件不存在: {data_yaml_path}"
            
        # 验证数值参数
        try:
            epochs = int(config['epochs'])
            batch_size = int(config['batch_size'])
            learning_rate = float(config['learning_rate'])
            image_size = int(config['image_size'])
            
            if epochs <= 0 or batch_size <= 0 or learning_rate <= 0 or image_size <= 0:
                return False, "数值参数必须大于0"
                
        except (ValueError, TypeError):
            return False, "数值参数格式错误"
            
        return True, "配置验证通过"
        
    def prepare_dataset(self, dataset_path):
        """准备数据集"""
        try:
            self.add_log(f"正在准备数据集: {dataset_path}")
            
            # 检查数据集结构
            required_dirs = ['train', 'valid']
            for dir_name in required_dirs:
                dir_path = os.path.join(dataset_path, dir_name)
                if not os.path.exists(dir_path):
                    raise Exception(f"数据集目录不存在: {dir_path}")
                    
            # 读取data.yaml配置
            data_yaml_path = os.path.join(dataset_path, 'data.yaml')
            with open(data_yaml_path, 'r', encoding='utf-8') as f:
                data_config = yaml.safe_load(f)
                
            self.add_log(f"数据集配置: {data_config}")
            
            # 统计数据集信息
            train_images = len(list(Path(os.path.join(dataset_path, 'train', 'images')).glob('*.*')))
            valid_images = len(list(Path(os.path.join(dataset_path, 'valid', 'images')).glob('*.*')))
            
            self.add_log(f"训练图片数量: {train_images}")
            self.add_log(f"验证图片数量: {valid_images}")
            
            return True, data_config
            
        except Exception as e:
            self.add_log(f"数据集准备失败: {str(e)}", 'error')
            return False, None
            
    def real_training(self, config):
        """真实的YOLOv8训练过程"""
        try:
            self.training_status['is_training'] = True
            self.training_status['start_time'] = datetime.now().isoformat()
            self.training_status['total_epochs'] = int(config['epochs'])
            self.training_status['error'] = None
            self.stop_training_flag = False
            
            self.add_log("开始真实YOLOv8训练")
            self.add_log(f"模型类型: {config['model_type']}")
            self.add_log(f"训练轮数: {config['epochs']}")
            self.add_log(f"批次大小: {config['batch_size']}")
            self.add_log(f"学习率: {config['learning_rate']}")
            self.add_log(f"图像尺寸: {config['image_size']}")
            
            # 准备数据集
            success, data_config = self.prepare_dataset(config['dataset_path'])
            if not success:
                raise Exception("数据集准备失败")
            
            # 检查CUDA可用性
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.add_log(f"使用设备: {device}")
            
            # 加载预训练模型
            model_name = f"{config['model_type']}.pt"
            self.add_log(f"加载预训练模型: {model_name}")
            model = YOLO(model_name)
            
            # 构建数据配置文件路径
            data_yaml_path = os.path.join(config['dataset_path'], 'data.yaml')
            
            # 创建自定义回调函数来监控训练进度
            def on_train_epoch_end(trainer):
                # 保存当前训练器实例
                self.current_trainer = trainer
                
                if self.stop_training_flag:
                    self.add_log("检测到停止信号，正在停止训练...", 'warning')
                    trainer.stop = True
                    return
                    
                epoch = trainer.epoch + 1
                total_epochs = trainer.epochs
                
                self.training_status['current_epoch'] = epoch
                self.training_status['progress'] = int((epoch / total_epochs) * 100)
                
                # 获取训练损失
                if hasattr(trainer, 'tloss') and trainer.tloss is not None:
                    # 处理张量类型的损失值，tloss通常是多元素张量
                    if hasattr(trainer.tloss, 'mean'):
                        self.training_status['loss'] = round(float(trainer.tloss.mean()), 4)
                    else:
                        self.training_status['loss'] = round(float(trainer.tloss), 4)
                elif hasattr(trainer, 'loss') and trainer.loss is not None:
                    if hasattr(trainer.loss, 'mean'):
                        self.training_status['loss'] = round(float(trainer.loss.mean()), 4)
                    else:
                        self.training_status['loss'] = round(float(trainer.loss), 4)
                
                self.add_log(f"Epoch {epoch}/{total_epochs} - Loss: {self.training_status['loss']:.4f}")
            
            def on_train_start(trainer):
                """训练开始时的回调"""
                self.current_trainer = trainer
                self.add_log("训练开始回调已设置")
            
            def on_val_end(validator):
                if self.stop_training_flag:
                    return
                    
                # 获取验证指标
                if hasattr(validator, 'metrics') and validator.metrics is not None:
                    metrics = validator.metrics
                    # 尝试不同的指标键名
                    if hasattr(metrics, 'box'): 
                         box_metrics = metrics.box
                         if hasattr(box_metrics, 'mp'):
                             mp_val = box_metrics.mp
                             if hasattr(mp_val, 'item'):
                                 self.training_status['precision'] = round(mp_val.item(), 4)
                             else:
                                 self.training_status['precision'] = round(float(mp_val), 4)
                         if hasattr(box_metrics, 'mr'):
                             mr_val = box_metrics.mr
                             if hasattr(mr_val, 'item'):
                                 self.training_status['recall'] = round(mr_val.item(), 4)
                             else:
                                 self.training_status['recall'] = round(float(mr_val), 4)
                         if hasattr(box_metrics, 'map50'):
                             map50_val = box_metrics.map50
                             if hasattr(map50_val, 'item'):
                                 self.training_status['map50'] = round(map50_val.item(), 4)
                             else:
                                 self.training_status['map50'] = round(float(map50_val), 4)
                         if hasattr(box_metrics, 'map'):
                             map_val = box_metrics.map
                             if hasattr(map_val, 'item'):
                                 self.training_status['map95'] = round(map_val.item(), 4)
                             else:
                                 self.training_status['map95'] = round(float(map_val), 4)
                    
                    self.add_log(f"验证指标 - Precision: {self.training_status['precision']:.4f}, "
                               f"Recall: {self.training_status['recall']:.4f}, "
                               f"mAP@0.5: {self.training_status['map50']:.4f}, "
                               f"mAP@0.5:0.95: {self.training_status['map95']:.4f}")
            
            # 添加回调函数
            model.add_callback('on_train_start', on_train_start)
            model.add_callback('on_train_epoch_end', on_train_epoch_end)
            model.add_callback('on_val_end', on_val_end)
            
            # 开始训练
            self.add_log("开始YOLOv8训练...")
            results = model.train(
                data=data_yaml_path,
                epochs=int(config['epochs']),
                batch=int(config['batch_size']),
                lr0=float(config['learning_rate']),
                imgsz=int(config['image_size']),
                device=device,
                project='runs/train',
                name=f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                save=True,
                save_period=10,  # 每10个epoch保存一次
                verbose=True
            )
            
            if not self.stop_training_flag:
                self.training_status['progress'] = 100
                self.add_log("YOLOv8训练完成！", 'success')
                
                # 获取最终训练结果
                if results:
                    save_dir = results.save_dir if hasattr(results, 'save_dir') else 'runs/train/latest'
                    self.add_log(f"模型已保存到: {save_dir}")
                    
                    # 获取最佳模型路径
                    best_model_path = os.path.join(save_dir, 'weights', 'best.pt')
                    if os.path.exists(best_model_path):
                        self.add_log(f"最佳模型: {best_model_path}")
            else:
                self.add_log("训练被用户停止", 'warning')
                
        except Exception as e:
            self.training_status['error'] = str(e)
            self.add_log(f"训练失败: {str(e)}", 'error')
            import traceback
            self.add_log(f"错误详情: {traceback.format_exc()}", 'error')
            
        finally:
            self.training_status['is_training'] = False
            self.training_status['end_time'] = datetime.now().isoformat()
            self.current_trainer = None  # 清除训练器引用
            
    def start_training(self, config):
        """开始训练"""
        if self.training_status['is_training']:
            return False, "训练正在进行中，请先停止当前训练"
            
        # 验证配置
        is_valid, message = self.validate_config(config)
        if not is_valid:
            return False, message
            
        # 重置状态和日志
        self.training_status = {
            'is_training': False,
            'progress': 0,
            'current_epoch': 0,
            'total_epochs': 0,
            'loss': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'map50': 0.0,
            'map95': 0.0,
            'start_time': None,
            'end_time': None,
            'error': None
        }
        self.training_logs = []
        
        # 启动训练线程
        self.training_thread = threading.Thread(target=self.real_training, args=(config,))
        self.training_thread.start()
        
        return True, "训练已开始"
        
    def stop_training(self):
        """停止训练"""
        if not self.training_status['is_training']:
            return False, "当前没有正在进行的训练"
            
        self.stop_training_flag = True
        self.add_log("正在停止训练...", 'warning')
        
        # 如果有当前训练器实例，直接设置停止标志
        if self.current_trainer:
            try:
                self.current_trainer.stop = True
                self.add_log("已向训练器发送停止信号", 'warning')
            except Exception as e:
                self.add_log(f"发送停止信号失败: {str(e)}", 'error')
        
        # 等待训练线程结束，增加超时时间
        if self.training_thread and self.training_thread.is_alive():
            self.add_log("等待训练线程结束...", 'warning')
            self.training_thread.join(timeout=10)  # 增加超时时间到10秒
            
            # 如果线程仍然存活，强制标记为停止
            if self.training_thread.is_alive():
                self.add_log("训练线程未能及时停止，强制标记为停止状态", 'warning')
                self.training_status['is_training'] = False
                self.training_status['end_time'] = datetime.now().isoformat()
                self.current_trainer = None
        
        return True, "训练已停止"
        
    def get_training_status(self):
        """获取训练状态"""
        return self.training_status.copy()
        
    def get_training_logs(self, limit=100):
        """获取训练日志"""
        return self.training_logs[-limit:] if limit else self.training_logs
        
    def clear_logs(self):
        """清空日志"""
        self.training_logs = []
        return True, "日志已清空"

# 全局训练器实例
trainer = YOLOTrainer()