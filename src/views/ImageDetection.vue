<template>
  <div class="image-detection">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-content">
        <h1>🖼️ 智能图像检测</h1>
        <p class="header-subtitle">使用AI技术识别图像中的物体，支持多种模型和自定义参数</p>
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
            <p>根据需要选择合适的AI模型</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>调整参数设置</h4>
            <p>可根据图像类型微调检测参数</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>上传图像文件</h4>
            <p>支持拖拽上传或点击选择</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h4>开始智能检测</h4>
            <p>AI将自动识别并标注物体</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="content">
      <!-- 配置面板 -->
      <div class="config-panel">
        <div class="panel-header">
          <h3>🎛️ 检测配置</h3>
          <div class="help-text">选择合适的模型和参数以获得最佳检测效果</div>
        </div>

        <!-- 模型选择 -->
        <div class="config-section">
          <div class="config-row">
            <label class="config-label">
              <span class="label-text">AI检测模型</span>
              <div class="tooltip">
                <span class="tooltip-icon">?</span>
                <div class="tooltip-content">
                  <strong>模型选择建议：</strong><br>
                  • YOLOv8n：速度最快，适合实时检测<br>
                  • YOLOv8s：速度与精度平衡，推荐日常使用<br>
                  • YOLOv8m：精度较高，适合重要检测<br>
                  • YOLOv8l/x：精度最高，适合专业应用<br>
                  • 自定义模型：使用训练好的专用模型
                </div>
              </div>
            </label>
            <select v-model="config.model" class="config-select">
              <option value="yolov8n">⚡ YOLOv8n - 快速检测 (推荐新手)</option>
              <option value="yolov8s">⚖️ YOLOv8s - 平衡模式 (推荐)</option>
              <option value="yolov8m">🎯 YOLOv8m - 精确检测</option>
              <option value="yolov8l">🏆 YOLOv8l - 高精度模式</option>
              <option value="yolov8x">👑 YOLOv8x - 顶级精度</option>
              <option value="custom">🔧 自定义模型</option>
            </select>
          </div>

          <!-- 自定义模型配置 -->
          <div v-if="config.model === 'custom'" class="config-row custom-model-section">
            <label class="config-label">
              <span class="label-text">模型文件路径</span>
              <div class="tooltip">
                <span class="tooltip-icon">?</span>
                <div class="tooltip-content">
                  <strong>自定义模型使用说明：</strong><br>
                  • 支持 .pt、.pth、.onnx 格式<br>
                  • 可输入完整路径或只输入文件名<br>
                  • 系统会自动在训练目录中查找模型<br>
                  • 如输入 "last.pt"，系统自动查找最新训练的模型
                </div>
              </div>
            </label>
            <div class="model-path-input">
              <input
                v-model="config.customModelPath"
                type="text"
                class="config-input"
                placeholder="输入模型文件名（如：last.pt）或完整路径"
              />
              <button @click="selectModelFile" class="browse-btn">📂 浏览文件</button>
            </div>
            <input ref="modelFileInput" type="file" accept=".pt,.pth,.onnx" @change="handleModelFileSelect" style="display: none" />
            <div v-if="customModelDisplayName" class="model-info">
              <span class="info-icon">✅</span>
              <small>已选择: {{ customModelDisplayName }}</small>
            </div>
          </div>
        </div>

        <!-- 检测参数 -->
        <div class="config-section">
          <h4 class="section-title">🔧 检测参数</h4>

          <div class="config-row">
            <label class="config-label">
              <span class="label-text">置信度阈值</span>
              <div class="tooltip">
                <span class="tooltip-icon">?</span>
                <div class="tooltip-content">
                  <strong>置信度阈值说明：</strong><br>
                  控制检测结果的可信度要求<br>
                  • 低值(0.1-0.3)：检测更多物体，可能有误报<br>
                  • 中值(0.4-0.6)：平衡准确性和召回率<br>
                  • 高值(0.7-0.9)：只显示最确信的结果
                </div>
              </div>
            </label>
            <div class="slider-container">
              <input v-model.number="config.confidence" type="range" min="0.1" max="1.0" step="0.05" class="config-slider" />
              <div class="slider-info">
                <span class="config-value">{{ config.confidence }}</span>
                <span class="slider-desc">{{ getConfidenceDesc(config.confidence) }}</span>
              </div>
            </div>
          </div>

          <div class="config-row">
            <label class="config-label">
              <span class="label-text">重叠度阈值 (IoU)</span>
              <div class="tooltip">
                <span class="tooltip-icon">?</span>
                <div class="tooltip-content">
                  <strong>IoU阈值说明：</strong><br>
                  控制重叠检测框的处理方式<br>
                  • 低值(0.1-0.3)：保留更多重叠的检测框<br>
                  • 中值(0.4-0.6)：标准设置，去除明显重叠<br>
                  • 高值(0.7-0.9)：只保留重叠度很低的框
                </div>
              </div>
            </label>
            <div class="slider-container">
              <input v-model.number="config.iou" type="range" min="0.1" max="1.0" step="0.05" class="config-slider" />
              <div class="slider-info">
                <span class="config-value">{{ config.iou }}</span>
                <span class="slider-desc">{{ getIouDesc(config.iou) }}</span>
              </div>
            </div>
          </div>

          <div class="config-row">
            <label class="config-label">
              <span class="label-text">最大检测数量</span>
              <div class="tooltip">
                <span class="tooltip-icon">?</span>
                <div class="tooltip-content">
                  <strong>最大检测数说明：</strong><br>
                  限制最多显示的检测结果数量<br>
                  • 建议值：50-100（常规图像）<br>
                  • 复杂场景可设置更高值<br>
                  • 过高可能影响性能
                </div>
              </div>
            </label>
            <div class="number-input-container">
              <input v-model.number="config.maxDetections" type="number" min="1" max="1000" class="config-input number-input" />
              <span class="input-unit">个物体</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧主体区域 -->
      <div class="main-panel">
        <!-- 图像上传卡片 -->
        <div class="panel-card upload-card">
          <div class="card-header">
            <h3>📤 图像上传</h3>
            <p class="card-subtitle">选择要检测的图像文件，支持多种常见格式</p>
          </div>

          <div class="card-content">
            <div class="upload-box" :class="{ 'media-present': !!selectedImage }" @click="selectFile" @dragover.prevent @drop="handleDrop">
              <div v-if="!selectedImage" class="upload-placeholder">
                <div class="upload-icon">📤</div>
                <h4>上传图像文件</h4>
                <p class="main-text">点击此区域选择文件或直接拖拽图像到这里</p>
                <div class="supported-formats">
                  <span class="format-badge">JPG</span>
                  <span class="format-badge">PNG</span>
                  <span class="format-badge">JPEG</span>
                  <span class="format-badge">BMP</span>
                  <span class="format-badge">WEBP</span>
                </div>
                <p class="size-hint">💡 建议图像大小：1MB以内，分辨率不超过2000x2000像素</p>
              </div>
              <div v-else class="image-preview">
                <img :src="selectedImage" alt="预览图像" />
                <div class="image-overlay">
                  <button @click.stop="clearImage" class="overlay-btn clear">🗑️ 删除</button>
                  <button @click.stop="selectFile" class="overlay-btn replace">🔄 替换</button>
                </div>
              </div>
            </div>
            <input ref="fileInput" type="file" accept="image/*" @change="handleFileSelect" style="display: none" />
          </div>

          <div class="card-footer">
            <button
              @click="detectImage"
              :disabled="!selectedImage || detecting"
              class="detect-btn primary-btn"
              :class="{ 'detecting': detecting }"
            >
              <span class="btn-icon">{{ detecting ? '⏳' : '🚀' }}</span>
              {{ detecting ? 'AI正在分析图像...' : '开始智能检测' }}
            </button>

            <div v-if="selectedImage" class="secondary-actions">
              <button @click="clearImage" class="clear-btn secondary-btn">
                🗑️ 清除图像
              </button>
              <span class="status-text">
                {{ detecting ? '请稍候，AI正在处理您的图像...' : '准备就绪，点击开始检测' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 检测结果卡片 -->
        <div v-if="detectionResult" class="panel-card result-card">
          <div class="card-header">
            <h3>🎯 检测结果</h3>
            <p class="card-subtitle">AI智能分析完成，以下是识别到的物体信息</p>
          </div>

          <div class="card-content">
            <!-- 错误信息 -->
            <div v-if="detectionResult.error" class="error-container">
              <div class="error-icon">⚠️</div>
              <div class="error-content">
                <h4>检测遇到问题</h4>
                <p>{{ detectionResult.error }}</p>
                <div class="error-suggestions">
                  <p>💡 建议尝试：</p>
                  <ul>
                    <li>检查图像格式是否正确</li>
                    <li>确认图像文件没有损坏</li>
                    <li>尝试更换其他图像</li>
                    <li>检查网络连接状态</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- 检测成功结果 -->
            <div v-else>
              <!-- 统计摘要 -->
              <div class="result-summary">
                <div class="summary-card">
                  <div class="summary-icon">📊</div>
                  <div class="summary-content">
                    <div class="summary-number">{{ detectionResult.objectCount }}</div>
                    <div class="summary-label">检测到的物体</div>
                  </div>
                </div>
                <div v-if="detectionResult.timestamp" class="summary-card">
                  <div class="summary-icon">⏱️</div>
                  <div class="summary-content">
                    <div class="summary-text">{{ new Date(detectionResult.timestamp).toLocaleString() }}</div>
                    <div class="summary-label">完成时间</div>
                  </div>
                </div>
              </div>

              <!-- 物体详情 -->
              <div v-if="detectionResult.objects && detectionResult.objects.length > 0" class="objects-section">
                <h4 class="section-title">🏷️ 识别的物体详情</h4>
                <div class="objects-grid">
                  <div v-for="(obj, index) in detectionResult.objects" :key="index" class="object-card">
                    <div class="object-header">
                      <span class="object-name">{{ getClassDisplayText(obj.name) }}</span>
                      <span class="object-index">#{{ index + 1 }}</span>
                    </div>
                    <div class="object-details">
                      <div class="confidence-bar">
                        <div class="confidence-label">置信度</div>
                        <div class="confidence-progress">
                          <div class="confidence-fill" :style="{ width: obj.confidence + '%' }"></div>
                        </div>
                        <div class="confidence-value">{{ obj.confidence }}%</div>
                      </div>
                      <div v-if="obj.bbox" class="position-info">
                        <span class="position-label">📍 位置坐标:</span>
                        <span class="position-coords">[{{ obj.bbox.join(', ') }}]</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 无检测结果 -->
              <div v-else class="no-objects">
                <div class="no-objects-icon">🔍</div>
                <h4>未检测到物体</h4>
                <p>AI没有在此图像中识别到任何物体</p>
                <div class="no-objects-tips">
                  <p>💡 可能的原因：</p>
                  <ul>
                    <li>图像中没有模型认识的物体</li>
                    <li>置信度阈值设置过高</li>
                    <li>图像质量或光线不佳</li>
                    <li>物体过小或被遮挡</li>
                  </ul>
                  <p>建议：降低置信度阈值或尝试其他图像</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 标注结果卡片 -->
        <div v-if="detectionResult && detectionResult.annotatedImage && !detectionResult.error" class="panel-card annotated-card">
          <div class="card-header">
            <h3>🖼️ 标注结果图像</h3>
            <p class="card-subtitle">AI已在图像上标出检测到的物体和边界框</p>
          </div>

          <div class="card-content">
            <div class="annotated-image-container">
              <div class="image-wrapper">
                <img :src="detectionResult.annotatedImage" alt="AI标注结果图像" class="annotated-image" />
              </div>
            </div>
          </div>

          <div class="card-footer">
            <div class="image-actions">
              <button @click="downloadResult" class="action-btn">💾 下载结果</button>
              <button @click="shareResult" class="action-btn">📤 分享结果</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getClassDisplayText } from '@/utils/classTranslations'

export default {
  name: 'ImageDetection',
  data() {
    return {
      selectedImage: null,
      detecting: false,
      detectionResult: null,
      selectedModelFile: null,
      selectedModelFileHandle: null,
      customModelDisplayName: '', // 用于显示的文件名（包含大小信息）
      config: {
        model: 'yolov8n',
        customModelPath: '', // 实际的文件路径
        confidence: 0.5,
        iou: 0.45,
        maxDetections: 100
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
        this.loadImage(file)
      }
    },
    handleDrop(event) {
      event.preventDefault()
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        this.loadImage(file)
      }
    },
    loadImage(file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        this.selectedImage = e.target.result
        this.detectionResult = null
      }
      reader.readAsDataURL(file)
    },
    clearImage() {
      this.selectedImage = null
      this.detectionResult = null
      this.$refs.fileInput.value = ''
    },
    async detectImage() {
      if (!this.selectedImage) return
      
      this.detecting = true
      
      try {
        // 调用YOLO检测API
        const response = await fetch('http://localhost:5001/api/detect/image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: this.selectedImage,
            config: {
              model: this.config.model === 'custom' ? this.config.customModelPath : this.config.model,
              confidence: this.config.confidence,
              iou: this.config.iou,
              max_detections: this.config.maxDetections
            }
          })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json()
        
        if (result.success) {
          this.detectionResult = {
            objectCount: result.objectCount || result.object_count || 0,
            objects: result.objects || [],
            annotatedImage: result.annotatedImage || result.annotated_image || null,
            timestamp: result.timestamp
          }
        } else {
          console.error('检测失败:', result.error)
          // 显示错误信息给用户
          this.detectionResult = {
            objectCount: 0,
            objects: [],
            error: result.error || '检测失败，请重试'
          }
        }
      } catch (error) {
        console.error('API调用失败:', error)
        // 网络错误时的处理
        this.detectionResult = {
          objectCount: 0,
          objects: [],
          error: '无法连接到检测服务，请确保YOLO服务已启动'
        }
      } finally {
        this.detecting = false
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
    
    // 下载检测结果
    downloadResult() {
      if (this.detectionResult && this.detectionResult.annotatedImage) {
        const link = document.createElement('a')
        link.href = this.detectionResult.annotatedImage
        link.download = `detection_result_${new Date().getTime()}.jpg`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    },
    
    // 分享检测结果
    shareResult() {
      if (navigator.share && this.detectionResult) {
        navigator.share({
          title: 'AI图像检测结果',
          text: `检测到 ${this.detectionResult.objectCount} 个物体`,
          url: window.location.href
        }).catch(err => {
          console.log('分享失败:', err)
          // 回退到复制链接
          this.copyToClipboard()
        })
      } else {
        this.copyToClipboard()
      }
    },
    
    // 复制到剪贴板
    copyToClipboard() {
      const text = `AI图像检测结果：检测到 ${this.detectionResult.objectCount} 个物体`
      navigator.clipboard.writeText(text).then(() => {
        alert('检测结果已复制到剪贴板！')
      }).catch(() => {
        alert('复制失败，请手动复制检测结果')
      })
    }
  }
}
</script>

<style scoped>
.image-detection {
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
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  gap: 30px;
}

.config-panel {
  flex: 0 0 320px;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  height: fit-content;
  position: sticky;
  top: 20px;
}

/* 右侧主体区域 */
.main-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片通用样式 */
.panel-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #e1e5e9;
  overflow: hidden;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.panel-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

/* 卡片头部 */
.card-header {
  padding: 20px 24px 16px 24px;
  border-bottom: 1px solid #f0f2f5;
  background: linear-gradient(135deg, #f8f9fb 0%, #ffffff 100%);
}

.card-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1d23;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-subtitle {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

/* 卡片内容 */
.card-content {
  padding: 24px;
}

/* 卡片底部 */
.card-footer {
  padding: 16px 24px;
  background: #fafbfc;
  border-top: 1px solid #f0f2f5;
}

/* 上传卡片特殊样式 */
.upload-card .card-content {
  padding: 16px 24px;
}

.upload-card .card-footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.secondary-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.status-text {
  font-size: 14px;
  color: #6b7280;
  font-style: italic;
}

/* 检测结果卡片样式 */
.result-card {
  animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 标注图像卡片样式 */
.annotated-card {
  animation: slideInUp 0.5s ease-out 0.2s both;
}

.annotated-card .card-content {
  padding: 16px;
  text-align: center;
}

.annotated-card .card-footer {
  text-align: center;
}

/* 优化按钮样式 */
.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 200px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.secondary-btn {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.secondary-btn:hover {
  background: #e9ecef;
  color: #333;
  border-color: #adb5bd;
}

/* 统计摘要优化 */
.result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fb 0%, #ffffff 100%);
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.summary-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.summary-number {
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
  line-height: 1;
}

.summary-text {
  font-size: 14px;
  color: #1a1d23;
  font-weight: 500;
}

.summary-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

/* 物体卡片优化 */
.objects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.object-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fb 100%);
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.object-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.object-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.object-name {
  font-weight: 600;
  color: #1a1d23;
  font-size: 16px;
}

.object-index {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

/* 置信度进度条优化 */
.confidence-progress {
  background: #e9ecef;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 6px;
  position: relative;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  transition: width 0.5s ease;
  border-radius: 4px;
  position: relative;
}

.confidence-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* 图像操作按钮优化 */
.image-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 无检测结果样式优化 */
.no-objects {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f8f9fb 0%, #ffffff 100%);
  border: 2px dashed #dee2e6;
  border-radius: 12px;
}

.no-objects-icon {
  font-size: 48px;
  margin-bottom: 16px;
  filter: grayscale(100%) opacity(0.6);
}

/* 响应式设计优化 */
@media (max-width: 1200px) {
  .content {
    flex-direction: column;
  }

  .config-panel {
    flex: none;
    position: relative;
    top: auto;
  }

  .objects-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .content {
    padding: 0 10px;
    gap: 20px;
  }

  .panel-card {
    border-radius: 8px;
  }

  .card-header, .card-content, .card-footer {
    padding: 16px;
  }

  .result-summary {
    grid-template-columns: 1fr;
  }

  .objects-grid {
    grid-template-columns: 1fr;
  }

  .secondary-actions {
    flex-direction: column;
    text-align: center;
  }
}

/* 配置面板样式 */
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

.model-info {
  margin-top: 5px;
}

.model-info small {
  color: #666;
  font-style: italic;
}

/* 上传区域样式 */
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
  overflow: hidden;
}

.upload-box.media-present {
  min-height: 0;
  max-height: none;
  height: auto;
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

.image-preview {
  width: 100%;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  position: relative;
}

.image-preview img {
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 600px;
  object-fit: contain;
  border-radius: 5px;
  display: block;
}

/* 图像遮罩层 */
.image-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
}

.overlay-btn {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.3s;
}

.overlay-btn:hover {
  background: rgba(0, 0, 0, 0.9);
}

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

/* 配置面板优化样式 */
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
  min-width: 80px;
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

/* 上传区域样式优化 */
.upload-placeholder h4 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #333;
}

.main-text {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
}

.supported-formats {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.format-badge {
  background: #667eea;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.size-hint {
  margin: 0;
  font-size: 12px;
  color: #666;
  font-style: italic;
}

/* 标注图像样式 */
.annotated-image-container {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.image-wrapper {
  position: relative;
  text-align: center;
}

.annotated-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 错误容器样式 */
.error-container {
  display: flex;
  gap: 15px;
  padding: 20px;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  color: #721c24;
}

.error-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.error-content h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.error-suggestions {
  margin-top: 15px;
}

.error-suggestions ul {
  margin: 8px 0 0 20px;
  padding: 0;
}

.error-suggestions li {
  margin-bottom: 4px;
}
/* 统一美化样式增强 */
.image-detection {
  min-height: 100vh;
  background: linear-gradient(120deg, #eff3ff 0%, #f8f1ff 100%);
  padding: 20px;
}

.panel-card,
.config-panel,
.upload-card,
.result-card {
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 28px rgba(102, 126, 234, 0.18);
}

.primary-btn,
.detect-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
}

.primary-btn:hover,
.detect-btn:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
}

.secondary-btn,
.clear-btn,
.browse-btn {
  background: rgba(255, 255, 255, 0.85);
  color: #444;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.secondary-btn:hover,
.clear-btn:hover,
.browse-btn:hover {
  background: #fff;
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

.upload-box {
  border: 2px dashed rgba(102, 126, 234, 0.35);
  background: radial-gradient(ellipse at center, #ffffff 0%, #fafafa 100%);
}

.card-header h3 {
  background: linear-gradient(90deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* 检测结果内的对象标签优化 */
.object-tag,
.type-tag,
.class-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: linear-gradient(135deg, #e9efff, #f3e9ff);
  color: #4a4a4a;
  box-shadow: inset 0 0 0 1px rgba(102,126,234,0.25);
}

/* 结果统计信息卡片 */
.metric-card,
.summary-item {
  background: rgba(255,255,255,0.9);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 10px;
  box-shadow: 0 8px 22px rgba(0,0,0,0.08);
}

/* 覆盖图像遮罩按钮效果 */
.overlay-btn.clear {
  background: rgba(255, 71, 87, 0.85);
}
.overlay-btn.replace {
  background: rgba(32, 201, 151, 0.85);
}

</style>