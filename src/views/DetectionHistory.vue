<template>
  <div class="detection-history">
    <div class="header">
      <h1>检测历史</h1>
      <button @click="goBack" class="back-btn">返回</button>
    </div>
    
    <div class="content">
      <div class="filter-bar">
        <div class="filter-group">
          <label>类型筛选:</label>
          <select v-model="filterType" @change="onFilterChange">
            <option value="all">全部</option>
            <option value="image">图像检测</option>
            <option value="video">视频检测</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>时间筛选:</label>
          <select v-model="filterTime" @change="filterHistory">
            <option value="all">全部时间</option>
            <option value="today">今天</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
          </select>
        </div>
        
        <div class="search-group">
          <input 
            v-model="searchKeyword" 
            @input="filterHistory" 
            placeholder="搜索检测结果..."
            class="search-input"
          />
        </div>
      </div>
      
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-number">{{ totalRecords }}</span>
          <span class="stat-label">总记录数</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ imageRecords }}</span>
          <span class="stat-label">图像检测</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ videoRecords }}</span>
          <span class="stat-label">视频检测</span>
        </div>
      </div>
      
      <div class="history-list">
        <div v-if="loading" class="loading-state">
          <i class="loading-icon">⏳</i>
          <p>正在加载检测记录...</p>
        </div>
        
        <div v-else-if="filteredHistory.length === 0" class="empty-state">
          <i class="empty-icon">📋</i>
          <p>暂无检测记录</p>
        </div>
        
        <div v-else>
          <div v-for="record in filteredHistory" :key="record.id" class="history-item">
            <div class="item-header">
              <div class="item-type">
                <span :class="['type-badge', record.type]">
                  {{ record.type === 'image' ? '图像' : '视频' }}
                </span>
              </div>
              <div class="item-time">{{ formatTime(record.timestamp) }}</div>
              <div class="item-actions">
                <button @click="viewDetails(record)" class="action-btn view-btn">查看</button>
                <button @click="deleteRecord(record.id)" class="action-btn delete-btn">删除</button>
              </div>
            </div>
            
            <div class="item-content">
              <div class="item-preview">
                <!-- 图像缩略图 -->
                <img v-if="record.type === 'image' && record.thumbnail" :src="record.thumbnail" alt="预览" class="thumbnail" />
                <!-- 视频首帧缩略图（若有） -->
                <img v-else-if="record.type === 'video' && record.thumbnail" :src="record.thumbnail" alt="视频预览" class="thumbnail" />
                <!-- 无缩略图时的占位 -->
                <div v-else class="video-thumbnail">
                  <i class="video-icon">🎬</i>
                  <span>{{ record.duration ? record.duration + 's' : '预览' }}</span>
                </div>
              </div>
              
              <div class="item-details">
                <h4 class="item-title">{{ record.filename }}</h4>
                <div class="detection-summary">
                  <span class="object-count">检测到 {{ record.objectCount }} 个对象</span>
                  <div class="detected-objects">
                    <span v-for="(obj, index) in record.objects.slice(0, 3)" :key="index" class="object-tag">
                      {{ obj.name }}
                    </span>
                    <span v-if="record.objects.length > 3" class="more-objects">
                      +{{ record.objects.length - 3 }}个
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
    
    <!-- 详情弹窗（增强预览） -->
    <div v-if="showDetails" class="modal-overlay" @click="closeDetails">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>检测详情</h3>
          <button @click="closeDetails" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedRecord" class="detail-content">
            <div class="detail-preview">
              <!-- 图像增强预览 -->
              <template v-if="selectedRecord.type === 'image'">
                <img :src="selectedRecord.previewImage || selectedRecord.thumbnail" alt="预览" class="detail-img" @click="openLightbox(selectedRecord.previewImage || selectedRecord.thumbnail)" />
                <div class="detail-toolbar">
                  <button class="tool-btn" @click="openLightbox(selectedRecord.previewImage || selectedRecord.thumbnail)">🔍 放大预览</button>
                  <button class="tool-btn" v-if="selectedRecord.previewImage || selectedRecord.thumbnail" @click="downloadImage(selectedRecord.previewImage || selectedRecord.thumbnail, selectedRecord.filename)">⬇ 下载标注图</button>
                  <button class="tool-btn ask-btn" v-if="selectedRecord.previewImage || selectedRecord.thumbnail" @click="goToQA(selectedRecord.previewImage || selectedRecord.thumbnail)">❓ 去提问</button>
                </div>
              </template>
              
              <!-- 视频增强预览 -->
              <template v-else>
                <div class="video-detail">
                  <div class="video-cover" v-if="selectedRecord.thumbnail">
                    <img :src="selectedRecord.thumbnail" alt="视频封面" class="detail-img" @click="openLightbox(selectedRecord.thumbnail)" />
                  </div>
                  <p>{{ selectedRecord.filename }}</p>
                  <p v-if="selectedRecord.duration">时长: {{ selectedRecord.duration }} 秒</p>
                </div>
                <div v-if="selectedRecord.frames && selectedRecord.frames.length" class="frames-section">
                  <h4>标注帧预览</h4>
                  <div class="frames-grid">
                    <div class="frame-card" v-for="frame in selectedRecord.frames" :key="frame.index">
                      <div class="frame-thumb" @click="openLightbox(frame.annotated)">
                        <img :src="frame.annotated" alt="标注帧" />
                        <span class="frame-time">{{ formatVideoTime(frame.timestamp) }}</span>
                      </div>
                      <div class="frame-meta">
                        第 {{ frame.index + 1 }} 帧 · 对象 {{ frame.objectCount }}
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </div>
            <div class="detail-info">
              <h4>检测结果</h4>
              <div class="objects-list">
                <div v-for="(obj, index) in selectedRecord.objects" :key="index" class="object-detail">
                  <span class="object-name">{{ getClassDisplayText(obj.name) }}</span>
                  <span class="confidence" v-if="obj.confidence !== undefined">置信度: {{ obj.confidence }}%</span>
                  <span class="confidence" v-else-if="obj.count !== undefined">出现次数: {{ obj.count }}</span>
                </div>
              </div>
              <div class="metrics" v-if="selectedRecord.processing_time || selectedRecord.confidence_avg">
                <span v-if="selectedRecord.processing_time">处理时间: {{ (selectedRecord.processing_time).toFixed ? selectedRecord.processing_time.toFixed(2) : selectedRecord.processing_time }}s</span>
                <span v-if="selectedRecord.confidence_avg"> · 平均置信度: {{ Math.round(selectedRecord.confidence_avg) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片放大预览（Lightbox） -->
    <div v-if="lightboxVisible" class="lightbox" @click="closeLightbox">
      <img :src="lightboxImage" alt="放大预览" />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { getClassDisplayText } from '@/utils/classTranslations'

export default {
  name: 'DetectionHistory',
  data() {
    return {
      filterType: 'all',
      filterTime: 'all',
      searchKeyword: '',
      showDetails: false,
      selectedRecord: null,
      historyData: [],
      filteredHistory: [],
      loading: false,
      // 预览增强相关状态
      lightboxVisible: false,
      lightboxImage: ''
    }
  },
  computed: {
    totalRecords() {
      return this.historyData.length
    },
    imageRecords() {
      return this.historyData.filter(item => item.type === 'image').length
    },
    videoRecords() {
      return this.historyData.filter(item => item.type === 'video').length
    }
  },
  mounted() {
    this.loadDetectionHistory()
  },
  methods: {
    // 获取带翻译的类别显示文本
    getClassDisplayText(className) {
      return getClassDisplayText(className)
    },
    async loadDetectionHistory() {
      this.loading = true
      try {
        const response = await axios.get('http://localhost:5002/api/detection-results', {
          params: {
            type: this.filterType !== 'all' ? this.filterType : undefined,
            sort: 'desc',  // 按时间降序排序，最新记录在前
            order_by: 'create_time'  // 按创建时间排序
          }
        })

        if (response.data.success) {
          const { data } = response.data  // 直接获取 data 数组
          this.historyData = this.transformApiData(data)
          this.filterHistory()
        } else {
          console.error('获取检测历史失败:', response.data.error)
          this.$message?.error('获取检测历史失败')
        }
      } catch (error) {
        console.error('API请求失败:', error)
        this.$message?.error('网络请求失败，请检查服务器连接')
      } finally {
        this.loading = false
      }
    },
    
    transformApiData(apiResults) {
      return apiResults.map(item => {
        let objects = []
        let duration = null
        let previewImage = null
        let thumbnail = null
        let frames = []
        let fps = null

        // 图像/视频对象列表
        if (item.detection_result && item.detection_result.objects) {
          // 置信度后端已是百分数，避免再次乘以100
          objects = item.detection_result.objects.map(obj => ({
            name: obj.class || obj.name || '未知对象',
            confidence: Math.round(obj.confidence || 0)
          }))
        }

        // 视频帧与首帧缩略图
        if (item.detection_type === 'video' && item.detection_result && Array.isArray(item.detection_result.frames)) {
          fps = item.detection_result.fps || null
          frames = item.detection_result.frames.map(f => ({
            index: f.frameIndex ?? f.index ?? 0,
            timestamp: f.timestamp ?? 0,
            objectCount: f.objectCount ?? (f.objects ? f.objects.length : 0),
            annotated: f.annotatedFrame || f.annotated || null
          }))
          if (frames.length > 0) {
            thumbnail = frames.find(f => !!f.annotated)?.annotated || null
          }
          // 计算视频时长（秒）
          if (frames.length > 0) {
            const maxTs = Math.max(...frames.map(f => Number(f.timestamp) || 0))
            duration = Math.round(maxTs)
          }
          // 聚合对象（用于视频详情展示）
          if ((!objects || !objects.length) && frames.length) {
            const counter = {}
            frames.forEach(f => {
              (f.objects || []).forEach(o => {
                const key = (o.class || o.name || '未知对象') + ''
                counter[key] = (counter[key] || 0) + 1
              })
            })
            objects = Object.keys(counter).map(name => ({ name, count: counter[name] }))
          }
        }

        // 图像预览/缩略图
        if (item.detection_type === 'image') {
          if (item.detection_result && item.detection_result.annotatedImage) {
            previewImage = item.detection_result.annotatedImage
            thumbnail = previewImage
          } else if (item.file_path) {
            const fileName = (item.file_path + '').split(/[\\/]/).pop()
            thumbnail = `http://localhost:5002/static/uploads/${fileName}`
            previewImage = thumbnail
          }
        }

        // 若仍无缩略图且是视频，尝试从文件路径构造
        if (item.detection_type === 'video' && !thumbnail && item.file_path) {
          const fileName = (item.file_path + '').split(/[\\/]/).pop()
          thumbnail = `http://localhost:5002/static/uploads/${fileName}`
        }
        
        return {
          id: item.id,
          type: item.detection_type,
          filename: item.file_name,
          timestamp: new Date(item.create_time || item.timestamp || Date.now()),
          thumbnail,
          previewImage,
          duration,
          frames,
          fps,
          objectCount: item.object_count || (objects && objects.length) || 0,
          objects,
          confidence_avg: item.confidence_avg,
          processing_time: item.processing_time
        }
      })
    },
    
    goBack() {
      this.$router.push('/')
    },
    filterHistory() {
      let filtered = [...this.historyData]
      
      if (this.filterTime !== 'all') {
        const now = new Date()
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        
        filtered = filtered.filter(item => {
          const itemDate = new Date(item.timestamp)
          switch (this.filterTime) {
            case 'today':
              return itemDate >= today
            case 'week':
              const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
              return itemDate >= weekAgo
            case 'month':
              const monthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
              return itemDate >= monthAgo
            default:
              return true
          }
        })
      }
      
      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.toLowerCase()
        filtered = filtered.filter(item => 
          item.filename.toLowerCase().includes(keyword) ||
          item.objects.some(obj => (obj.name || '').toLowerCase().includes(keyword))
        )
      }

      // 按时间倒序排序（最新记录在最前面，越往后越早）
      filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      
      this.filteredHistory = filtered
    },
    
    async onFilterChange() {
      await this.loadDetectionHistory()
    },
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    },
    formatVideoTime(sec) {
      const s = Math.floor(Number(sec) || 0)
      const m = Math.floor(s / 60)
      const rs = s % 60
      return (m > 0 ? (m + ':') : '') + (rs < 10 ? '0' + rs : rs)
    },
    viewDetails(record) {
      this.selectedRecord = record
      this.showDetails = true
    },
    closeDetails() {
      this.showDetails = false
      this.selectedRecord = null
    },
    async deleteRecord(id) {
      if (confirm('确定要删除这条记录吗？')) {
        try {
          this.historyData = this.historyData.filter(item => item.id !== id)
          this.filterHistory()
          this.$message?.success('删除成功')
        } catch (error) {
          console.error('删除失败:', error)
          this.$message?.error('删除失败，请重试')
        }
      }
    },
    // 预览增强
    openLightbox(src) {
      if (!src) return
      this.lightboxImage = src
      this.lightboxVisible = true
    },
    closeLightbox() {
      this.lightboxVisible = false
      this.lightboxImage = ''
    },
    downloadImage(src, filename = 'annotated.jpg') {
      try {
        const a = document.createElement('a')
        a.href = src
        a.download = filename || 'annotated.jpg'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
      } catch (e) {
        console.error('下载失败', e)
      }
    },

    // 跳转到智能问答页面
    goToQA(imageUrl) {
      if (!imageUrl) {
        alert('没有可用的图片进行提问')
        return
      }

      try {
        // 将图片数据存储到sessionStorage中
        const qaData = {
          image: imageUrl,
          question: '解释一下这是什么',
          source: 'detection-history',
          timestamp: Date.now()
        }

        sessionStorage.setItem('qa_image_data', JSON.stringify(qaData))

        // 跳转到智能问答页面，带上标识参数
        this.$router.push({
          name: 'IntelligentQA',
          query: {
            from: 'detection',
            auto_ask: 'true'
          }
        })

        // 关闭详情弹窗
        this.closeDetails()

      } catch (error) {
        console.error('跳转到问答页面失败:', error)
        alert('跳转失败，请重试')
      }
    }
  }
}
</script>

<style scoped>
.detection-history {
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
  max-width: 1000px;
  margin: 0 auto;
}

.filter-bar {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #333;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: white;
}

.search-group {
  flex: 1;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.stats-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
  flex: 1;
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.history-list {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon, .loading-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 15px;
}

.loading-icon {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.history-item {
  border-bottom: 1px solid #eee;
  padding: 20px;
}

.history-item:last-child {
  border-bottom: none;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.type-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.image {
  background: #e3f2fd;
  color: #1976d2;
}

.type-badge.video {
  background: #f3e5f5;
  color: #7b1fa2;
}

.item-time {
  color: #666;
  font-size: 14px;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.3s;
}

.view-btn {
  background: #007bff;
  color: white;
}

.view-btn:hover {
  background: #0056b3;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.delete-btn:hover {
  background: #c82333;
}

.item-content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.item-preview {
  flex-shrink: 0;
}

.thumbnail {
  width: 120px;
  height: 80px;
  object-fit: cover;
  border-radius: 5px;
}

.video-thumbnail {
  width: 120px;
  height: 80px;
  background: #f8f9fa;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #dee2e6;
}

.video-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.item-details {
  flex: 1;
}

.item-title {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
}

.detection-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.object-count {
  color: #666;
  font-size: 14px;
}

.detected-objects {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.object-tag {
  background: #e9ecef;
  color: #495057;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 12px;
}

.more-objects {
  background: #6c757d;
  color: white;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 12px;
}


/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  max-width: 900px;
  width: 92%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-preview {
  text-align: center;
}

.detail-img {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  cursor: zoom-in;
}

.detail-toolbar {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.tool-btn {
  padding: 6px 10px;
  background: #f1f3f5;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.tool-btn:hover {
  background: #e9ecef;
}

.ask-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: none !important;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.ask-btn:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.video-detail {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.frames-section {
  margin-top: 10px;
}

.frames-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.frame-card {
  background: #ffffff;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.frame-thumb {
  position: relative;
  width: 100%;
  padding-top: 66%; /* 3:2 */
  overflow: hidden;
  cursor: zoom-in;
}

.frame-thumb img {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.frame-time {
  position: absolute;
  right: 6px;
  bottom: 6px;
  background: rgba(0,0,0,0.6);
  color: #fff;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.frame-meta {
  font-size: 12px;
  color: #666;
  padding: 6px 8px;
}

.detail-info {
  margin-top: 10px;
}

.objects-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.object-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
}

.object-name {
  font-weight: 500;
  color: #333;
}

.confidence {
  color: #28a745;
  font-size: 14px;
}

.metrics {
  margin-top: 8px;
  color: #666;
}

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.lightbox img {
  max-width: 92vw;
  max-height: 92vh;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-bar {
    flex-direction: column;
  }
  
  .item-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .item-content {
    flex-direction: column;
  }
  
  .pagination {
    flex-direction: column;
    gap: 10px;
  }
}
</style>