<template>
  <div class="knowledge-base">
    <div class="header">
      <h1>知识库管理</h1>
      <button @click="goBack" class="back-btn">返回</button>
    </div>
    
    <div class="content">
      <!-- 知识库内容 -->
      <div class="knowledge-content">
        <div class="search-section">
          <div class="search-container">
            <input 
              v-model="searchQuery" 
              @keyup.enter="searchKnowledge"
              type="text" 
              placeholder="请输入关键词搜索知识条目..."
              class="search-input"
            />
            <button @click="searchKnowledge" class="search-btn">
              <i>🔍</i> 查询
            </button>
          </div>
          
          <div class="search-stats">
            <span class="total-count">共 {{ filteredKnowledgeList.length }} 条知识条目</span>
            <div class="filter-options">
              <select v-model="selectedCategory" @change="filterByCategory" class="category-select">
                <option value="">全部分类</option>
                <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="knowledge-list">
          <div class="list-header">
            <div class="header-item title-col">标题</div>
            <div class="header-item category-col">分类</div>
            <div class="header-item date-col">更新时间</div>
            <div class="header-item action-col">操作</div>
          </div>
          
          <div class="list-body">
            <div 
              v-for="(item, index) in paginatedKnowledgeList" 
              :key="item.id" 
              class="knowledge-item"
              :class="{ 'expanded': expandedItems.includes(item.id) }"
            >
              <div class="item-row" @click="toggleExpand(item.id)">
                <div class="item-cell title-col">
                  <i class="expand-icon" :class="{ 'expanded': expandedItems.includes(item.id) }">▶</i>
                  <span class="item-title">{{ item.title }}</span>
                </div>
                <div class="item-cell category-col">
                  <span class="category-tag" :class="getCategoryClass(item.category)">{{ item.category }}</span>
                </div>
                <div class="item-cell date-col">{{ formatDate(item.updateTime) }}</div>
                <div class="item-cell action-col">
                  <button @click.stop="editKnowledge(item)" class="action-btn edit-btn">
                    <i>✏️</i>
                  </button>
                  <button @click.stop="deleteKnowledge(item.id)" class="action-btn delete-btn">
                    <i>🗑️</i>
                  </button>
                </div>
              </div>
              
              <div v-if="expandedItems.includes(item.id)" class="item-content">
                <div class="content-section">
                  <h4>内容摘要</h4>
                  <p>{{ item.summary }}</p>
                </div>
                <div class="content-section">
                  <h4>详细内容</h4>
                  <div class="content-text">{{ item.content }}</div>
                </div>
                <div class="content-section">
                  <h4>关键词</h4>
                  <div class="keywords">
                    <span v-for="keyword in item.keywords" :key="keyword" class="keyword-tag">{{ keyword }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="filteredKnowledgeList.length === 0" class="empty-state">
              <div class="empty-content">
                <i class="empty-icon">📚</i>
                <h3>暂无知识条目</h3>
                <p v-if="searchQuery">未找到与"{{ searchQuery }}"相关的知识条目</p>
                <p v-else>知识库为空，请添加知识条目</p>
              </div>
            </div>
          </div>
          
          <div v-if="totalPages > 1" class="pagination">
            <button 
              @click="currentPage = Math.max(1, currentPage - 1)" 
              :disabled="currentPage === 1"
              class="page-btn"
            >
              上一页
            </button>
            
            <span class="page-info">
              第 {{ currentPage }} 页，共 {{ totalPages }} 页
            </span>
            
            <button 
              @click="currentPage = Math.min(totalPages, currentPage + 1)" 
              :disabled="currentPage === totalPages"
              class="page-btn"
            >
              下一页
            </button>
          </div>
        </div>
        
        <div class="action-bar">
          <button @click="addKnowledge" class="primary-btn">
            <i>➕</i> 添加知识条目
          </button>
          <button @click="exportKnowledge" class="secondary-btn">
            <i>💾</i> 导出知识库
          </button>
          <button @click="importKnowledge" class="secondary-btn">
            <i>📁</i> 导入知识库
          </button>
        </div>
      </div>


    </div>
  </div>
</template>

<script>
export default {
  name: 'KnowledgeBase',
  data() {
    return {
      // 知识库相关
      searchQuery: '',
      selectedCategory: '',
      expandedItems: [],
      currentPage: 1,
      itemsPerPage: 10,
      knowledgeList: [],
      categories: [],
      loading: false,
      refreshTimer: null,
      
      apiBaseUrl: 'http://localhost:5002/api'
    }
  },
  computed: {
    filteredKnowledgeList() {
      // 由于现在使用后端API进行过滤，直接返回knowledgeList
      return this.knowledgeList
    },
    paginatedKnowledgeList() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredKnowledgeList.slice(start, end)
    },
    totalPages() {
      return Math.ceil(this.filteredKnowledgeList.length / this.itemsPerPage)
    }
  },
  watch: {
    filteredKnowledgeList() {
      // 当筛选结果改变时，重置到第一页
      this.currentPage = 1
    }
  },
  methods: {
    // 知识库相关方法
    async fetchKnowledge() {
      try {
        this.loading = true
        const params = new URLSearchParams()
        
        if (this.searchQuery.trim()) {
          params.append('search', this.searchQuery.trim())
        }
        
        if (this.selectedCategory) {
          params.append('category', this.selectedCategory)
        }
        
        const response = await fetch(`${this.apiBaseUrl}/knowledge?${params}`)
        const result = await response.json()
        
        if (result.success) {
          this.knowledgeList = result.data.map(item => ({
            ...item,
            updateTime: new Date(item.updateTime)
          }))
        } else {
          console.error(result.message || '获取数据失败')
          this.$message?.error(result.message || '获取知识库数据失败')
        }
      } catch (error) {
        console.error('获取知识库数据失败:', error)
        this.$message?.error('网络错误，请检查后端服务是否启动')
      } finally {
        this.loading = false
      }
    },
    
    async fetchCategories() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/categories`)
        const result = await response.json()
        
        if (result.success) {
          this.categories = result.data
        }
      } catch (error) {
        console.error('获取分类失败:', error)
        this.$message?.error('获取分类失败，请检查网络连接')
      }
    },
    
    // 通用方法
    goBack() {
      this.$router.push('/')
    },
    searchKnowledge() {
      this.currentPage = 1
      this.fetchKnowledge()
    },
    filterByCategory() {
      this.currentPage = 1
      this.fetchKnowledge()
    },
    toggleExpand(id) {
      const index = this.expandedItems.indexOf(id)
      if (index > -1) {
        this.expandedItems.splice(index, 1)
      } else {
        this.expandedItems.push(id)
      }
    },
    getCategoryClass(category) {
      const classMap = {
        '图像检测': 'category-image',
        '视频分析': 'category-video',
        '系统使用': 'category-system',
        '技术支持': 'category-support'
      }
      return classMap[category] || 'category-default'
    },
    formatDate(date) {
      return date.toLocaleDateString('zh-CN')
    },
    formatDateTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    editKnowledge(item) {
      alert(`编辑知识条目: ${item.title}\n\n此功能正在开发中...`)
    },
    async deleteKnowledge(id) {
      if (confirm('确定要删除这个知识条目吗？')) {
        try {
          this.loading = true
          const response = await fetch(`${this.apiBaseUrl}/knowledge/${id}`, {
            method: 'DELETE'
          })
          
          const result = await response.json()
          
          if (result.success) {
            this.fetchKnowledge()
            this.fetchCategories()
            this.$message?.success('删除成功')
          } else {
            this.$message?.error(result.message || '删除失败')
          }
        } catch (error) {
          console.error('删除知识条目失败:', error)
          this.$message?.error('网络错误，删除失败')
        } finally {
          this.loading = false
        }
      }
    },
    async addKnowledge() {
      // 显示添加知识条目的对话框
      const title = prompt('请输入知识条目标题:')
      if (!title || !title.trim()) {
        return
      }
      
      const content = prompt('请输入知识条目内容:')
      if (!content || !content.trim()) {
        return
      }
      
      const category = prompt('请输入分类（可选）:', '未分类')
      const keywordsStr = prompt('请输入关键词（用逗号分隔，可选）:', '')
      const keywords = keywordsStr ? keywordsStr.split(',').map(k => k.trim()).filter(k => k) : []
      
      try {
        this.loading = true
        const response = await fetch(`${this.apiBaseUrl}/knowledge`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: title.trim(),
            content: content.trim(),
            category: category?.trim() || '未分类',
            keywords: keywords
          })
        })
        
        const result = await response.json()
        
        if (result.success) {
          this.fetchKnowledge()
          this.fetchCategories()
          this.$message?.success('添加成功')
        } else {
          this.$message?.error(result.message || '添加失败')
        }
      } catch (error) {
        console.error('添加知识条目失败:', error)
        this.$message?.error('网络错误，添加失败')
      } finally {
        this.loading = false
      }
    },
    async editKnowledge(item) {
      // 显示编辑知识条目的对话框
      const title = prompt('请修改知识条目标题:', item.title)
      if (title === null) return // 用户取消
      
      if (!title.trim()) {
        this.$message?.error('标题不能为空')
        return
      }
      
      const content = prompt('请修改知识条目内容:', item.content)
      if (content === null) return // 用户取消
      
      if (!content.trim()) {
        this.$message?.error('内容不能为空')
        return
      }
      
      const category = prompt('请修改分类:', item.category || '未分类')
      if (category === null) return // 用户取消
      
      const keywordsStr = prompt('请修改关键词（用逗号分隔）:', (item.keywords || []).join(', '))
      if (keywordsStr === null) return // 用户取消
      
      const keywords = keywordsStr ? keywordsStr.split(',').map(k => k.trim()).filter(k => k) : []
      
      try {
        this.loading = true
        const response = await fetch(`${this.apiBaseUrl}/knowledge/${item.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: title.trim(),
            content: content.trim(),
            category: category?.trim() || '未分类',
            keywords: keywords
          })
        })
        
        const result = await response.json()
        
        if (result.success) {
          this.fetchKnowledge()
          this.fetchCategories()
          this.$message?.success('更新成功')
        } else {
          this.$message?.error(result.message || '更新失败')
        }
      } catch (error) {
        console.error('更新知识条目失败:', error)
        this.$message?.error('网络错误，更新失败')
      } finally {
        this.loading = false
      }
    },
    exportKnowledge() {
      const data = JSON.stringify(this.knowledgeList, null, 2)
      const blob = new Blob([data], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `知识库导出_${new Date().toISOString().split('T')[0]}.json`
      link.click()
      URL.revokeObjectURL(url)
    },
    importKnowledge() {
      // 创建文件输入元素
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.json'
      input.style.display = 'none'
      
      input.onchange = async (event) => {
        const file = event.target.files[0]
        if (!file) return
        
        try {
          this.loading = true
          
          // 读取文件内容
          const text = await this.readFileAsText(file)
          let data
          
          try {
            data = JSON.parse(text)
          } catch (e) {
            this.$message?.error('文件格式错误，请确保是有效的JSON文件')
            return
          }
          
          // 验证数据格式
          if (!Array.isArray(data)) {
            this.$message?.error('数据格式错误，应为数组格式')
            return
          }
          
          if (data.length === 0) {
            this.$message?.error('文件为空，没有可导入的数据')
            return
          }
          
          // 显示确认对话框
          const confirmed = confirm(`确定要导入 ${data.length} 条知识库记录吗？`)
          if (!confirmed) return
          
          // 调用后端API导入数据
          const response = await fetch(`${this.apiBaseUrl}/knowledge/import`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
          })
          
          const result = await response.json()
          
          if (result.success) {
            // 显示导入结果
            const { successCount, errorCount, totalCount, errors } = result.data
            let message = `导入完成！\n成功：${successCount} 条\n失败：${errorCount} 条\n总计：${totalCount} 条`
            
            if (errors && errors.length > 0) {
              message += '\n\n错误详情：\n' + errors.join('\n')
            }
            
            alert(message)
            
            // 刷新知识库列表
            this.fetchKnowledge()
            this.fetchCategories()
            
            this.$message?.success(result.message)
          } else {
            this.$message?.error(result.error || '导入失败')
          }
          
        } catch (error) {
          console.error('导入知识库失败:', error)
          this.$message?.error('导入失败，请检查文件格式和网络连接')
        } finally {
          this.loading = false
          // 清理文件输入元素
          document.body.removeChild(input)
        }
      }
      
      // 添加到DOM并触发点击
      document.body.appendChild(input)
      input.click()
    },
    
    // 辅助方法：读取文件内容
    readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.onerror = (e) => reject(e)
        reader.readAsText(file, 'utf-8')
      })
    }
  },
  
  mounted() {
    this.fetchKnowledge()
    this.fetchCategories()
    
    // 设置定时器，每30秒自动刷新数据
    this.refreshTimer = setInterval(() => {
      this.fetchKnowledge()
    }, 30000)
  },
  
  beforeDestroy() {
    // 清除定时器
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
    }
  }
}
</script>

<style scoped>
.knowledge-base {
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
}

/* 知识库内容样式 */
.knowledge-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.search-section {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.search-input, .type-filter, .category-select {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.search-input:focus, .type-filter:focus, .category-select:focus {
  outline: none;
  border-color: #007bff;
}

.search-btn {
  padding: 12px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.search-btn:hover {
  background: #0056b3;
}

.search-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-count {
  color: #666;
  font-size: 14px;
}

.filter-options {
  display: flex;
  gap: 10px;
}

.knowledge-list {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  font-weight: bold;
  color: #495057;
}

.header-item {
  padding: 15px;
  border-right: 1px solid #dee2e6;
}

.header-item:last-child {
  border-right: none;
}

/* 知识库列表列宽 */
.title-col {
  flex: 2;
}

.category-col {
  flex: 1;
}

.date-col {
  flex: 1;
}

.action-col {
  flex: 0.8;
}

/* 检测记录列表列宽 */
.type-col {
  flex: 0.8;
}

.file-col {
  flex: 1.5;
}

.objects-col {
  flex: 0.8;
}

.confidence-col {
  flex: 1;
}

.time-col {
  flex: 1;
}

.list-body {
  max-height: 600px;
  overflow-y: auto;
}

.knowledge-item, .detection-item {
  border-bottom: 1px solid #eee;
}

.knowledge-item:last-child, .detection-item:last-child {
  border-bottom: none;
}

.item-row {
  display: flex;
  cursor: pointer;
  transition: background 0.3s;
}

.item-row:hover {
  background: #f8f9fa;
}

.item-cell {
  padding: 15px;
  border-right: 1px solid #eee;
  display: flex;
  align-items: center;
}

.item-cell:last-child {
  border-right: none;
}

.expand-icon {
  margin-right: 8px;
  transition: transform 0.3s;
  color: #666;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.item-title {
  font-weight: 500;
  color: #333;
}

.category-tag, .type-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.category-image {
  background: #e3f2fd;
  color: #1976d2;
}

.category-video {
  background: #f3e5f5;
  color: #7b1fa2;
}

.category-system {
  background: #e8f5e8;
  color: #388e3c;
}

.category-support {
  background: #fff3e0;
  color: #f57c00;
}

.category-default {
  background: #f5f5f5;
  color: #666;
}

.type-tag.image {
  background: #e3f2fd;
  color: #1976d2;
}

.type-tag.video {
  background: #f3e5f5;
  color: #7b1fa2;
}

.action-btn {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
  transition: all 0.3s;
  font-size: 12px;
}

.edit-btn {
  background: #28a745;
  color: white;
}

.edit-btn:hover {
  background: #218838;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.delete-btn:hover {
  background: #c82333;
}

.view-btn {
  background: #17a2b8;
  color: white;
}

.view-btn:hover {
  background: #138496;
}

.item-content {
  padding: 20px;
  background: #f8f9fa;
  border-top: 1px solid #eee;
}

.content-section {
  margin-bottom: 15px;
}

.content-section:last-child {
  margin-bottom: 0;
}

.content-section h4 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 14px;
}

.content-text {
  color: #666;
  line-height: 1.6;
  max-height: 100px;
  overflow-y: auto;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.keyword-tag {
  padding: 2px 8px;
  background: #007bff;
  color: white;
  border-radius: 12px;
  font-size: 12px;
}

/* 知识库详情样式 */

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-content {
  max-width: 300px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-content h3 {
  color: #666;
  margin: 0 0 10px 0;
}

.empty-content p {
  color: #999;
  margin: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
}

.page-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #0056b3;
}

.page-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

.action-bar {
  display: flex;
  gap: 10px;
  justify-content: center;
  padding: 20px;
}

.primary-btn {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.primary-btn:hover {
  background: #0056b3;
}

.secondary-btn {
  padding: 12px 24px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.secondary-btn:hover {
  background: #5a6268;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .tab-buttons {
    flex-direction: column;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .list-header, .item-row {
    flex-direction: column;
  }
  
  .header-item, .item-cell {
    border-right: none;
    border-bottom: 1px solid #eee;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .objects-grid {
    grid-template-columns: 1fr;
  }
  
  .frames-summary {
    flex-direction: column;
    gap: 10px;
  }
}
/* 统一美化样式增强 */
.knowledge-base {
  min-height: 100vh;
  background: linear-gradient(120deg, #eff3ff 0%, #f8f1ff 100%);
  padding: 20px;
}

.search-section,
.knowledge-list,
.action-bar {
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 10px 28px rgba(102, 126, 234, 0.18);
  padding: 16px;
}

.search-input {
  background: rgba(255,255,255,0.9);
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 10px;
  box-shadow: inset 0 0 0 1px rgba(102,126,234,0.12);
}

.search-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
}

.list-header {
  background: rgba(248, 249, 250, 0.85);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 8px;
}

.knowledge-item {
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 10px;
  margin: 10px 0;
  background: rgba(255,255,255,0.95);
  box-shadow: 0 8px 22px rgba(0,0,0,0.08);
}

.item-row:hover {
  background: linear-gradient(135deg, rgba(102,126,234,0.06), rgba(118,75,162,0.06));
}

.category-tag {
  background: linear-gradient(135deg, #e9efff, #f3e9ff);
  color: #4a4a4a;
  box-shadow: inset 0 0 0 1px rgba(102,126,234,0.25);
}

.primary-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  box-shadow: 0 8px 20px rgba(32, 201, 151, 0.35);
}

.secondary-btn {
  background: rgba(255,255,255,0.85);
  color: #444;
  border: 1px solid rgba(0,0,0,0.06);
}

.secondary-btn:hover {
  background: #fff;
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

</style>
}

.expand-icon {
  margin-right: 8px;
  transition: transform 0.3s;
  font-size: 12px;
  color: #666;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.item-title {
  font-weight: 500;
  color: #333;
}

.category-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.category-image {
  background: #e3f2fd;
  color: #1976d2;
}

.category-video {
  background: #f3e5f5;
  color: #7b1fa2;
}

.category-system {
  background: #e8f5e8;
  color: #388e3c;
}

.category-support {
  background: #fff3e0;
  color: #f57c00;
}

.category-default {
  background: #f5f5f5;
  color: #666;
}

.action-btn {
  padding: 6px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 2px;
  transition: background 0.3s;
}

.edit-btn {
  background: #fff3cd;
  color: #856404;
}

.edit-btn:hover {
  background: #ffeaa7;
}

.delete-btn {
  background: #f8d7da;
  color: #721c24;
}

.delete-btn:hover {
  background: #f5c6cb;
}

.item-content {
  padding: 20px;
  background: #f8f9fa;
  border-top: 1px solid #eee;
}

.content-section {
  margin-bottom: 15px;
}

.content-section:last-child {
  margin-bottom: 0;
}

.content-section h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 14px;
}

.content-text {
  line-height: 1.6;
  color: #555;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.keyword-tag {
  padding: 2px 8px;
  background: #e9ecef;
  border-radius: 10px;
  font-size: 12px;
  color: #495057;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 15px;
}

.empty-content h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.page-btn:disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

.action-bar {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.primary-btn {
  padding: 12px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.primary-btn:hover {
  background: #218838;
}

.secondary-btn {
  padding: 12px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.secondary-btn:hover {
  background: #5a6268;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .search-stats {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .list-header,
  .item-row {
    flex-direction: column;
  }
  
  .header-item,
  .item-cell {
    border-right: none;
    border-bottom: 1px solid #eee;
    padding: 10px 15px;
  }
  
  .action-bar {
    flex-direction: column;
  }
}
</style>