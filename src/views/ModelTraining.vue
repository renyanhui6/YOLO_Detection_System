<template>
  <div class="model-training">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="header-left">
        <button @click="goBack" class="back-btn">
          <i>←</i> 返回主页
        </button>
        <h1>模型训练</h1>
      </div>
      <div class="header-right">
        <div class="status-indicator" :class="trainingStatus">
          <span class="status-dot"></span>
          {{ getStatusText() }}
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 训练配置面板 -->
      <div class="config-panel">
        <div class="panel-header">
          <h2>训练配置</h2>
          <button @click="resetConfig" class="reset-btn">重置配置</button>
        </div>
        
        <div class="config-form">
          <!-- 数据集配置 -->
          <div class="form-section">
            <h3>数据集配置</h3>
            <div class="form-group">
              <label>数据集路径:</label>
              <div class="input-group">
                <input v-model="config.datasetPath" type="text" placeholder="请选择数据集路径" />
                <button @click="selectDataset" class="browse-btn">浏览</button>
              </div>
            </div>
            <div class="form-group">
              <label>训练集比例:</label>
              <input v-model="config.trainRatio" type="number" min="0.1" max="0.9" step="0.1" />
            </div>
            <div class="form-group">
              <label>验证集比例:</label>
              <input v-model="config.valRatio" type="number" min="0.1" max="0.9" step="0.1" />
            </div>
          </div>

          <!-- 模型配置 -->
          <div class="form-section">
            <h3>模型配置</h3>
            <div class="form-group">
              <label>模型类型:</label>
              <select v-model="config.modelType">
                <option value="yolov8n">YOLOv8n (轻量级)</option>
                <option value="yolov8s">YOLOv8s (小型)</option>
                <option value="yolov8m">YOLOv8m (中型)</option>
                <option value="yolov8l">YOLOv8l (大型)</option>
                <option value="yolov8x">YOLOv8x (超大型)</option>
              </select>
            </div>
            <div class="form-group">
              <label>预训练权重:</label>
              <select v-model="config.pretrainedWeights">
                <option value="coco">COCO预训练权重</option>
                <option value="custom">自定义权重</option>
                <option value="none">不使用预训练权重</option>
              </select>
            </div>
          </div>

          <!-- 训练参数 -->
          <div class="form-section">
            <h3>训练参数</h3>
            <div class="form-row">
              <div class="form-group">
                <label>训练轮数 (Epochs):</label>
                <input v-model="config.epochs" type="number" min="1" max="1000" />
              </div>
              <div class="form-group">
                <label>批次大小 (Batch Size):</label>
                <input v-model="config.batchSize" type="number" min="1" max="64" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>学习率:</label>
                <input v-model="config.learningRate" type="number" step="0.001" min="0.001" max="1" />
              </div>
              <div class="form-group">
                <label>图像尺寸:</label>
                <select v-model="config.imageSize">
                  <option value="416">416x416</option>
                  <option value="512">512x512</option>
                  <option value="640">640x640</option>
                  <option value="832">832x832</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>类别数量 (nc):</label>
                <input v-model="config.numClasses" type="number" min="1" readonly class="readonly-input" />
                <small class="form-hint">{{ datasetInfo.classNames.length > 0 ? `类别: ${datasetInfo.classNames.join(', ')}` : '请选择数据集以自动获取类别信息' }}</small>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button @click="startTraining" :disabled="isTraining" class="start-btn">
            <i v-if="isTraining">⏳</i>
            <i v-else>▶️</i>
            {{ isTraining ? '训练中...' : '开始训练' }}
          </button>
          <button @click="stopTraining" :disabled="!isTraining" class="stop-btn">
            <i>⏹️</i> 停止训练
          </button>
          <button @click="trackCurrentTraining" class="track-btn">
            <i>🔍</i> 跟踪当前训练
          </button>
          <button @click="saveConfig" class="save-btn">
            <i>💾</i> 保存配置
          </button>
        </div>
      </div>

      <!-- 训练监控面板 -->
      <div class="monitor-panel">
        <div class="panel-header">
          <h2>训练监控</h2>
          <div class="monitor-controls">
            <button @click="refreshLogs" class="refresh-btn">刷新</button>
            <button @click="clearLogs" class="clear-btn">清空日志</button>
          </div>
        </div>

        <!-- 训练进度 -->
        <div class="progress-section">
          <div class="progress-info">
            <span>训练进度: {{ currentEpoch }}/{{ config.epochs }}</span>
            <span>{{ trainingProgress }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: trainingProgress + '%' }"></div>
          </div>
        </div>

        <!-- 训练指标 -->
        <div class="metrics-section">
          <div class="metric-card">
            <h4>损失值 (Loss)</h4>
            <div class="metric-value">{{ metrics.loss.toFixed(4) }}</div>
          </div>
          <div class="metric-card">
            <h4>精确度 (Precision)</h4>
            <div class="metric-value">{{ metrics.precision.toFixed(3) }}</div>
          </div>
          <div class="metric-card">
            <h4>召回率 (Recall)</h4>
            <div class="metric-value">{{ metrics.recall.toFixed(3) }}</div>
          </div>
          <div class="metric-card">
            <h4>mAP@0.5</h4>
            <div class="metric-value">{{ metrics.map50.toFixed(3) }}</div>
          </div>
        </div>

        <!-- 训练日志 -->
        <div class="logs-section">
          <h3>训练日志</h3>
          <div class="logs-container" ref="logsContainer">
            <div v-for="(log, index) in trainingLogs" :key="index" class="log-entry" :class="log.type">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="trainingLogs.length === 0" class="no-logs">
              暂无训练日志
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据集浏览弹窗 -->
    <div v-if="showDatasetDialog" class="modal-mask" @click.self="closeDatasetDialog">
      <div class="modal-container">
        <div class="modal-header">
          <h3>选择数据集路径</h3>
          <button @click="closeDatasetDialog" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="path-bar">
            <span class="label">当前路径:</span>
            <span class="path-text">{{ datasetBrowser.currentPath || '/' }}</span>
            <button v-if="datasetBrowser.canGoUp" @click="goUp" class="up-btn">上级目录</button>
            <button @click="chooseCurrentDirectory" class="choose-here-btn">选择此目录</button>
          </div>
          
          <div v-if="datasetBrowser.loading" class="loading">
            正在加载目录...
          </div>
          
          <div v-else-if="datasetBrowser.error" class="error">
            {{ datasetBrowser.error }}
          </div>
          
          <div v-else class="dir-list">
            <div v-if="datasetBrowser.directories.length === 0" class="empty-tip">
              此目录为空
            </div>
            <div v-for="dir in datasetBrowser.directories" :key="dir.path" class="dir-item">
              <div class="dir-info" @click="enterDirectory(dir.path)">
                <span class="dir-name">📁 {{ dir.name }}</span>
                <div class="badges">
                  <span v-if="dir.hasDataYaml" class="badge success">data.yaml</span>
                  <span v-if="dir.hasTrainDir" class="badge info">train</span>
                  <span v-if="dir.hasValidDir" class="badge info">valid</span>
                </div>
              </div>
              <button @click="selectDirectory(dir.path)" class="select-btn">选择</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModelTraining',
  data() {
    return {
      // 训练状态
      trainingStatus: 'idle', // idle, training, completed, error
      isTraining: false,
      currentEpoch: 0,
      trainingProgress: 0,
      
      // 训练配置
      config: {
        datasetPath: '',
        trainRatio: 0.8,
        valRatio: 0.2,
        modelType: 'yolov8n',
        pretrainedWeights: 'coco',
        epochs: 100,
        batchSize: 16,
        learningRate: 0.01,
        imageSize: '640',
        numClasses: 0
      },
      
      // 训练指标
      metrics: {
        loss: 0,
        precision: 0,
        recall: 0,
        map50: 0
      },
      
      // 训练日志
      trainingLogs: [],
      
      // 状态监控定时器
      statusInterval: null,
      
      // API配置
      apiBaseUrl: 'http://localhost:5002/api',

      // 数据集浏览弹窗状态
      showDatasetDialog: false,
      datasetBrowser: {
        currentPath: '',
        basePath: '',
        parentPath: '',
        canGoUp: false,
        directories: [],
        loading: false,
        error: ''
      },
      
      // 数据集信息
      datasetInfo: {
        numClasses: 0,
        classNames: []
      }
    }
  },
  methods: {
    goBack() {
      this.$router.push('/')
    },
    
    getStatusText() {
      const statusMap = {
        idle: '待机中',
        training: '训练中',
        completed: '训练完成',
        error: '训练错误'
      }
      return statusMap[this.trainingStatus] || '未知状态'
    },
    
    resetConfig() {
      this.config = {
        datasetPath: '',
        trainRatio: 0.8,
        valRatio: 0.2,
        modelType: 'yolov8n',
        pretrainedWeights: 'coco',
        epochs: 100,
        batchSize: 16,
        learningRate: 0.01,
        imageSize: '640',
        numClasses: 0
      }
      this.datasetInfo = {
        numClasses: 0,
        classNames: []
      }
      this.addLog('info', '配置已重置为默认值')
    },
    
    // 打开数据集浏览弹窗
    selectDataset() {
      this.openDatasetDialog()
    },

    openDatasetDialog() {
      this.showDatasetDialog = true
      this.datasetBrowser.error = ''
      // 首次打开加载默认 datasets 目录
      this.fetchDirectory()
    },

    closeDatasetDialog() {
      this.showDatasetDialog = false
    },

    async fetchDirectory(path) {
      try {
        this.datasetBrowser.loading = true
        this.datasetBrowser.error = ''
        const url = path ? `${this.apiBaseUrl}/fs/list?path=${encodeURIComponent(path)}`
                         : `${this.apiBaseUrl}/fs/list`
        const res = await fetch(url)
        const json = await res.json()
        if (json.success) {
          const data = json.data
          this.datasetBrowser.currentPath = data.currentPath
          this.datasetBrowser.basePath = data.basePath
          this.datasetBrowser.parentPath = data.parentPath
          this.datasetBrowser.canGoUp = data.canGoUp
          this.datasetBrowser.directories = data.directories || []
        } else {
          this.datasetBrowser.error = json.error || '目录读取失败'
        }
      } catch (e) {
        this.datasetBrowser.error = '目录读取失败: ' + e.message
      } finally {
        this.datasetBrowser.loading = false
      }
    },

    goUp() {
      if (this.datasetBrowser.canGoUp && this.datasetBrowser.parentPath) {
        this.fetchDirectory(this.datasetBrowser.parentPath)
      }
    },

    enterDirectory(path) {
      this.fetchDirectory(path)
    },

    async selectDirectory(path) {
      this.config.datasetPath = path
      this.addLog('info', `已选择数据集路径: ${path}`)
      this.closeDatasetDialog()
      
      // 获取数据集信息
      await this.fetchDatasetInfo(path)
    },

    async chooseCurrentDirectory() {
      if (this.datasetBrowser.currentPath) {
        this.config.datasetPath = this.datasetBrowser.currentPath
        this.addLog('info', `已选择数据集路径: ${this.datasetBrowser.currentPath}`)
        this.closeDatasetDialog()
        
        // 获取数据集信息
        await this.fetchDatasetInfo(this.datasetBrowser.currentPath)
      }
    },
    
    // 获取数据集信息
    async fetchDatasetInfo(datasetPath) {
      try {
        this.addLog('info', '正在获取数据集信息...')
        const response = await fetch(`${this.apiBaseUrl}/dataset/info?path=${encodeURIComponent(datasetPath)}`)
        const result = await response.json()
        
        if (result.success) {
          this.datasetInfo.numClasses = result.data.numClasses
          this.datasetInfo.classNames = result.data.classNames
          this.config.numClasses = result.data.numClasses
          
          this.addLog('success', `数据集信息获取成功: ${result.data.numClasses} 个类别`)
          if (result.data.classNames.length > 0) {
            this.addLog('info', `类别名称: ${result.data.classNames.join(', ')}`)
          }
        } else {
          this.addLog('warning', `获取数据集信息失败: ${result.error}`)
          // 重置数据集信息
          this.datasetInfo.numClasses = 0
          this.datasetInfo.classNames = []
          this.config.numClasses = 0
        }
      } catch (error) {
        this.addLog('error', `获取数据集信息时发生错误: ${error.message}`)
        // 重置数据集信息
        this.datasetInfo.numClasses = 0
        this.datasetInfo.classNames = []
        this.config.numClasses = 0
      }
    },
    
    async startTraining() {
      if (!this.config.datasetPath) {
        this.$message?.error('请先选择数据集路径')
        return
      }
      
      try {
        this.addLog('info', '正在启动训练...')
        
        // 检查是否有类别信息
        if (this.config.numClasses === 0) {
          this.addLog('warning', '未检测到数据集类别信息，尝试重新获取...')
          await this.fetchDatasetInfo(this.config.datasetPath)
        }
        
        // 准备训练配置
        const trainingConfig = {
          dataset_path: this.config.datasetPath,
          model_type: this.config.modelType,
          epochs: parseInt(this.config.epochs),
          batch_size: parseInt(this.config.batchSize),
          learning_rate: parseFloat(this.config.learningRate),
          image_size: parseInt(this.config.imageSize),
          num_classes: parseInt(this.config.numClasses)
        }
        
        // 调用后端API开始训练
        const response = await fetch(`${this.apiBaseUrl}/training/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(trainingConfig)
        })
        
        const result = await response.json()
        
        if (result.success) {
          this.isTraining = true
          this.trainingStatus = 'training'
          this.addLog('info', result.message)
          this.$message?.success('训练已开始')
          
          // 开始监控训练状态
          this.startStatusMonitoring()
        } else {
          this.addLog('error', result.error)
          this.$message?.error(result.error)
        }
        
      } catch (error) {
        this.trainingStatus = 'error'
        this.addLog('error', `训练启动失败: ${error.message}`)
        this.$message?.error('训练启动失败')
      }
    },
    
    async stopTraining() {
      try {
        this.addLog('info', '正在停止训练...')
        
        const response = await fetch(`${this.apiBaseUrl}/training/stop`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        const result = await response.json()
        
        if (result.success) {
          this.isTraining = false
          this.trainingStatus = 'idle'
          this.addLog('warning', result.message)
          this.$message?.success('训练已停止')
          
          // 停止状态监控
          this.stopStatusMonitoring()
          
          // 重置训练进度
          this.currentEpoch = 0
          this.trainingProgress = 0
          
          // 重置训练指标
          this.metrics = {
            loss: 0,
            precision: 0,
            recall: 0,
            map50: 0
          }
        } else {
          this.addLog('error', result.error)
          this.$message?.error(result.error)
        }
        
      } catch (error) {
        this.addLog('error', `停止训练失败: ${error.message}`)
        this.$message?.error('停止训练失败')
        
        // 即使API调用失败，也尝试本地停止监控
        this.isTraining = false
        this.trainingStatus = 'idle'
        this.stopStatusMonitoring()
      }
    },
    
    saveConfig() {
      // 保存配置到本地存储
      localStorage.setItem('modelTrainingConfig', JSON.stringify(this.config))
      this.addLog('info', '配置已保存')
      this.$message?.success('配置保存成功')
    },
    
    loadConfig() {
      // 从本地存储加载配置
      const savedConfig = localStorage.getItem('modelTrainingConfig')
      if (savedConfig) {
        this.config = { ...this.config, ...JSON.parse(savedConfig) }
        this.addLog('info', '已加载保存的配置')
      }
    },
    
    startStatusMonitoring() {
      // 开始监控训练状态
      this.statusInterval = setInterval(async () => {
        await this.fetchTrainingStatus()
        await this.fetchTrainingLogs()
      }, 2000) // 每2秒更新一次
    },
    
    stopStatusMonitoring() {
      // 停止状态监控
      if (this.statusInterval) {
        clearInterval(this.statusInterval)
        this.statusInterval = null
      }
    },
    
    async fetchTrainingStatus() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/training/status`)
        const result = await response.json()
        
        if (result.success) {
          const status = result.data
          
          this.isTraining = status.is_training
          this.currentEpoch = status.current_epoch
          this.trainingProgress = status.progress
          
          // 更新训练指标
          this.metrics.loss = status.loss
          this.metrics.precision = status.precision
          this.metrics.recall = status.recall
          this.metrics.map50 = status.map50
          
          // 更新训练状态
          if (status.error) {
            this.trainingStatus = 'error'
            this.stopStatusMonitoring()
          } else if (!status.is_training && status.progress === 100) {
            this.trainingStatus = 'completed'
            this.stopStatusMonitoring()
          } else if (status.is_training) {
            this.trainingStatus = 'training'
          } else {
            this.trainingStatus = 'idle'
          }
        }
      } catch (error) {
        console.error('获取训练状态失败:', error)
      }
    },
    
    async fetchTrainingLogs() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/training/logs?limit=50`)
        const result = await response.json()
        
        if (result.success) {
          // 更新日志，只添加新的日志条目
          const newLogs = result.data
          if (newLogs.length > this.trainingLogs.length) {
            this.trainingLogs = newLogs.map(log => ({
              type: log.level,
              time: log.timestamp.split(' ')[1], // 只显示时间部分
              message: log.message
            }))
            
            // 自动滚动到底部
            this.$nextTick(() => {
              const container = this.$refs.logsContainer
              if (container) {
                container.scrollTop = container.scrollHeight
              }
            })
          }
        }
      } catch (error) {
        console.error('获取训练日志失败:', error)
      }
    },
    
    addLog(type, message) {
      const log = {
        type,
        time: new Date().toLocaleTimeString(),
        message
      }
      this.trainingLogs.push(log)
      
      // 限制日志数量
      if (this.trainingLogs.length > 100) {
        this.trainingLogs.shift()
      }
      
      // 自动滚动到底部
      this.$nextTick(() => {
        const container = this.$refs.logsContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    
    async refreshLogs() {
      await this.fetchTrainingLogs()
      this.addLog('info', '日志已刷新')
    },
    
    async clearLogs() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/training/logs/clear`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        const result = await response.json()
        
        if (result.success) {
          this.trainingLogs = []
          this.addLog('info', '日志已清空')
          this.$message?.success('日志清空成功')
        } else {
          this.$message?.error(result.error)
        }
      } catch (error) {
        this.$message?.error('清空日志失败')
      }
    },

    // 跟踪当前训练
    async trackCurrentTraining() {
      try {
        this.addLog('info', '正在检查当前训练状态...')
        
        // 首先检查训练状态
        const statusResponse = await fetch(`${this.apiBaseUrl}/training/status`)
        const statusResult = await statusResponse.json()
        
        if (statusResult.success) {
          const status = statusResult.data
          
          if (status.is_training) {
            // 有正在进行的训练，恢复监控状态
            this.isTraining = true
            this.trainingStatus = 'training'
            this.currentEpoch = status.current_epoch
            this.trainingProgress = status.progress
            
            // 更新训练指标
            this.metrics.loss = status.loss || 0
            this.metrics.precision = status.precision || 0
            this.metrics.recall = status.recall || 0
            this.metrics.map50 = status.map50 || 0
            
            // 加载训练日志
            await this.fetchTrainingLogs()
            
            // 开始监控训练状态
            this.startStatusMonitoring()
            
            this.addLog('success', `已成功跟踪当前训练 - 第${status.current_epoch}轮，进度${status.progress}%`)
            this.$message?.success('已成功跟踪当前训练任务')
          } else {
            // 没有正在进行的训练
            this.addLog('warning', '当前无训练任务')
            this.$message?.info('当前无训练任务')
          }
        } else {
          this.addLog('error', '检查训练状态失败: ' + statusResult.error)
          this.$message?.error('检查训练状态失败')
        }
      } catch (error) {
        this.addLog('error', `跟踪训练失败: ${error.message}`)
         this.$message?.error('跟踪训练失败')
       }
     },

     // 页面加载时检查训练状态
     async checkTrainingOnLoad() {
       try {
         const statusResponse = await fetch(`${this.apiBaseUrl}/training/status`)
         const statusResult = await statusResponse.json()
         
         if (statusResult.success && statusResult.data.is_training) {
           // 如果有正在进行的训练，自动恢复监控
           this.addLog('info', '检测到正在进行的训练，自动恢复监控状态...')
           await this.trackCurrentTraining()
         }
       } catch (error) {
         // 静默处理错误，不影响页面正常加载
         console.warn('检查训练状态失败:', error)
       }
     }
   },
  
  mounted() {
    this.loadConfig()
    this.addLog('info', '模型训练页面已加载')
    
    // 初始化指标
    this.metrics = {
      loss: 1.0,
      precision: 0.5,
      recall: 0.5,
      map50: 0.3
    }
    
    // 页面加载时自动检查是否有正在进行的训练
    this.checkTrainingOnLoad()
  },
  
  beforeDestroy() {
    // 清理定时器
    this.stopStatusMonitoring()
  }
}
</script>

<style scoped>
.model-training {
  min-height: 100vh;
  padding: 28px;
  background: radial-gradient(1200px 800px at 15% 10%, #eef2ff 0%, transparent 50%),
              radial-gradient(900px 700px at 85% 20%, #f0f9ff 0%, transparent 45%),
              linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 22px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(241, 245, 249, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.08);
  border: 1px solid rgba(2, 6, 23, 0.06);
  backdrop-filter: blur(8px);
  margin-bottom: 22px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  padding: 10px 16px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.14) 0%, rgba(37, 99, 235, 0.12) 100%);
  color: #0f172a;
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
}
.back-btn:hover { 
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.24) 0%, rgba(37, 99, 235, 0.22) 100%);
  box-shadow: 0 10px 20px rgba(2, 6, 23, 0.12);
}

.header h1 {
  margin: 0;
  font-weight: 800;
  letter-spacing: .2px;
  background: linear-gradient(90deg, #0f172a 0%, #334155 30%, #2563eb 60%, #0ea5e9 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: 999px;
  font-weight: 600;
  border: 1px solid rgba(2, 6, 23, 0.08);
  box-shadow: 0 6px 16px rgba(2, 6, 23, 0.08);
}
.status-indicator.idle { background: rgba(226, 232, 240, 0.65); color: #475569; }
.status-indicator.training { background: rgba(254, 240, 138, 0.7); color: #854d0e; }
.status-indicator.completed { background: rgba(187, 247, 208, 0.7); color: #166534; }
.status-indicator.error { background: rgba(254, 202, 202, 0.7); color: #991b1b; }
.status-dot { width: 10px; height: 10px; border-radius: 50%; background: currentColor; box-shadow: 0 0 0 2px rgba(255,255,255,.6) inset; }

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}

.config-panel, .monitor-panel {
  background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(255,255,255,0.86) 100%);
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(2, 6, 23, 0.10);
  overflow: hidden;
  border: 1px solid rgba(2, 6, 23, 0.06);
  backdrop-filter: blur(8px);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.9) 0%, rgba(241, 245, 249, 0.9) 100%);
  border-bottom: 1px solid rgba(2, 6, 23, 0.06);
}
.panel-header h2 { margin: 0; color: #0f172a; font-weight: 700; }

.reset-btn, .refresh-btn, .clear-btn {
  padding: 8px 14px;
  background: linear-gradient(135deg, rgba(75, 85, 99, 0.18) 0%, rgba(15, 23, 42, 0.14) 100%);
  color: #0f172a;
  border: 1px solid rgba(75, 85, 99, 0.28);
  border-radius: 10px;
  cursor: pointer;
  font-size: 12px;
  transition: all .2s ease;
}
.reset-btn:hover, .refresh-btn:hover, .clear-btn:hover { box-shadow: 0 10px 20px rgba(2, 6, 23, 0.12); }

.monitor-controls { display: flex; gap: 10px; }

.config-form { padding: 20px; }

.form-section { margin-bottom: 28px; }
.form-section h3 {
  margin: 0 0 14px 0;
  color: #334155;
  font-size: 16px;
  border-bottom: 2px solid #2563eb;
  padding-bottom: 8px;
}

.form-group { margin-bottom: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.form-group label { display: block; margin-bottom: 6px; font-weight: 600; color: #0f172a; }
.form-group input, .form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  background: rgba(255,255,255,0.9);
  transition: box-shadow .2s ease, border-color .2s ease;
}
.form-group input:focus, .form-group select:focus { outline: none; border-color: #93c5fd; box-shadow: 0 0 0 4px rgba(147, 197, 253, 0.35); }

.form-group .readonly-input { background-color: #f1f5f9; color: #64748b; cursor: not-allowed; }
.form-group .form-hint { display: block; font-size: 12px; color: #64748b; margin-top: 6px; font-style: italic; }

.input-group { display: flex; gap: 10px; }
.input-group input { flex: 1; }

.browse-btn {
  padding: 10px 16px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.24);
}
.browse-btn:hover { filter: brightness(1.05); }

.action-buttons {
  display: flex;
  gap: 12px;
  padding: 18px 20px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.9) 0%, rgba(241, 245, 249, 0.9) 100%);
  border-top: 1px solid rgba(2, 6, 23, 0.06);
}

.start-btn {
  padding: 12px 20px;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 10px 20px rgba(22, 163, 74, 0.24);
}
.start-btn:disabled { background: #94a3b8; cursor: not-allowed; }

.stop-btn {
  padding: 12px 20px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.24);
}
.stop-btn:disabled { background: #94a3b8; cursor: not-allowed; }

.save-btn {
  padding: 12px 20px;
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 10px 20px rgba(6, 182, 212, 0.24);
}

.track-btn {
  padding: 12px 20px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #1f2937;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 10px 20px rgba(217, 119, 6, 0.24);
}
.track-btn:hover { filter: brightness(1.05); }

.progress-section {
  padding: 20px;
  border-bottom: 1px solid rgba(2, 6, 23, 0.06);
}

.progress-info { display: flex; justify-content: space-between; margin-bottom: 10px; font-weight: 600; color: #0f172a; }

.progress-bar {
  width: 100%;
  height: 10px;
  background: rgba(226, 232, 240, 0.8);
  border-radius: 999px;
  overflow: hidden;
  box-shadow: inset 0 2px 6px rgba(2, 6, 23, 0.08);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #22c55e);
  transition: width 0.3s ease;
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.25);
}

.metrics-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 20px;
  border-bottom: 1px solid rgba(2, 6, 23, 0.06);
}

.metric-card {
  text-align: center;
  padding: 16px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.95) 100%);
  border-radius: 14px;
  border: 1px solid rgba(2, 6, 23, 0.06);
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.10);
  transition: transform .2s ease, box-shadow .2s ease;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 16px 32px rgba(2, 6, 23, 0.12); }

.metric-card h4 { margin: 0 0 8px 0; font-size: 12px; color: #64748b; text-transform: uppercase; }
.metric-value { font-size: 26px; font-weight: 800; background: linear-gradient(90deg, #2563eb, #0ea5e9); -webkit-background-clip: text; background-clip: text; color: transparent; }

.logs-section { padding: 20px; }
.logs-section h3 { margin: 0 0 15px 0; color: #0f172a; }

.logs-container {
  height: 300px;
  overflow-y: auto;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.95) 100%);
  border: 1px solid rgba(2, 6, 23, 0.06);
  border-radius: 12px;
  padding: 12px;
  box-shadow: inset 0 2px 8px rgba(2, 6, 23, 0.06);
}

.log-entry { display: flex; gap: 10px; margin-bottom: 6px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 12px; }
.log-time { color: #64748b; white-space: nowrap; }
.log-message { flex: 1; }
.log-entry.info .log-message { color: #0f172a; }
.log-entry.success .log-message { color: #16a34a; }
.log-entry.warning .log-message { color: #d97706; }
.log-entry.error .log-message { color: #dc2626; }

.no-logs { text-align: center; color: #64748b; font-style: italic; padding: 20px; }

@media (max-width: 1200px) { .main-content { grid-template-columns: 1fr; } .metrics-section { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .header { flex-direction: column; gap: 15px; } .form-row { grid-template-columns: 1fr; } .metrics-section { grid-template-columns: 1fr; } .action-buttons { flex-direction: column; } }
</style>

<style>
/* 选择数据集弹窗（玻璃拟态优化） */
.modal-mask {
  position: fixed;
  z-index: 1000;
  inset: 0;
  background: rgba(2, 6, 23, 0.35);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-container {
  width: min(800px, 90vw);
  background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(255,255,255,0.86) 100%);
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.18);
  overflow: hidden;
  border: 1px solid rgba(2, 6, 23, 0.06);
  backdrop-filter: blur(8px);
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.9) 0%, rgba(241, 245, 249, 0.9) 100%);
  border-bottom: 1px solid rgba(2, 6, 23, 0.06);
}
.modal-header h3 { margin: 0; font-weight: 700; color: #0f172a; }
.modal-close { border: none; background: transparent; font-size: 18px; cursor: pointer; color: #334155; }
.modal-close:hover { color: #0f172a; }
.modal-body { padding: 18px; }
.path-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.path-bar .label { color: #64748b; }
.path-text { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.up-btn, .choose-here-btn, .select-btn {
  padding: 8px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all .2s ease;
}
.up-btn:hover, .choose-here-btn:hover, .select-btn:hover { box-shadow: 0 10px 20px rgba(2, 6, 23, 0.12); }
.choose-here-btn { border-color: #22c55e; color: #166534; background: rgba(34, 197, 94, 0.08); }
.dir-list { max-height: 50vh; overflow: auto; border: 1px solid #e2e8f0; border-radius: 14px; }
.dir-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; border-bottom: 1px solid #f1f5f9; }
.dir-item:last-child { border-bottom: none; }
.dir-info { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.dir-name { font-weight: 600; color: #0f172a; }
.badges { display: flex; gap: 6px; }
.badge { padding: 2px 6px; font-size: 12px; border-radius: 12px; background: #e2e8f0; color: #334155; }
.badge.success { background: #dcfce7; color: #166534; }
.badge.info { background: #e0f2fe; color: #0c4a6e; }
.empty-tip { padding: 16px; color: #64748b; text-align: center; }
.loading { padding: 16px; text-align: center; }
.error { margin-top: 8px; color: #dc2626; }
</style>