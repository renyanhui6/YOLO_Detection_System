<template>
  <div class="intelligent-qa">
    <div class="header">
      <h1>智能问答</h1>
      <button @click="goBack" class="back-btn">返回</button>
    </div>
    
    <div class="content">
      <div class="chat-container">
        <div class="chat-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-content">
              <i class="welcome-icon">🤖</i>
              <h3>欢迎使用智能问答系统</h3>
              <p>您可以询问关于图像检测、视频分析等相关问题</p>
              <div class="quick-questions">
                <h4>快速提问:</h4>
                <div class="question-buttons">
                  <button @click="askQuickQuestion('如何提高图像检测的准确率？')" class="quick-btn">
                    如何提高图像检测的准确率？
                  </button>
                  <button @click="askQuickQuestion('支持哪些视频格式？')" class="quick-btn">
                    支持哪些视频格式？
                  </button>
                  <button @click="askQuickQuestion('检测结果如何导出？')" class="quick-btn">
                    检测结果如何导出？
                  </button>
                  <button @click="askQuickQuestion('如何批量处理图片？')" class="quick-btn">
                    如何批量处理图片？
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-for="(message, index) in messages" :key="index" class="message" :class="message.type">
            <div class="message-avatar">
              <i v-if="message.type === 'user'">👤</i>
              <i v-else-if="message.type === 'system'">⚠️</i>
              <i v-else>🤖</i>
            </div>
            <div class="message-content">
              <!-- 显示图片（如果有） -->
              <div v-if="message.image" class="message-image">
                <img :src="message.image" alt="上传的图片" class="chat-image" @click="openImagePreview(message.image)" />
                <div class="image-label">
                  <span v-if="message.type === 'system'">📸 检测结果图片</span>
                  <span v-else>🖼️ 用户图片</span>
                </div>
              </div>
              <div class="message-text">{{ message.text }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
          
          <div v-if="isTyping" class="message assistant typing">
            <div class="message-avatar">
              <i>🤖</i>
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="chat-input-area">
          <div class="input-container">
            <textarea 
              v-model="currentMessage" 
              @keydown.enter.prevent="sendMessage"
              @input="adjustTextareaHeight"
              placeholder="请输入您的问题..."
              class="message-input"
              ref="messageInput"
              rows="1"
            ></textarea>
            <button 
              @click="sendMessage" 
              :disabled="!currentMessage.trim() || isTyping"
              class="send-btn"
              :title="(!currentMessage.trim() || isTyping) ? '请输入消息或等待回复完成' : '发送消息'"
            >
              <i>📤</i>
            </button>
          </div>
          
          <div class="input-actions">
            <button @click="clearChat" class="action-btn clear-btn">
              <i>🗑️</i> 清空对话
            </button>
            <button @click="exportChat" class="action-btn export-btn">
              <i>💾</i> 导出对话
            </button>
          </div>
        </div>
      </div>
      
      <div class="sidebar">
        <div class="sidebar-section">
          <h4>常见问题</h4>
          <div class="faq-list">
            <div v-for="(faq, index) in faqs" :key="index" class="faq-item" @click="askQuickQuestion(faq.question)">
              <div class="faq-question">{{ faq.question }}</div>
            </div>
          </div>
        </div>
        
        <div class="sidebar-section">
          <h4>使用统计</h4>
          <div class="stats">
            <div class="stat-item">
              <span class="stat-label">今日提问</span>
              <span class="stat-value">{{ todayQuestions }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总提问数</span>
              <span class="stat-value">{{ totalQuestions }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均响应时间</span>
              <span class="stat-value">{{ avgResponseTime }}s</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <div v-if="showImagePreview" class="image-preview-overlay" @click="closeImagePreview">
      <div class="image-preview-container" @click.stop>
        <button class="preview-close-btn" @click="closeImagePreview">×</button>
        <img :src="previewImageUrl" alt="图片预览" class="preview-image" />
        <div class="preview-caption">检测结果图片预览</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IntelligentQA',
  data() {
    return {
      messages: [],
      currentMessage: '',
      isTyping: false,
      isConnected: true,
      todayQuestions: 12,
      totalQuestions: 156,
      avgResponseTime: 1.2,
      faqs: [
        { question: '如何上传图片进行检测？' },
        { question: '支持的图片格式有哪些？' },
        { question: '视频检测需要多长时间？' },
        { question: '检测结果的准确率如何？' },
        { question: '如何查看历史检测记录？' },
        { question: '可以批量处理文件吗？' },
        { question: '检测失败的常见原因？' },
        { question: '如何提高检测速度？' }
      ],
      // 图片预览相关
      showImagePreview: false,
      previewImageUrl: '',
      knowledgeBase: {
        '图像检测': '我们的图像检测系统支持JPG、PNG、GIF等常见格式，采用先进的深度学习算法，能够识别多种对象类型，准确率可达95%以上。',
        '视频检测': '视频检测支持MP4、AVI、MOV等格式，系统会逐帧分析视频内容，提供时间线检测结果，处理时间取决于视频长度和复杂度。',
        '准确率': '我们的检测系统经过大量数据训练，在标准测试集上的准确率超过95%。实际使用中的准确率会受到图像质量、光照条件等因素影响。',
        '格式支持': '图像格式：JPG、JPEG、PNG、GIF、BMP、TIFF；视频格式：MP4、AVI、MOV、WMV、FLV、MKV。',
        '批量处理': '系统支持批量上传和处理，您可以一次选择多个文件进行检测，系统会自动排队处理。',
        '导出结果': '检测结果可以导出为JSON、CSV、PDF等多种格式，方便后续分析和存档。',
        '检测速度': '单张图片检测通常在1-3秒内完成，视频检测速度约为实时播放的2-5倍，具体取决于内容复杂度。'
      }
    }
  },
  mounted() {
    this.adjustTextareaHeight()
    this.checkNetworkConnection()

    // 检查是否从检测历史页面跳转过来
    this.handleFromDetection()
  },
  methods: {
    goBack() {
      this.$router.push('/')
    },
    sendMessage() {
      console.log('sendMessage 被调用')
      console.log('当前消息:', this.currentMessage)
      console.log('是否正在输入:', this.isTyping)
      
      if (!this.currentMessage.trim() || this.isTyping) {
        console.log('发送被阻止 - 消息为空或正在输入')
        return
      }
      
      const userMessage = {
        type: 'user',
        text: this.currentMessage.trim(),
        timestamp: new Date()
      }
      
      console.log('添加用户消息:', userMessage)
      this.messages.push(userMessage)
      const messageText = this.currentMessage.trim()
      this.currentMessage = ''
      this.adjustTextareaHeight()
      
      this.scrollToBottom()
      
      // 调用DeepSeek API
      console.log('调用 API:', messageText)
      this.callDeepSeekAPI(messageText)
    },
    askQuickQuestion(question) {
      this.currentMessage = question
      this.sendMessage()
    },
    async callDeepSeekAPI(message) {
      console.log('callDeepSeekAPI 开始执行:', message)
      this.isTyping = true
      
      try {
        // 构建对话历史
        const history = this.messages
          .filter(msg => msg.type === 'user' || msg.type === 'assistant')
          .slice(-10) // 保留最近10条消息
          .map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.text
          }))
        
        console.log('发送请求到API:', { message, history })
        
        const response = await fetch('http://localhost:3000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: message,
            history: history
          })
        })
        
        console.log('API响应状态:', response.status)
        const result = await response.json()
        console.log('API响应结果:', result)
        
        if (result.success) {
          const aiMessage = {
            type: 'assistant',
            text: result.data.message,
            timestamp: new Date()
          }
          
          console.log('添加AI回复:', aiMessage)
          this.messages.push(aiMessage)
          this.todayQuestions++
          this.totalQuestions++
        } else {
          // 如果API调用失败，显示错误信息
          const errorMessage = {
            type: 'assistant',
            text: `抱歉，${result.message || '服务暂时不可用，请稍后重试'}`,
            timestamp: new Date()
          }
          console.log('API调用失败，添加错误消息:', errorMessage)
          this.messages.push(errorMessage)
        }
        
      } catch (error) {
        console.error('API调用异常:', error)
        
        // 检查是否是网络连接问题
        const errorMessage = {
          type: 'assistant',
          text: '网络连接失败，请检查网络连接后重试。如果问题持续存在，请联系技术支持。',
          timestamp: new Date()
        }
        console.log('添加网络错误消息:', errorMessage)
        this.messages.push(errorMessage)
      } finally {
        console.log('API调用完成，设置isTyping为false')
        this.isTyping = false
        this.scrollToBottom()
      }
     },
     async checkNetworkConnection() {
       try {
         const response = await fetch('http://localhost:3000/api/chat/check-connection')
         const result = await response.json()
         this.isConnected = result.connected
         
         if (!this.isConnected) {
           const warningMessage = {
             type: 'system',
             text: '⚠️ 网络连接异常，智能问答功能可能无法正常使用。请检查网络连接后刷新页面重试。',
             timestamp: new Date()
           }
           this.messages.push(warningMessage)
         }
       } catch (error) {
         console.error('网络连接检查失败:', error)
         this.isConnected = false
         
         const warningMessage = {
           type: 'system',
           text: '⚠️ 无法连接到服务器，智能问答功能暂时不可用。请检查网络连接或联系技术支持。',
           timestamp: new Date()
         }
         this.messages.push(warningMessage)
       }
     },
    generateAIResponse(question) {
      this.isTyping = true
      
      setTimeout(() => {
        let response = this.findBestResponse(question)
        
        const aiMessage = {
          type: 'assistant',
          text: response,
          timestamp: new Date()
        }
        
        this.messages.push(aiMessage)
        this.isTyping = false
        this.scrollToBottom()
        
        // 更新统计
        this.todayQuestions++
        this.totalQuestions++
      }, 1000 + Math.random() * 2000)
    },
    findBestResponse(question) {
      const lowerQuestion = question.toLowerCase()
      
      // 简单的关键词匹配
      for (const [key, value] of Object.entries(this.knowledgeBase)) {
        if (lowerQuestion.includes(key.toLowerCase()) || 
            lowerQuestion.includes(key) ||
            this.containsKeywords(lowerQuestion, key)) {
          return value
        }
      }
      
      // 特定问题的回答
      if (lowerQuestion.includes('如何') || lowerQuestion.includes('怎么')) {
        return '根据您的问题，我建议您查看我们的使用指南。如果您需要具体的操作步骤，请告诉我您想要完成什么任务，我会为您提供详细的指导。'
      }
      
      if (lowerQuestion.includes('支持') || lowerQuestion.includes('格式')) {
        return this.knowledgeBase['格式支持']
      }
      
      if (lowerQuestion.includes('时间') || lowerQuestion.includes('速度')) {
        return this.knowledgeBase['检测速度']
      }
      
      // 默认回答
      return '感谢您的提问！我是智能检测系统的AI助手。我可以帮您解答关于图像检测、视频分析、系统使用等方面的问题。如果您的问题比较具体，请提供更多详细信息，我会尽力为您提供准确的答案。'
    },
    containsKeywords(question, key) {
      const keywords = {
        '图像检测': ['图片', '照片', '图像', '检测', '识别'],
        '视频检测': ['视频', '录像', '影片', '检测', '分析'],
        '准确率': ['准确', '精确', '正确', '可靠'],
        '批量处理': ['批量', '多个', '一次', '同时'],
        '导出结果': ['导出', '保存', '下载', '输出'],
        '检测速度': ['速度', '快慢', '时间', '效率']
      }
      
      const keywordList = keywords[key] || []
      return keywordList.some(keyword => question.includes(keyword))
    },
    formatTime(timestamp) {
      return timestamp.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    adjustTextareaHeight() {
      this.$nextTick(() => {
        const textarea = this.$refs.messageInput
        if (textarea) {
          textarea.style.height = 'auto'
          textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
        }
      })
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    clearChat() {
      if (confirm('确定要清空所有对话记录吗？')) {
        this.messages = []
      }
    },
    exportChat() {
      if (this.messages.length === 0) {
        alert('暂无对话记录可导出')
        return
      }
      
      const chatData = this.messages.map(msg => ({
        type: msg.type === 'user' ? '用户' : 'AI助手',
        content: msg.text,
        time: this.formatTime(msg.timestamp)
      }))
      
      const dataStr = JSON.stringify(chatData, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      
      const link = document.createElement('a')
      link.href = URL.createObjectURL(dataBlob)
      link.download = `智能问答记录_${new Date().toISOString().split('T')[0]}.json`
      link.click()
    },

    // 处理从检测历史页面跳转过来的数据
    handleFromDetection() {
      try {
        // 检查URL参数
        const { from, auto_ask } = this.$route.query

        if (from === 'detection' && auto_ask === 'true') {
          // 从sessionStorage获取图片数据
          const qaDataStr = sessionStorage.getItem('qa_image_data')

          if (qaDataStr) {
            const qaData = JSON.parse(qaDataStr)

            // 验证数据有效性
            if (qaData.image && qaData.question && qaData.source === 'detection-history') {
              // 清除sessionStorage中的数据
              sessionStorage.removeItem('qa_image_data')

              // 添加系统消息，显示接收到的图片
              const systemMessage = {
                type: 'system',
                text: '📸 已接收到来自检测历史的标注图片，正在为您分析...',
                timestamp: new Date(),
                image: qaData.image
              }
              this.messages.push(systemMessage)

              // 设置问题并自动发送
              this.currentMessage = qaData.question

              // 延迟一下让用户看到系统消息，然后自动发送问题
              setTimeout(() => {
                this.sendMessageWithImage(qaData.image)
              }, 1000)
            }
          }
        }
      } catch (error) {
        console.error('处理检测历史数据失败:', error)
      }
    },

    // 发送带图片的消息
    sendMessageWithImage(imageUrl) {
      if (!this.currentMessage.trim() || this.isTyping) return

      const userMessage = {
        type: 'user',
        text: this.currentMessage.trim(),
        timestamp: new Date(),
        image: imageUrl
      }

      this.messages.push(userMessage)
      const messageText = this.currentMessage.trim()
      this.currentMessage = ''
      this.adjustTextareaHeight()

      this.scrollToBottom()

      // 调用API并传递图片信息
      this.callDeepSeekAPIWithImage(messageText, imageUrl)
    },

    // 调用API并传递图片信息
    async callDeepSeekAPIWithImage(message, imageUrl) {
      this.isTyping = true

      try {
        const response = await fetch('http://localhost:3000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: message,
            imageUrl: imageUrl,  // 直接传递图片URL
            context: {
              hasImage: true,
              imageType: 'detection_result',
              originalQuestion: message
            }
          })
        })

        if (!response.ok) {
          throw new Error('网络请求失败')
        }

        const result = await response.json()

        if (result.success) {
          const assistantMessage = {
            type: 'assistant',
            text: result.response || '抱歉，我无法理解您的问题。',
            timestamp: new Date()
          }
          this.messages.push(assistantMessage)
        } else {
          throw new Error(result.error || '获取回复失败')
        }

      } catch (error) {
        console.error('API调用失败:', error)
        const errorMessage = {
          type: 'assistant',
          text: '抱歉，我现在无法回答您的问题。这可能是网络连接问题，请稍后再试。关于检测结果图片，我可以告诉您这通常显示了AI系统识别到的物体，包括物体的类别和置信度。',
          timestamp: new Date()
        }
        this.messages.push(errorMessage)
      } finally {
        this.isTyping = false
        this.scrollToBottom()
      }
    },

    // 打开图片预览
    openImagePreview(imageUrl) {
      this.previewImageUrl = imageUrl
      this.showImagePreview = true
    },

    // 关闭图片预览
    closeImagePreview() {
      this.showImagePreview = false
      this.previewImageUrl = ''
    }
  }
}
</script>

<style scoped>
.intelligent-qa {
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
  gap: 20px;
  height: calc(100vh - 140px);
}

.chat-container {
  flex: 1;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.welcome-content {
  max-width: 500px;
  margin: 0 auto;
}

.welcome-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 20px;
}

.welcome-content h3 {
  color: #333;
  margin-bottom: 10px;
}

.quick-questions {
  margin-top: 30px;
  text-align: left;
}

.quick-questions h4 {
  color: #333;
  margin-bottom: 15px;
}

.question-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quick-btn {
  padding: 12px 16px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  transition: all 0.3s;
  color: #495057;
}

.quick-btn:hover {
  background: #e9ecef;
  border-color: #007bff;
  color: #007bff;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #007bff;
  color: white;
}

.message.assistant .message-avatar {
  background: #28a745;
  color: white;
}

.message.system .message-avatar {
  background: #ffc107;
  color: white;
}

.message.system .message-text {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.message-content {
  flex: 1;
}

.message-text {
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
  line-height: 1.4;
}

.message.user .message-text {
  background: #007bff;
  color: white;
}

.message.assistant .message-text {
  background: #f8f9fa;
  color: #333;
  border: 1px solid #dee2e6;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  text-align: right;
}

.message.assistant .message-time {
  text-align: left;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 18px;
  width: fit-content;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.chat-input-area {
  border-top: 1px solid #eee;
  padding: 20px;
}

.input-container {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  margin-bottom: 15px;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.4;
  max-height: 120px;
  overflow-y: auto;
}

.message-input:focus {
  outline: none;
  border-color: #007bff;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: background 0.3s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #0056b3;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.input-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-btn:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.sidebar {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-section {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
}

.sidebar-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.faq-item {
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  color: #495057;
}

.faq-item:hover {
  background: #e9ecef;
  color: #007bff;
}

.faq-question {
  line-height: 1.3;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.stat-value {
  color: #007bff;
  font-weight: bold;
  font-size: 16px;
}

/* 消息中的图片样式 */
.message-image {
  margin-bottom: 12px;
}

.chat-image {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.chat-image:hover {
  transform: scale(1.02);
}

.image-label {
  margin-top: 4px;
  font-size: 12px;
  color: #666;
  text-align: center;
}

/* 图片预览弹窗样式 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-preview-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.preview-close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.preview-close-btn:hover {
  background: #ff3838;
}

.preview-image {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
}

.preview-caption {
  text-align: center;
  margin-top: 12px;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .content {
    flex-direction: column;
    height: auto;
  }
  
  .chat-container {
    height: 60vh;
  }
  
  .sidebar {
    width: 100%;
  }
  
  .question-buttons {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .input-actions {
    flex-wrap: wrap;
  }
}
/* 统一美化样式增强 */
.intelligent-qa {
  min-height: 100vh;
  background: linear-gradient(120deg, #eff3ff 0%, #f8f1ff 100%);
  padding: 20px;
}

.chat-container,
.sidebar-section {
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 28px rgba(102, 126, 234, 0.18);
}

.message.assistant .message-text {
  background: linear-gradient(135deg, #f8fbff, #fff8ff);
  border: 1px solid rgba(0,0,0,0.06);
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea, #764ba2);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
}

.quick-btn {
  background: linear-gradient(135deg, #f8fbff, #fff8ff);
  border: 1px solid rgba(0,0,0,0.06);
}

.quick-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.send-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border: none;
  border-radius: 10px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: inline-block;
  animation: pulse 1.2s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.4); opacity: 1; }
}

</style>