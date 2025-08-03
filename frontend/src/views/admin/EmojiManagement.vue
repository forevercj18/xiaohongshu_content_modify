<template>
  <div class="emoji-management-page">
    <AdminLayout>
      <template #header>
        <div class="page-header">
          <div class="header-content">
            <div class="title-section">
              <h1 class="page-title">表情管理</h1>
              <p class="page-subtitle">管理小红书专用表情包，支持[XXR]和[XXH]格式表情</p>
            </div>
          </div>
        </div>
      </template>
      
      <!-- 页面工具栏 -->
      <div class="page-toolbar">
        <div class="toolbar-section">
          <div class="search-group">
            <div class="search-input">
              <Search :size="18" />
              <input
                v-model="searchKeyword"
                placeholder="搜索表情代码、名称..."
                @input="handleSearch"
              />
            </div>
            
            <div class="filter-select">
              <select v-model="selectedType" @change="handleFilter">
                <option value="">所有类型</option>
                <option value="R">R系列</option>
                <option value="H">H系列</option>
              </select>
            </div>
            
            <div class="filter-select">
              <select v-model="selectedCategory" @change="handleFilter">
                <option value="">所有分类</option>
                <option 
                  v-for="cat in categories" 
                  :key="cat.name" 
                  :value="cat.name"
                >
                  {{ cat.display_name }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="action-group">
            <button class="btn btn-secondary" @click="exportData">
              <Download :size="16" />
              导出数据
            </button>
            <button class="btn btn-primary" @click="showAddDialog = true">
              <Plus :size="16" />
              添加表情
            </button>
          </div>
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon total">
              <Smile :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_emojis }}</div>
              <div class="stat-label">表情总数</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon active">
              <CheckCircle :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.active_emojis }}</div>
              <div class="stat-label">已启用</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon usage">
              <TrendingUp :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_usage }}</div>
              <div class="stat-label">总使用次数</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon categories">
              <Grid :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ categories.length }}</div>
              <div class="stat-label">表情分类</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 现代化数据表格 -->
      <div class="data-table-container">
        <div class="table-header">
          <div class="table-title">
            <span>表情列表</span>
            <div class="table-count">{{ filteredEmojis.length }} 条记录</div>
          </div>
          <div class="table-actions">
            <div class="page-size-selector">
              <span>每页显示</span>
              <select v-model="pageSize" @change="handleSizeChange(pageSize)">
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
              <span>条</span>
            </div>
          </div>
        </div>
        
        <div class="modern-table" v-loading="loading">
          <div class="table-content">
            <div v-if="paginatedEmojis.length === 0" class="empty-state">
              <Smile :size="48" />
              <h3>暂无数据</h3>
              <p>{{ searchKeyword ? '未找到匹配的表情' : '还没有添加任何表情' }}</p>
              <button v-if="!searchKeyword" class="btn btn-primary" @click="showAddDialog = true">
                添加第一个表情
              </button>
            </div>
            
            <div v-else class="table-rows">
              <div
                v-for="emoji in paginatedEmojis"
                :key="emoji.id"
                class="table-row"
              >
                <div class="row-main">
                  <div class="emoji-info">
                    <div class="emoji-text">
                      <span class="emoji-code" :class="`type-${emoji.emoji_type.toLowerCase()}`">
                        {{ emoji.code }}
                      </span>
                      <span class="emoji-name">{{ emoji.name }}</span>
                      <div class="emoji-meta">
                        <span class="emoji-type" :class="`badge-${emoji.emoji_type.toLowerCase()}`">
                          {{ emoji.emoji_type }}系列
                        </span>
                        <span class="emoji-category">{{ getCategoryDisplayName(emoji.category) }}</span>
                        <span v-if="emoji.subcategory" class="emoji-subcategory">{{ emoji.subcategory }}</span>
                      </div>
                    </div>
                    
                    <div class="keywords-preview" v-if="emoji.keywords && emoji.keywords.length > 0">
                      <div class="keyword-items">
                        <span
                          v-for="(keyword, index) in emoji.keywords.slice(0, 3)"
                          :key="index"
                          class="keyword-item"
                        >
                          {{ keyword }}
                        </span>
                        <span v-if="emoji.keywords.length > 3" class="more-count">
                          +{{ emoji.keywords.length - 3 }} 更多
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="emoji-meta-info">
                    <div class="priority-info">
                      <span>优先级</span>
                      <div class="priority-stars">
                        <Star 
                          v-for="i in 5" 
                          :key="i" 
                          :size="12" 
                          :class="{ active: i <= emoji.priority }"
                        />
                      </div>
                    </div>
                    <div class="usage-stats">
                      <span>使用次数: {{ emoji.usage_count || 0 }}</span>
                    </div>
                  </div>
                  
                  <div class="row-actions">
                    <div class="status-toggle">
                      <label class="switch">
                        <input 
                          type="checkbox" 
                          :checked="emoji.status === 1"
                          @change="handleStatusChange(emoji)"
                        />
                        <span class="slider"></span>
                      </label>
                      <span class="status-label">{{ emoji.status === 1 ? '已启用' : '已禁用' }}</span>
                    </div>
                    
                    <div class="action-buttons">
                      <button
                        class="action-btn edit"
                        @click="editEmoji(emoji)"
                        title="编辑"
                      >
                        <Edit2 :size="16" />
                      </button>
                      <button
                        class="action-btn delete"
                        @click="deleteEmoji(emoji)"
                        title="删除"
                      >
                        <Trash2 :size="16" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 现代化分页器 -->
          <div class="modern-pagination" v-if="filteredEmojis.length > pageSize">
            <div class="pagination-info">
              <span>
                显示第 {{ (currentPage - 1) * pageSize + 1 }} - 
                {{ Math.min(currentPage * pageSize, filteredEmojis.length) }} 条，
                共 {{ filteredEmojis.length }} 条记录
              </span>
            </div>
            <div class="pagination-controls">
              <button 
                class="page-btn" 
                :disabled="currentPage === 1"
                @click="changePage(currentPage - 1)"
              >
                <ChevronLeft :size="16" />
              </button>
              <div class="page-numbers">
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  class="page-number"
                  :class="{ active: page === currentPage }"
                  @click="changePage(page)"
                >
                  {{ page }}
                </button>
              </div>
              <button 
                class="page-btn" 
                :disabled="currentPage === totalPages"
                @click="changePage(currentPage + 1)"
              >
                <ChevronRight :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>

    <!-- 添加/编辑表情对话框 -->
    <div v-if="showAddDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h2>{{ editingEmoji ? '编辑表情' : '添加表情' }}</h2>
          <button class="close-btn" @click="closeDialog">
            <X :size="20" />
          </button>
        </div>
        
        <div class="dialog-body">
          <div class="form-grid">
            <div class="form-group">
              <label>表情代码 <span class="required">*</span></label>
              <input
                v-model="emojiForm.code"
                type="text"
                placeholder="例: [开心R]"
                :disabled="!!editingEmoji"
                class="form-input"
              />
              <div class="form-hint">格式: [表情名R] 或 [表情名H]</div>
            </div>
            
            <div class="form-group">
              <label>表情名称 <span class="required">*</span></label>
              <input
                v-model="emojiForm.name"
                type="text"
                placeholder="例: 开心"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label>表情类型 <span class="required">*</span></label>
              <div class="radio-group">
                <label class="radio-item">
                  <input type="radio" v-model="emojiForm.emoji_type" value="R" />
                  <span>R系列</span>
                </label>
                <label class="radio-item">
                  <input type="radio" v-model="emojiForm.emoji_type" value="H" />
                  <span>H系列</span>
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <label>分类 <span class="required">*</span></label>
              <select v-model="emojiForm.category" class="form-select">
                <option value="">请选择分类</option>
                <option 
                  v-for="cat in categories" 
                  :key="cat.name" 
                  :value="cat.name"
                >
                  {{ cat.display_name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>子分类</label>
              <input
                v-model="emojiForm.subcategory"
                type="text"
                placeholder="例: 正面情绪"
                class="form-input"
              />
            </div>
            
            <div class="form-group full-width">
              <label>描述</label>
              <textarea
                v-model="emojiForm.description"
                rows="3"
                placeholder="描述表情的使用场景和含义"
                class="form-textarea"
              ></textarea>
            </div>
            
            <div class="form-group full-width">
              <label>关键词</label>
              <input
                v-model="keywordsInput"
                type="text"
                placeholder="输入关键词，用逗号分隔"
                class="form-input"
                @blur="parseKeywords"
              />
              <div class="keywords-preview" v-if="emojiForm.keywords.length > 0">
                <span
                  v-for="keyword in emojiForm.keywords"
                  :key="keyword"
                  class="keyword-tag"
                  @click="removeKeyword(keyword)"
                >
                  {{ keyword }}
                  <X :size="12" />
                </span>
              </div>
            </div>
            
            <div class="form-group">
              <label>优先级</label>
              <div class="priority-selector">
                <Star 
                  v-for="i in 5" 
                  :key="i" 
                  :size="24" 
                  :class="{ active: i <= emojiForm.priority }"
                  @click="emojiForm.priority = i"
                />
                <span class="priority-text">{{ getPriorityText(emojiForm.priority) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="closeDialog">取消</button>
          <button class="btn btn-primary" @click="saveEmoji" :disabled="saving">
            {{ saving ? '保存中...' : (editingEmoji ? '更新' : '创建') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { 
  Search, 
  Download, 
  Plus, 
  Smile, 
  CheckCircle, 
  TrendingUp, 
  Grid,
  Star,
  Edit2, 
  Trash2, 
  ChevronLeft, 
  ChevronRight,
  X
} from 'lucide-vue-next'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { emojiAdminApi, emojiApi } from '@/api/emoji'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const editingEmoji = ref(null)
const searchKeyword = ref('')
const selectedType = ref('')
const selectedCategory = ref('')

const emojis = ref([])
const categories = ref([])
const stats = reactive({
  total_emojis: 0,
  active_emojis: 0,
  total_usage: 0
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)

// 表单数据
const emojiForm = reactive({
  code: '',
  name: '',
  emoji_type: 'R',
  category: '',
  subcategory: '',
  description: '',
  keywords: [],
  priority: 3
})

const keywordsInput = ref('')

// 计算属性
const filteredEmojis = computed(() => {
  let filtered = emojis.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(emoji => 
      emoji.code.toLowerCase().includes(keyword) ||
      emoji.name.toLowerCase().includes(keyword) ||
      (emoji.keywords && emoji.keywords.some(k => k.toLowerCase().includes(keyword)))
    )
  }
  
  if (selectedType.value) {
    filtered = filtered.filter(emoji => emoji.emoji_type === selectedType.value)
  }
  
  if (selectedCategory.value) {
    filtered = filtered.filter(emoji => emoji.category === selectedCategory.value)
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredEmojis.value.length / pageSize.value))

const paginatedEmojis = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEmojis.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

// 方法
const getCategoryDisplayName = (categoryName) => {
  const category = categories.value.find(cat => cat.name === categoryName)
  return category ? category.display_name : categoryName
}

const getPriorityText = (priority) => {
  const texts = ['', '低', '较低', '中等', '较高', '高']
  return texts[priority] || ''
}

const fetchEmojis = async () => {
  loading.value = true
  try {
    const response = await emojiAdminApi.getEmojiList({
      page: 1,
      size: 1000 // 获取所有数据，前端分页
    })
    emojis.value = response.emojis
  } catch (error) {
    console.error('获取表情列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await emojiApi.getCategories()
    categories.value = response.categories
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

const fetchStats = async () => {
  try {
    const response = await emojiAdminApi.getStats()
    Object.assign(stats, response.overview)
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const refreshData = async () => {
  await Promise.all([
    fetchEmojis(),
    fetchCategories(),
    fetchStats()
  ])
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = parseInt(size)
  currentPage.value = 1
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const handleStatusChange = async (emoji) => {
  try {
    const newStatus = emoji.status === 1 ? 0 : 1
    await emojiAdminApi.updateEmoji(emoji.id, { status: newStatus })
    emoji.status = newStatus
    await fetchStats() // 更新统计
  } catch (error) {
    console.error('状态更新失败:', error)
  }
}

const editEmoji = (emoji) => {
  editingEmoji.value = emoji
  Object.assign(emojiForm, {
    code: emoji.code,
    name: emoji.name,
    emoji_type: emoji.emoji_type,
    category: emoji.category,
    subcategory: emoji.subcategory || '',
    description: emoji.description || '',
    keywords: [...(emoji.keywords || [])],
    priority: emoji.priority
  })
  keywordsInput.value = (emoji.keywords || []).join(', ')
  showAddDialog.value = true
}

const deleteEmoji = async (emoji) => {
  if (confirm(`确定要删除表情 "${emoji.code}" 吗？`)) {
    try {
      await emojiAdminApi.deleteEmoji(emoji.id)
      await refreshData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

const parseKeywords = () => {
  const keywords = keywordsInput.value
    .split(',')
    .map(k => k.trim())
    .filter(k => k.length > 0)
  emojiForm.keywords = [...new Set(keywords)] // 去重
}

const removeKeyword = (keyword) => {
  const index = emojiForm.keywords.indexOf(keyword)
  if (index > -1) {
    emojiForm.keywords.splice(index, 1)
    keywordsInput.value = emojiForm.keywords.join(', ')
  }
}

const resetForm = () => {
  editingEmoji.value = null
  Object.assign(emojiForm, {
    code: '',
    name: '',
    emoji_type: 'R',
    category: '',
    subcategory: '',
    description: '',
    keywords: [],
    priority: 3
  })
  keywordsInput.value = ''
}

const closeDialog = () => {
  showAddDialog.value = false
  resetForm()
}

const saveEmoji = async () => {
  try {
    saving.value = true
    
    const data = {
      name: emojiForm.name,
      emoji_type: emojiForm.emoji_type,
      category: emojiForm.category,
      subcategory: emojiForm.subcategory,
      description: emojiForm.description,
      keywords: emojiForm.keywords,
      priority: emojiForm.priority
    }
    
    if (editingEmoji.value) {
      // 更新
      await emojiAdminApi.updateEmoji(editingEmoji.value.id, data)
    } else {
      // 创建
      data.code = emojiForm.code
      await emojiAdminApi.createEmoji(data)
    }
    
    closeDialog()
    await refreshData()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const exportData = () => {
  const csvContent = [
    ['表情代码', '表情名称', '类型', '分类', '子分类', '描述', '关键词', '优先级', '状态', '使用次数'].join(','),
    ...emojis.value.map(emoji => [
      emoji.code,
      emoji.name,
      emoji.emoji_type,
      getCategoryDisplayName(emoji.category),
      emoji.subcategory || '',
      emoji.description || '',
      (emoji.keywords || []).join(';'),
      emoji.priority,
      emoji.status === 1 ? '启用' : '禁用',
      emoji.usage_count || 0
    ].join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `表情数据_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style lang="scss" scoped>
// 基础样式重置和变量
* {
  box-sizing: border-box;
}

// 页面头部
.page-header {
  .header-content {
    .title-section {
      .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
        letter-spacing: -0.025em;
        line-height: 1.2;
      }
      
      .page-subtitle {
        color: #6b7280;
        font-size: 15px;
        font-weight: 400;
        line-height: 1.5;
      }
    }
  }
}

// 页面工具栏
.page-toolbar {
  margin-bottom: 32px;
  
  .toolbar-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
    .search-group {
      display: flex;
      gap: 16px;
      align-items: center;
      
      .search-input {
        position: relative;
        display: flex;
        align-items: center;
        
        svg {
          position: absolute;
          left: 16px;
          color: #9ca3af;
          z-index: 1;
        }
        
        input {
          width: 320px;
          height: 44px;
          padding: 0 16px 0 48px;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          background: white;
          font-size: 14px;
          transition: all 0.2s ease;
          
          &:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          }
          
          &::placeholder {
            color: #9ca3af;
          }
        }
      }
      
      .filter-select {
        select {
          height: 44px;
          padding: 0 16px;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          background: white;
          font-size: 14px;
          color: #374151;
          min-width: 160px;
          transition: all 0.2s ease;
          
          &:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          }
        }
      }
    }
    
    .action-group {
      display: flex;
      gap: 12px;
    }
  }
  
  // 统计卡片
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    
    .stat-card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 16px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      transition: all 0.2s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
      }
      
      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        
        &.total {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }
        
        &.active {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
        }
        
        &.usage {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          color: white;
        }
        
        &.categories {
          background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
          color: white;
        }
      }
      
      .stat-content {
        flex: 1;
        
        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: #111827;
          line-height: 1;
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #6b7280;
          font-weight: 500;
        }
      }
    }
  }
}

// 现代化按钮系统
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  
  &.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.25);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.35);
    }
  }
  
  &.btn-secondary {
    background: white;
    color: #374151;
    border: 1px solid #e5e7eb;
    
    &:hover {
      background: #f9fafb;
      border-color: #d1d5db;
      transform: translateY(-1px);
    }
  }
}

// 数据表格容器
.data-table-container {
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #f3f4f6;
    background: #fafbfc;
    
    .table-title {
      display: flex;
      align-items: center;
      gap: 12px;
      
      span {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
      }
      
      .table-count {
        padding: 4px 12px;
        background: #e5e7eb;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 500;
        color: #6b7280;
      }
    }
    
    .table-actions {
      .page-size-selector {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: #6b7280;
        
        select {
          padding: 6px 12px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: white;
          font-size: 14px;
          color: #374151;
        }
      }
    }
  }
  
  .modern-table {
    .table-content {
      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 20px;
        text-align: center;
        
        svg {
          color: #d1d5db;
          margin-bottom: 16px;
        }
        
        h3 {
          font-size: 20px;
          font-weight: 600;
          color: #374151;
          margin-bottom: 8px;
        }
        
        p {
          color: #6b7280;
          margin-bottom: 24px;
        }
      }
      
      .table-rows {
        .table-row {
          border-bottom: 1px solid #f3f4f6;
          transition: background-color 0.2s ease;
          
          &:hover {
            background: #fafbfc;
          }
          
          .row-main {
            display: flex;
            align-items: center;
            padding: 20px 24px;
            gap: 20px;
            
            .emoji-info {
              flex: 1;
              
              .emoji-text {
                margin-bottom: 8px;
                
                .emoji-code {
                  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                  font-weight: bold;
                  font-size: 16px;
                  margin-right: 12px;
                  
                  &.type-r {
                    color: #10b981;
                  }
                  
                  &.type-h {
                    color: #f59e0b;
                  }
                }
                
                .emoji-name {
                  font-size: 16px;
                  font-weight: 600;
                  color: #111827;
                }
              }
              
              .emoji-meta {
                display: flex;
                gap: 8px;
                align-items: center;
                
                .emoji-type {
                  padding: 2px 8px;
                  border-radius: 12px;
                  font-size: 12px;
                  font-weight: 500;
                  
                  &.badge-r {
                    background-color: #dcfce7;
                    color: #16a34a;
                  }
                  
                  &.badge-h {
                    background-color: #fef3c7;
                    color: #d97706;
                  }
                }
                
                .emoji-category,
                .emoji-subcategory {
                  font-size: 12px;
                  color: #6b7280;
                }
              }
            }
            
            .keywords-preview {
              .keyword-items {
                display: flex;
                flex-wrap: wrap;
                gap: 4px;
                
                .keyword-item {
                  padding: 2px 6px;
                  background-color: #f3f4f6;
                  border-radius: 4px;
                  font-size: 12px;
                  color: #374151;
                }
                
                .more-count {
                  font-size: 12px;
                  color: #9ca3af;
                }
              }
            }
            
            .emoji-meta-info {
              min-width: 140px;
              
              .priority-info {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 4px;
                
                span {
                  font-size: 12px;
                  color: #6b7280;
                }
              }
              
              .usage-stats {
                font-size: 12px;
                color: #6b7280;
              }
            }
            
            .row-actions {
              display: flex;
              flex-direction: column;
              gap: 8px;
              align-items: flex-end;
              
              .status-toggle {
                display: flex;
                align-items: center;
                gap: 8px;
                
                .status-label {
                  font-size: 12px;
                  color: #6b7280;
                }
              }
              
              .action-buttons {
                display: flex;
                gap: 4px;
                
                .action-btn {
                  width: 32px;
                  height: 32px;
                  border: none;
                  border-radius: 8px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  cursor: pointer;
                  transition: all 0.2s ease;
                  
                  &.edit {
                    background: #eff6ff;
                    color: #2563eb;
                    
                    &:hover {
                      background: #dbeafe;
                    }
                  }
                  
                  &.delete {
                    background: #fef2f2;
                    color: #dc2626;
                    
                    &:hover {
                      background: #fee2e2;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    
    .modern-pagination {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 24px;
      border-top: 1px solid #f3f4f6;
      background: #fafbfc;
      
      .pagination-info {
        font-size: 14px;
        color: #6b7280;
      }
      
      .pagination-controls {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .page-btn {
          width: 36px;
          height: 36px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: white;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover:not(:disabled) {
            border-color: #667eea;
            color: #667eea;
          }
          
          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
        }
        
        .page-numbers {
          display: flex;
          gap: 4px;
          
          .page-number {
            width: 36px;
            height: 36px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 14px;
            
            &:hover {
              border-color: #667eea;
              color: #667eea;
            }
            
            &.active {
              background: #667eea;
              border-color: #667eea;
              color: white;
            }
          }
        }
      }
    }
  }
}

/* 表情管理特定样式 */
.priority-stars {
  display: flex;
  gap: 2px;
  
  .lucide {
    color: #e5e7eb;
    cursor: pointer;
    transition: color 0.2s;
    
    &.active {
      color: #fbbf24;
    }
  }
}

.priority-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .lucide {
    color: #e5e7eb;
    cursor: pointer;
    transition: color 0.2s;
    
    &.active {
      color: #fbbf24;
    }
  }
  
  .priority-text {
    font-size: 14px;
    color: #6b7280;
    margin-left: 8px;
  }
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background-color: #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #d1d5db;
  }
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #10b981;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  
  .full-width {
    grid-column: 1 / -1;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #ef4444;
}

.form-input,
.form-select,
.form-textarea {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
  
  &:focus {
    outline: none;
    border-color: #3b82f6;
  }
}

.form-hint {
  font-size: 12px;
  color: #6b7280;
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  cursor: pointer;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  padding: 4px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 4px;
  color: #6b7280;
  
  &:hover {
    background-color: #f3f4f6;
  }
}

.dialog-body {
  padding: 24px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
}
</style>