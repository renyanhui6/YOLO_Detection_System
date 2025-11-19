<template>
  <div class="home">
    <!-- 左侧边栏 -->
    <div class="sidebar">
      <div class="slider-container">
        <div class="slider-track">
          <div class="slider-thumb" @click="openAnnouncement">
            <span class="announcement-label">公告</span>
          </div>
          <div class="slider-button" style="top: 80px;" @click="goToImageDetection">图像检测</div>
          <div class="slider-button" style="top: 140px;" @click="goToVideoDetection">视频检测</div>
          <div class="slider-button" style="top: 200px;" @click="goToDetectionHistory">检测历史</div>
          <div class="slider-button" style="top: 260px;" @click="goToIntelligentQA">智能问答</div>
          <div class="slider-button" style="top: 320px;" @click="goToKnowledgeBase">知识库管理</div>
          <div class="slider-button" style="top: 380px;" @click="goToModelTraining">模型训练</div>
        </div>
      </div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="welcome-section">
        <h1>欢迎使用智能检测系统</h1>
        <div class="feature-grid">
          <div class="feature-card" @click="goToImageDetection">
            <h3>图像检测</h3>
            <p>上传图片进行智能检测分析</p>
          </div>
          <div class="feature-card" @click="goToVideoDetection">
            <h3>视频检测</h3>
            <p>上传视频进行实时检测分析</p>
          </div>
          <div class="feature-card" @click="goToDetectionHistory">
            <h3>检测历史</h3>
            <p>查看历史检测记录和结果</p>
          </div>
          <div class="feature-card" @click="goToIntelligentQA">
            <h3>智能问答</h3>
            <p>获取智能化问题解答服务</p>
          </div>
          <div class="feature-card" @click="goToKnowledgeBase">
            <h3>知识库管理</h3>
            <p>管理和维护知识库内容</p>
          </div>
          <div class="feature-card" @click="goToModelTraining">
            <h3>模型训练</h3>
            <p>训练和优化检测模型</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 公告侧边栏遮罩层 -->
    <div v-if="announcementVisible" class="announcement-overlay" @click="closeAnnouncement"></div>
    
    <!-- 公告侧边栏 -->
    <div class="announcement-sidebar" :class="{ 'announcement-sidebar--open': announcementVisible }">
      <div class="announcement-sidebar__header">
        <h3 class="announcement-sidebar__title">系统公告 / 版本信息</h3>
        <button class="announcement-sidebar__close" @click="closeAnnouncement" aria-label="关闭公告">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="announcement-sidebar__content">
        <div v-if="announcementText" class="announcement-sidebar__text">{{ announcementText }}</div>
        <div v-else class="announcement-sidebar__loading">
          <div class="loading-spinner"></div>
          <span>正在加载公告...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      announcementVisible: false,
      announcementText: '',
      announcementError: ''
    }
  },
  methods: {
    goToImageDetection() {
      this.$router.push('/image-detection')
    },
    goToVideoDetection() {
      this.$router.push('/video-detection')
    },
    goToDetectionHistory() {
      this.$router.push('/detection-history')
    },
    goToIntelligentQA() {
      this.$router.push('/intelligent-qa')
    },
    goToKnowledgeBase() {
      this.$router.push('/knowledge-base')
    },
    goToModelTraining() {
      this.$router.push('/model-training')
    },
    openAnnouncement() {
      this.announcementVisible = true
      this.announcementText = ''
      this.announcementError = ''
      // 避免缓存，加入时间戳
      fetch(`/announcement.txt?ts=${Date.now()}`)
        .then(res => {
          if (!res.ok) throw new Error('公告文件加载失败')
          return res.text()
        })
        .then(text => {
          this.announcementText = text
        })
        .catch(err => {
          this.announcementError = err.message
          this.announcementText = `提示: 未能加载公告文件。\n\n错误信息: ${err.message}\n\n请确认文件存在于 public/announcement.txt 并具有可读权限。`
        })
    },
    closeAnnouncement() {
      this.announcementVisible = false
    }
  }
}
</script>

<style scoped>
/* 新主题变量（仅在本组件作用域内生效） */
.home {
  /* 背景由纯白改为更柔和的浅色渐变 */
  min-height: 100vh;
  background: radial-gradient(1200px 800px at 20% 10%, #eef2ff 0%, transparent 50%),
              radial-gradient(1000px 700px at 90% 20%, #f0f9ff 0%, transparent 45%),
              linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  display: flex;
  flex-direction: row;
}

/* 左侧边栏样式 */
.sidebar {
  width: calc(100vw / 7);
  height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #111827 60%, #0b1220 100%);
  position: relative;
  box-shadow:
    inset -2px 0 4px rgba(0, 0, 0, 0.35),
    inset 2px 0 4px rgba(255, 255, 255, 0.06);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* 滑块容器 */
.slider-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  height: 600px;
}

/* 滑块轨道 */
.slider-track {
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 50%, rgba(2, 6, 23, 0.9) 100%);
  border-radius: 16px;
  position: relative;
  box-shadow:
    inset 0 6px 12px rgba(0, 0, 0, 0.45),
    inset 0 -4px 10px rgba(255, 255, 255, 0.06),
    0 10px 25px rgba(2, 6, 23, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(6px);
}

/* 滑块按钮 */
.slider-thumb {
  width: 90%;
  height: 42px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%);
  border-radius: 12px;
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow:
    0 8px 16px rgba(0, 0, 0, 0.35),
    inset 0 2px 4px rgba(255, 255, 255, 0.18),
    inset 0 -2px 4px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.slider-thumb:hover {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
  box-shadow:
    0 12px 20px rgba(0, 0, 0, 0.45),
    inset 0 2px 6px rgba(255, 255, 255, 0.28),
    inset 0 -2px 4px rgba(0, 0, 0, 0.25);
  transform: translateX(-50%) translateY(-2px);
}

.slider-thumb:active {
  transform: translateX(-50%) translateY(0px);
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.45),
    inset 0 2px 4px rgba(255, 255, 255, 0.1),
    inset 0 -2px 4px rgba(0, 0, 0, 0.35);
}

/* 滑块按钮样式 */
.slider-button {
  width: 85%;
  height: 38px;
  background: linear-gradient(135deg, rgba(55, 65, 81, 0.9) 0%, rgba(31, 41, 55, 0.92) 50%, rgba(17, 24, 39, 0.95) 100%);
  border-radius: 10px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow:
    0 4px 10px rgba(0, 0, 0, 0.35),
    inset 0 1px 2px rgba(255, 255, 255, 0.08),
    inset 0 -1px 3px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e5e7eb;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: .2px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.55);
}

.slider-button:hover {
  background: linear-gradient(135deg, rgba(75, 85, 99, 0.95) 0%, rgba(55, 65, 81, 0.98) 50%, rgba(31, 41, 55, 1) 100%);
  box-shadow:
    0 8px 16px rgba(0, 0, 0, 0.45),
    inset 0 1px 2px rgba(255, 255, 255, 0.16),
    inset 0 -1px 2px rgba(0, 0, 0, 0.25);
  transform: translateX(-50%) translateY(-1px);
  color: #f8fafc;
}

.slider-button:active {
  transform: translateX(-50%) translateY(0px);
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.5),
    inset 0 1px 2px rgba(255, 255, 255, 0.05),
    inset 0 -1px 3px rgba(0, 0, 0, 0.4);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 48px;
  background: transparent;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  max-width: 1200px;
  width: 100%;
}

.welcome-section h1 {
  font-size: 2.75rem;
  margin-bottom: 0.75rem;
  font-weight: 700;
  background: linear-gradient(90deg, #0f172a 0%, #334155 30%, #2563eb 60%, #0ea5e9 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.welcome-section > p {
  font-size: 1.1rem;
  color: #667085;
  margin-bottom: 2.5rem;
}

/* 功能卡片网格 */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.75rem;
  margin-top: 1.5rem;
}

.feature-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.82) 100%);
  border-radius: 14px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(2, 6, 23, 0.08);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  cursor: pointer;
  border: 1px solid rgba(2, 6, 23, 0.06);
  backdrop-filter: blur(6px);
  position: relative;
  overflow: hidden;
  animation: floatIn .6s ease both;
}

.feature-card::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(600px 180px at 0% 0%, rgba(37, 99, 235, 0.12), transparent 40%),
              radial-gradient(600px 180px at 100% 0%, rgba(14, 165, 233, 0.12), transparent 40%);
  opacity: 0.8;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.18);
  border-color: rgba(37, 99, 235, 0.35);
}

.feature-card h3 {
  font-size: 1.4rem;
  color: #0f172a;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.feature-card p {
  color: #475569;
  font-size: 0.98rem;
  line-height: 1.7;
  margin: 0;
}

/* 入场动画与节奏 */
@keyframes floatIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.feature-grid > .feature-card:nth-child(1) { animation-delay: .02s; }
.feature-grid > .feature-card:nth-child(2) { animation-delay: .06s; }
.feature-grid > .feature-card:nth-child(3) { animation-delay: .10s; }
.feature-grid > .feature-card:nth-child(4) { animation-delay: .14s; }
.feature-grid > .feature-card:nth-child(5) { animation-delay: .18s; }
.feature-grid > .feature-card:nth-child(6) { animation-delay: .22s; }

/* 响应式设计 */
@media (max-width: 1200px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .home {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: 82px;
  }
  
  .slider-container {
    width: 220px;
    height: 120px;
  }
  
  .slider-track {
    height: 100%;
  }
  
  .slider-thumb {
    height: 32px;
    top: 15px;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-section h1 {
    font-size: 2.1rem;
  }
  
  .welcome-section > p {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 24px;
  }
  
  .feature-card {
    padding: 1.5rem;
  }
  
  .welcome-section h1 {
    font-size: 1.85rem;
  }
}

/* 公告按钮标签样式 */
.announcement-label {
  display: inline-block;
  width: 100%;
  height: 100%;
  color: #eaf2ff;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.5px;
  text-align: center;
  line-height: 42px; /* 与 slider-thumb 高度一致 */
  text-shadow: 0 1px 2px rgba(0,0,0,0.35);
  pointer-events: none;
}

/* 公告侧边栏样式 */
.announcement-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  z-index: 1000;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  to { opacity: 1; }
}

.announcement-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: min(420px, 85vw);
  height: 100vh;
  background: linear-gradient(180deg, 
    rgba(255, 255, 255, 0.98) 0%, 
    rgba(248, 250, 252, 0.96) 100%);
  backdrop-filter: blur(12px);
  border-left: 1px solid rgba(2, 6, 23, 0.08);
  box-shadow: 
    -8px 0 32px rgba(2, 6, 23, 0.12),
    -4px 0 16px rgba(2, 6, 23, 0.08);
  z-index: 1001;
  transform: translateX(100%);
  transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  display: flex;
  flex-direction: column;
}

.announcement-sidebar--open {
  transform: translateX(0);
}

.announcement-sidebar__header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(2, 6, 23, 0.06);
  background: linear-gradient(135deg, 
    rgba(37, 99, 235, 0.08) 0%, 
    rgba(14, 165, 233, 0.06) 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.announcement-sidebar__title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  background: linear-gradient(90deg, #0f172a 0%, #2563eb 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.announcement-sidebar__close {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #64748b;
  border-radius: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.announcement-sidebar__close:hover {
  background: rgba(2, 6, 23, 0.06);
  color: #0f172a;
  transform: scale(1.05);
}

.announcement-sidebar__close:active {
  transform: scale(0.95);
}

.announcement-sidebar__content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scrollbar-width: thin;
  scrollbar-color: rgba(2, 6, 23, 0.2) transparent;
}

.announcement-sidebar__content::-webkit-scrollbar {
  width: 6px;
}

.announcement-sidebar__content::-webkit-scrollbar-track {
  background: transparent;
}

.announcement-sidebar__content::-webkit-scrollbar-thumb {
  background: rgba(2, 6, 23, 0.2);
  border-radius: 3px;
}

.announcement-sidebar__content::-webkit-scrollbar-thumb:hover {
  background: rgba(2, 6, 23, 0.3);
}

.announcement-sidebar__text {
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #1f2937;
  font-size: 15px;
  line-height: 1.7;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: 0.2px;
}

.announcement-sidebar__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #64748b;
  font-size: 14px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(37, 99, 235, 0.1);
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 公告侧边栏响应式设计 */
@media (max-width: 768px) {
  .announcement-sidebar {
    width: 100vw;
    border-left: none;
  }
  
  .announcement-sidebar__header {
    padding: 16px 20px 12px;
  }
  
  .announcement-sidebar__title {
    font-size: 16px;
  }
  
  .announcement-sidebar__content {
    padding: 20px;
  }
  
  .announcement-sidebar__text {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .announcement-sidebar__header {
    padding: 14px 16px 10px;
  }
  
  .announcement-sidebar__content {
    padding: 16px;
  }
}
</style>