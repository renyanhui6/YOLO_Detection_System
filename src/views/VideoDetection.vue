<template>
  <div class="video-detection">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-content">
        <h1>🎬 智能视频检测</h1>
        <p class="header-subtitle">使用AI技术分析视频内容，逐帧识别和追踪物体</p>
      </div>
      <button @click="goBack" class="back-btn">← 返回主页</button>
    </div>
    
    <!-- 操作指引 -->
    <div class="guide-section">
      <div class="guide-steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h4>选择检测模型</h4>
            <p>根据视频内容选择合适的AI模型</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>调整检测参数</h4>
            <p>配置置信度、采样频率等参数</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>上传视频文件</h4>
            <p>支持多种视频格式，建议不超过100MB</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h4>开始智能分析</h4>
            <p>AI将逐帧分析并生成检测报告</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="content">
      <!-- 配置面板 -->
      <div class="config-panel">
        <h3>检测配置</h3>
        <div class="config-row">
          <label>模型选择:</label>
          <select v-model="config.model" class="config-select">
            <option value="yolov8n">YOLOv8n (快速)</option>
            <option value="yolov8s">YOLOv8s (平衡)</option>
            <option value="yolov8m">YOLOv8m (精确)</option>
            <option value="yolov8l">YOLOv8l (高精度)</option>
            <option value="yolov8x">YOLOv8x (最高精度)</option>
            <option value="custom">自定义模型</option>
          </select>
        </div>
        <div v-if="config.model === 'custom'" class="config-row">
          <label>模型路径:</label>
          <div class="model-path-input">
            <input v-model="config.customModelPath" type="text" class="config-input" placeholder="请输入完整模型文件路径或点击浏览选择文件" />
            <button @click="selectModelFile" class="browse-btn">浏览</button>
          </div>
          <input ref="modelFileInput" type="file" accept=".pt,.pth,.onnx" @change="handleModelFileSelect" style="display: none" />
          <div v-if="customModelDisplayName" class="model-info">
            <small>已选择: {{ customModelDisplayName }}</small>
          </div>
        </div>
        <div class="config-row">
          <label>置信度阈值:</label>
          <input v-model.number="config.confidence" type="range" min="0.1" max="1.0" step="0.05" class="config-slider" />
          <span class="config-value">{{ config.confidence }}</span>
        </div>
        <div class="config-row">
          <label>IoU阈值:</label>
          <input v-model.number="config.iou" type="range" min="0.1" max="1.0" step="0.05" class="config-slider" />
          <span class="config-value">{{ config.iou }}</span>
        </div>
        <div class="config-row">
          <label>最大检测数:</label>
          <input v-model.number="config.maxDetections" type="number" min="1" max="1000" class="config-input" />
        </div>
        <div class="config-row">
          <label>采样频率 (帧/秒):</label>
          <input v-model.number="config.samplingRate" type="range" min="0.5" max="30" step="0.5" class="config-slider" />
          <span class="config-value">{{ config.samplingRate }}</span>
        </div>
        <div class="config-row">
          <label>跳帧间隔:</label>
          <input v-model.number="config.frameSkip" type="number" min="1" max="100" class="config-input" />
          <span class="config-hint">每隔多少帧检测一次</span>
        </div>
      </div>

      <div class="upload-area">
        <div class="upload-box" :class="{ 'media-present': !!selectedVideo }" @click="selectFile" @dragover.prevent @drop="handleDrop">
        
        <div v-if="!selectedVideo" class="upload-placeholder">
          <i class="upload-icon">🎬</i>
          <p>点击或拖拽上传视频</p>
          <p class="upload-hint">支持 MP4、AVI、MOV 格式</p>
        </div>
        <div v-else class="video-preview">
          <video :src="selectedVideo" controls preload="metadata"></video>
        </div>
        </div>
        <input ref="fileInput" type="file" accept="video/*" @change="handleFileSelect" style="display: none" />
      </div>
      
      <div class="controls">
        <button @click="detectVideo" :disabled="!selectedVideo || detecting" class="detect-btn">
          {{ detecting ? '检测中...' : '开始检测' }}
        </button>
        <button @click="clearVideo" :disabled="!selectedVideo" class="clear-btn">
          清除视频
        </button>
      </div>
      
      <div v-if="detecting" class="progress-area">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text">检测进度: {{ progress }}%</p>
      </div>
      
      <div v-if="detectionResult" class="result-area">
        <h3>检测结果</h3>
        <div v-if="detectionResult.error" class="error-message">
          <p>{{ detectionResult.error }}</p>
        </div>
        <div v-else class="result-content">
          <div class="result-summary">
            <p>视频时长: {{ detectionResult.duration }}秒</p>
            <p>处理帧数: {{ detectionResult.frameCount }}/{{ detectionResult.totalFrames }}</p>
            <p>视频帧率: {{ detectionResult.fps }} FPS</p>
            <p>检测到的对象类型: {{ detectionResult.objectTypes.length }}种</p>
            <p>总检测对象数: {{ detectionResult.totalObjects }}个</p>
          </div>
          
          <div v-if="detectionResult.objectTypes.length > 0" class="object-types">
            <h4>检测到的对象类型</h4>
            <div class="type-tags">
              <span v-for="type in detectionResult.objectTypes" :key="type" class="type-tag">
                {{ getClassDisplayText(type) }}
              </span>
            </div>
          </div>
          
          <div v-if="detectionResult.timeline.length > 0" class="timeline">
            <h4>检测时间线</h4>
            <div class="timeline-items">
              <div v-for="(item, index) in detectionResult.timeline" :key="index" class="timeline-item">
                <div class="time-info">
                  <div class="time-stamp">{{ item.time }}s</div>
                  <div class="frame-info">帧 #{{ item.frameIndex }}</div>
                </div>
                <div class="detected-objects">
                  <span v-for="(obj, objIndex) in item.objects" :key="objIndex" class="object-tag">
                    {{ getClassDisplayText(obj.name) }} ({{ obj.confidence }}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 检测结果帧图像单独显示在下方 -->
          <div v-if="detectionResult.timeline.length > 0" class="detection-frames-section">
            <h4>检测结果帧</h4>
            <div class="frames-grid">
              <div v-for="(item, index) in detectionResult.timeline" :key="'frame-' + index" class="frame-item">
                <div v-if="item.annotatedFrame" class="frame-container">
                  <div class="frame-header">
                    <span class="frame-time">{{ item.time }}s</span>
                    <span class="frame-number">帧 #{{ item.frameIndex }}</span>
                  </div>
                  <img :src="item.annotatedFrame" alt="检测结果帧" class="detection-frame-img" />
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="no-detection">
            <p>在视频中未检测到任何对象</p>
          </div>
          
          <div v-if="detectionResult.timestamp" class="timestamp">
            检测时间: {{ new Date(detectionResult.timestamp).toLocaleString() }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getClassDisplayText } from '@/utils/classTranslations'

export default {
  name: 'VideoDetection',
  data() {
    return {
      selectedVideo: null,
      videoFile: null,
      detecting: false,
      progress: 0,
      detectionResult: null,
      selectedModelFile: null,
      selectedModelFileHandle: null,
      customModelDisplayName: '', // 用于显示的文件名（包含大小信息）
      config: {
        model: 'yolov8m',
        customModelPath: '', // 实际的文件路径
        confidence: 0.6,
        iou: 0.5,
        maxDetections: 200,
        samplingRate: 8.0,
        frameSkip: 2
      }
    }
  },
  methods: {
    // 获取带翻译的类别显示文本
    getClassDisplayText(className) {
      return getClassDisplayText(className)
    },
    goBack() {
      this.$router.push('/')
    },
    selectFile() {
      this.$refs.fileInput.click()
    },
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.loadVideo(file)
      }
    },
    handleDrop(event) {
      event.preventDefault()
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('video/')) {
        this.loadVideo(file)
      }
    },
    loadVideo(file) {
      // 存储文件对象以供后续使用
      this.videoFile = file
      
      const reader = new FileReader()
      reader.onload = (e) => {
        this.selectedVideo = e.target.result
        this.detectionResult = null
        this.progress = 0
      }
      reader.readAsDataURL(file)
    },
    clearVideo() {
      this.selectedVideo = null
      this.videoFile = null
      this.detectionResult = null
      this.progress = 0
      this.$refs.fileInput.value = ''
    },
    async detectVideo() {
      if (!this.selectedVideo) return
      
      this.detecting = true
      this.progress = 0
      this.detectionResult = null
      
      try {
        // 获取文件对象
        const file = this.videoFile || this.$refs.fileInput.files[0]
        
        if (!file) {
          throw new Error('未找到视频文件')
        }
        
        // 创建FormData对象
        const formData = new FormData()
        formData.append('video', file)
        formData.append('config', JSON.stringify({
          model: this.config.model === 'custom' ? this.config.customModelPath : this.config.model,
          confidence: this.config.confidence,
          iou: this.config.iou,
          max_detections: this.config.maxDetections,
          sampling_rate: this.config.samplingRate,
          frame_skip: this.config.frameSkip
        }))
        
        // 模拟进度更新
        const progressInterval = setInterval(() => {
          if (this.progress < 90) {
            this.progress += 10
          }
        }, 500)
        
        // 调用视频检测API
        const response = await fetch('http://localhost:5001/api/detect/video', {
          method: 'POST',
          body: formData
        })
        
        clearInterval(progressInterval)
        
        if (!response.ok) {
          throw new Error(`HTTP错误: ${response.status}`)
        }
        
        const result = await response.json()
        
        if (!result.success) {
          throw new Error(result.error || '检测失败')
        }
        
        // 处理检测结果
        this.processVideoResult(result)
        this.progress = 100
        
      } catch (error) {
        console.error('视频检测失败:', error)
        this.detectionResult = {
          error: error.message || '视频检测过程中发生错误'
        }
      } finally {
        this.detecting = false
      }
    },
    
    processVideoResult(result) {
      // 统计对象类型
      const objectTypes = new Set()
      const timeline = []

      // 处理每一帧的结果
      result.frames.forEach(frame => {
        if (frame.objects && frame.objects.length > 0) {
          // 添加对象类型到集合
          frame.objects.forEach(obj => {
            objectTypes.add(obj.name)
          })

          // 添加到时间线（只显示有检测结果的帧）
          timeline.push({
            time: Math.round(frame.timestamp * 10) / 10, // 保留一位小数
            frameIndex: frame.frameIndex,
            objects: frame.objects.map(obj => ({
              name: obj.name,
              confidence: obj.confidence
            })),
            annotatedFrame: frame.annotatedFrame
          })
        }
      })

      // 计算视频时长（基于帧数和FPS）
      const duration = result.fps > 0 ? Math.round((result.totalFrames / result.fps) * 10) / 10 : 0

      this.detectionResult = {
        duration: duration,
        frameCount: result.processedFrames,
        totalFrames: result.totalFrames,
        fps: Math.round(result.fps * 10) / 10,
        objectTypes: Array.from(objectTypes),
        totalObjects: result.totalObjects,
        timeline: timeline,
        timestamp: result.timestamp
      }
    },
    async selectModelFile() {
      // 检查是否支持现代的File System Access API
      if ('showOpenFilePicker' in window) {
        try {
          const [fileHandle] = await window.showOpenFilePicker({
            types: [{
              description: '模型文件',
              accept: {
                'application/octet-stream': ['.pt', '.pth', '.onnx']
              }
            }],
            multiple: false
          })
          
          // 获取文件信息
          const file = await fileHandle.getFile()
          
          // 存储文件句柄以便后续使用
          this.selectedModelFile = file
          this.selectedModelFileHandle = fileHandle
          
          // 分别存储显示名称和提示用户输入完整路径
          this.customModelDisplayName = `${fileHandle.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`
          this.config.customModelPath = fileHandle.name  // 文件名作为提示，用户需要修改为完整路径
          
        } catch (error) {
          if (error.name !== 'AbortError') {
            console.error('选择文件时出错:', error)
          }
        }
      } else {
        // 回退到传统的文件选择方式
        this.$refs.modelFileInput.click()
      }
    },
    handleModelFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        // 存储文件对象
        this.selectedModelFile = file
        
        // 分别存储显示名称和实际路径
        this.customModelDisplayName = `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`
        
        // 尝试获取完整路径，如果支持webkitRelativePath则使用它
        if (file.webkitRelativePath) {
          this.config.customModelPath = file.webkitRelativePath
        } else if (file.path) {
          // 某些环境下可能有path属性（如Electron应用）
          this.config.customModelPath = file.path
        } else {
          // 文件名作为提示，用户需要修改为完整路径
          this.config.customModelPath = file.name
        }
      }
    }
  },
  
  // 获取置信度描述
  getConfidenceDesc(confidence) {
    if (confidence < 0.3) return '检测更多物体（可能有误报）'
    if (confidence < 0.6) return '平衡模式（推荐）'
    return '只显示高置信度结果'
  },
  
  // 获取IoU描述
  getIouDesc(iou) {
    if (iou < 0.3) return '保留更多重叠框'
    if (iou < 0.6) return '标准去重（推荐）'
    return '严格去重模式'
  },
  
  // 获取采样频率描述
  getSamplingDesc(rate) {
    if (rate < 2) return '节省时间模式'
    if (rate < 10) return '平衡模式（推荐）'
    return '详细分析模式'
  },
  
  // 获取跳帧描述
  getFrameSkipDesc(skip) {
    if (skip < 5) return '连续检测'
    if (skip < 15) return '标准间隔（推荐）'
    return '快速预览'
  }
}
</script>

<style scoped>
.video-detection {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 0 20px;
}

.header h1 {
  color: #333;
  font-size: 28px;
  margin: 0;
}

.back-btn {
  padding: 10px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.back-btn:hover {
  background: #5a6268;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 30px;
}

.config-panel {
  flex: 0 0 300px;
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  height: fit-content;
}

.config-panel h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.config-row {
  margin-bottom: 15px;
}

.config-row label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

.config-select,
.config-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.config-select:focus,
.config-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.config-slider {
  width: calc(100% - 60px);
  margin-right: 10px;
}

.config-value {
  display: inline-block;
  width: 50px;
  text-align: center;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
  color: #666;
}

.config-hint {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 3px;
}

.model-path-input {
  display: flex;
  gap: 10px;
  align-items: center;
}

.model-path-input .config-input {
  flex: 1;
}

.browse-btn {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
  white-space: nowrap;
}

.browse-btn:hover {
  background: #218838;
}

.upload-area {
  flex: 1;
}

.upload-area {
  margin-bottom: 30px;
}

.upload-box {
  width: 100%;
  min-height: 400px;
  border: 2px dashed #ccc;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.3s;
  background: white;
}
/* 选择了视频后，容器按内容自然撑开，避免因固定高度导致缩放 */
.upload-box.media-present {
  min-height: 0;
}
.upload-box:hover {
  border-color: #007bff;
}

.upload-placeholder {
  text-align: center;
  color: #666;
}

.upload-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 10px;
}

.upload-hint {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

.video-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.video-preview video {
  width: auto;
  height: auto;
  max-width: 100%;
  /* 移除高度限制，避免被容器高度强制缩小 */
  max-height: none;
  border-radius: 5px;
}

.controls {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 30px;
}

.detect-btn {
  padding: 12px 30px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.detect-btn:hover:not(:disabled) {
  background: #0056b3;
}

.detect-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.clear-btn {
  padding: 12px 30px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.clear-btn:hover:not(:disabled) {
  background: #c82333;
}

.clear-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.progress-area {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  color: #666;
  margin: 0;
}

.result-area {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.result-area h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 20px;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.result-summary p {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
  margin: 0;
  text-align: center;
  font-weight: bold;
  color: #495057;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 5px;
  border: 1px solid #f5c6cb;
  margin-bottom: 15px;
}

.object-types {
  margin-bottom: 30px;
}

.object-types h4 {
  color: #333;
  margin-bottom: 15px;
}

.type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.type-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid #bbdefb;
}

.timeline h4 {
  color: #333;
  margin-bottom: 15px;
}

.timeline-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.timeline-item {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.time-stamp {
  font-weight: bold;
  color: #007bff;
  font-size: 16px;
}

.frame-info {
  color: #6c757d;
  font-size: 12px;
}

.detected-objects {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.object-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.frame-preview {
  margin-top: 15px;
}

.annotated-frame {
  max-width: 100%;
  max-height: 300px;
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 检测结果帧样式 */
.detection-frames-section {
  margin-top: 30px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.detection-frames-section h4 {
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.frames-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.frame-item {
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.frame-container {
  width: 100%;
}

.frame-header {
  padding: 10px 15px;
  background: #007bff;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.frame-time {
  font-weight: bold;
  font-size: 14px;
}

.frame-number {
  font-size: 12px;
  opacity: 0.9;
}

.detection-frame-img {
  width: 100%;
  height: auto;
  display: block;
}

.no-detection {
  text-align: center;
  color: #6c757d;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.timestamp {
  color: #6c757d;
  font-size: 12px;
  text-align: right;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e9ecef;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .controls {
    flex-direction: column;
    align-items: center;
  }
  
  .detect-btn, .clear-btn {
    width: 200px;
  }
  
  .timeline-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .result-summary {
    grid-template-columns: 1fr;
  }
}

.model-info {
  margin-top: 5px;
}

.model-info small {
  color: #666;
  font-style: italic;
}

/* 导入图像检测界面的样式 */
/* 页面头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.header-subtitle {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 操作指引样式 */
.guide-section {
  margin-bottom: 30px;
}

.guide-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-number {
  width: 32px;
  height: 32px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.step-content p {
  margin: 0;
  font-size: 12px;
  color: #666;
}

/* 配置面板样式 */
.panel-header {
  margin-bottom: 25px;
}

.panel-header h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #333;
}

.help-text {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.config-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 8px;
}

.config-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.label-text {
  font-weight: 500;
  color: #333;
}

/* 工具提示样式 */
.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip-icon {
  width: 18px;
  height: 18px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: help;
}

.tooltip:hover .tooltip-content {
  visibility: visible;
  opacity: 1;
}

.tooltip-content {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.4;
  width: 280px;
  z-index: 1000;
  transition: opacity 0.3s;
}

.tooltip-content::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #333 transparent transparent transparent;
}

/* 滑块样式 */
.slider-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.slider-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
}

.config-value {
  font-weight: bold;
  color: #667eea;
}

.slider-desc {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

/* 数字输入样式 */
.number-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.number-input {
  width: 100px;
}

.input-unit {
  font-size: 14px;
  color: #666;
}

/* 自定义模型区域 */
.custom-model-section {
  background: #fff3cd;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ffeaa7;
}

.info-icon {
  color: #28a745;
  margin-right: 5px;
}
/* 统一美化样式增强 */
.video-detection {
  min-height: 100vh;
  background: linear-gradient(120deg, #eff3ff 0%, #f8f1ff 100%);
  padding: 20px;
}

.config-panel,
.upload-area,
.result-area {
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 10px 28px rgba(102, 126, 234, 0.18);
}

.detect-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
}

.detect-btn:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
}

.clear-btn {
  padding: 12px 24px;
  background: rgba(255,255,255,0.85);
  color: #444;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 8px;
}

.clear-btn:hover {
  background: #fff;
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

.progress-bar {
  height: 10px;
  background: rgba(0,0,0,0.06);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.type-tag,
.object-tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: linear-gradient(135deg, #e9efff, #f3e9ff);
  color: #4a4a4a;
  box-shadow: inset 0 0 0 1px rgba(102,126,234,0.25);
}

.timeline-item {
  background: rgba(255,255,255,0.9);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 10px;
  padding: 12px;
  box-shadow: 0 8px 22px rgba(0,0,0,0.08);
}

.frames-grid .frame-container {
  background: rgba(255,255,255,0.9);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 10px;
  box-shadow: 0 8px 22px rgba(0,0,0,0.08);
}

</style>
