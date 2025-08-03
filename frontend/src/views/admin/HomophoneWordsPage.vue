<template>
  <div class="homophone-words-page">
    <AdminLayout>
      <template #header>
        <div class="page-header">
          <div class="header-content">
            <div class="title-section">
              <h1 class="page-title">谐音词管理</h1>
              <p class="page-subtitle">管理原词与谐音替换词的映射关系</p>
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
                placeholder="搜索原词、谐音词..."
                @input="handleSearch"
              />
            </div>
          </div>
          
          <div class="action-group">
            <button class="btn btn-secondary" @click="showImportDialog = true">
              <Upload :size="16" />
              批量导入
            </button>
            <button class="btn btn-secondary" @click="exportData">
              <Download :size="16" />
              导出数据
            </button>
            <button class="btn btn-primary" @click="showAddDialog = true">
              <Plus :size="16" />
              添加原词映射
            </button>
          </div>
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon total">
              <Volume2 :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ originalWordsCount }}</div>
              <div class="stat-label">原词总数</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon replacements">
              <MessageSquare :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalReplacements }}</div>
              <div class="stat-label">谐音词总数</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon ratio">
              <TrendingUp :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ averageReplacements }}</div>
              <div class="stat-label">平均替换数</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon priority">
              <Star :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ priorityReplacements }}</div>
              <div class="stat-label">优先替换词</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 现代化数据表格 -->
      <div class="data-table-container">
        <div class="table-header">
          <div class="table-title">
            <span>谐音词映射列表</span>
            <div class="table-count">{{ filteredMappings.length }} 条记录</div>
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
            <div v-if="paginatedMappings.length === 0" class="empty-state">
              <Volume2 :size="48" />
              <h3>暂无数据</h3>
              <p>{{ searchKeyword ? '未找到匹配的原词' : '还没有添加任何原词映射' }}</p>
              <button v-if="!searchKeyword" class="btn btn-primary" @click="showAddDialog = true">
                添加第一个原词映射
              </button>
            </div>
            
            <div v-else class="table-rows">
              <div
                v-for="mapping in paginatedMappings"
                :key="mapping.id"
                class="table-row"
              >
                <div class="row-main">
                  <div class="word-info">
                    <div class="word-text">
                      <span class="word-content">{{ mapping.original_word }}</span>
                      <div class="word-meta">
                        <span class="replacements-count" :class="getReplacementCountClass(mapping.replacements.length)">
                          {{ mapping.replacements.length }} 个谐音词
                        </span>
                        <span class="priority-count" v-if="getPriorityCount(mapping.replacements) > 0">
                          {{ getPriorityCount(mapping.replacements) }} 个优先词
                        </span>
                      </div>
                    </div>
                    
                    <div class="replacements-preview">
                      <div class="replacement-items">
                        <span
                          v-for="(replacement, index) in mapping.replacements.slice(0, 5)"
                          :key="replacement.id"
                          class="replacement-item"
                          :class="{ priority: replacement.priority === 1 }"
                        >
                          {{ replacement.replacement_word }}
                          <Star v-if="replacement.priority === 1" :size="12" />
                        </span>
                        <span v-if="mapping.replacements.length > 5" class="more-count">
                          +{{ mapping.replacements.length - 5 }} 更多
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="word-meta-info">
                    <div class="create-time">
                      <span>创建于 {{ formatDate(mapping.created_at) }}</span>
                    </div>
                    <div class="usage-stats">
                      <span>平均使用次数: {{ getAverageUsage(mapping.replacements) }}</span>
                    </div>
                  </div>
                  
                  <div class="row-actions">
                    <div class="action-buttons">
                      <button
                        class="action-btn view"
                        @click="viewReplacements(mapping)"
                        title="查看谐音词"
                      >
                        <Eye :size="16" />
                      </button>
                      <button
                        class="action-btn edit"
                        @click="editOriginalWord(mapping)"
                        title="编辑"
                      >
                        <Edit2 :size="16" />
                      </button>
                      <button
                        class="action-btn delete"
                        @click="deleteOriginalWordHandler(mapping)"
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
          <div class="modern-pagination" v-if="filteredMappings.length > pageSize">
            <div class="pagination-info">
              显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredMappings.length) }} 条，
              共 {{ filteredMappings.length }} 条记录
            </div>
            
            <div class="pagination-controls">
              <button
                class="page-btn"
                :disabled="currentPage === 1"
                @click="handleCurrentChange(currentPage - 1)"
              >
                <ChevronLeft :size="16" />
              </button>
              
              <div class="page-numbers">
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  class="page-number"
                  :class="{ active: page === currentPage }"
                  @click="handleCurrentChange(page)"
                >
                  {{ page }}
                </button>
              </div>
              
              <button
                class="page-btn"
                :disabled="currentPage === totalPages"
                @click="handleCurrentChange(currentPage + 1)"
              >
                <ChevronRight :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingOriginalWord ? '编辑原词' : '添加原词映射'"
      width="500px"
    >
      <el-form
        ref="originalWordFormRef"
        :model="originalWordForm"
        :rules="originalWordFormRules"
        label-width="80px"
      >
        <el-form-item label="原词" prop="original_word">
          <el-input
            v-model="originalWordForm.original_word"
            placeholder="请输入原词"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="originalWordForm.description"
            type="textarea"
            placeholder="可选：添加描述信息"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="saveOriginalWord"
            :loading="saving"
          >
            {{ editingOriginalWord ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 替换词管理对话框 -->
    <el-dialog
      v-model="showReplacementsDialog"
      :title="`管理「${currentOriginalWord?.original_word}」的替换词`"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="replacements-manager">
        <div class="manager-header">
          <div class="word-info">
            <span class="original-word">{{ currentOriginalWord?.original_word }}</span>
            <span class="word-desc" v-if="currentOriginalWord?.description">
              {{ currentOriginalWord.description }}
            </span>
          </div>
          <el-button 
            type="primary" 
            @click="showAddReplacementForm"
            size="small"
          >
            <Plus :size="16" />
            添加替换词
          </el-button>
        </div>
        
        <div class="replacements-list" v-if="replacements.length > 0">
          <div 
            v-for="replacement in replacements" 
            :key="replacement.id"
            class="replacement-item"
          >
            <div class="replacement-content">
              <div class="replacement-word">
                <span class="word-text">{{ replacement.replacement_word }}</span>
                <div class="word-badges">
                  <el-tag 
                    :type="replacement.priority === 1 ? 'warning' : 'info'"
                    size="small"
                  >
                    {{ replacement.priority === 1 ? '优先推荐' : '普通推荐' }}
                  </el-tag>
                  <el-tag type="success" size="small">
                    置信度: {{ (replacement.confidence_score * 100).toFixed(0) }}%
                  </el-tag>
                  <el-tag size="small">
                    使用次数: {{ replacement.usage_count }}
                  </el-tag>
                </div>
              </div>
              
              <div class="replacement-meta">
                <div class="meta-item" v-if="replacement.description">
                  <span class="meta-label">描述:</span>
                  <span class="meta-value">{{ replacement.description }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">创建时间:</span>
                  <span class="meta-value">{{ formatDate(replacement.created_at) }}</span>
                </div>
              </div>
            </div>
            
            <div class="replacement-actions">
              <button 
                class="action-btn edit-btn"
                @click="editReplacement(replacement)"
                title="编辑替换词"
              >
                <Edit2 :size="14" />
                <span>编辑</span>
              </button>
              <button 
                class="action-btn delete-btn"
                @click="deleteReplacementHandler(replacement)"
                title="删除替换词"
              >
                <Trash2 :size="14" />
                <span>删除</span>
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-replacements">
          <div class="empty-content">
            <MessageSquare :size="48" />
            <h4>暂无替换词</h4>
            <p>为「{{ currentOriginalWord?.original_word }}」添加第一个替换词</p>
            <el-button type="primary" @click="showAddReplacementForm">
              立即添加
            </el-button>
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeReplacementsDialog">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加/编辑替换词对话框 -->
    <el-dialog
      v-model="showAddReplacementDialog"
      :title="editingReplacement ? '编辑替换词' : '添加替换词'"
      width="500px"
    >
      <el-form
        ref="replacementFormRef"
        :model="replacementForm"
        :rules="replacementFormRules"
        label-width="80px"
      >
        <el-form-item label="替换词" prop="replacement_word">
          <el-input
            v-model="replacementForm.replacement_word"
            placeholder="请输入替换词"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="replacementForm.priority" placeholder="选择优先级">
            <el-option label="普通推荐" :value="0" />
            <el-option label="优先推荐" :value="1" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="置信度" prop="confidence_score">
          <el-input-number
            v-model="replacementForm.confidence_score"
            :min="0"
            :max="1"
            :step="0.1"
            :precision="1"
            placeholder="置信度 (0-1)"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="replacementForm.description"
            type="textarea"
            placeholder="可选：添加描述信息"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddReplacementDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="saveReplacement"
            :loading="saving"
          >
            {{ editingReplacement ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入谐音词"
      width="600px"
    >
      <div class="import-container">
        <div class="import-tips">
          <h4>导入说明：</h4>
          <ul>
            <li>支持 Excel (.xlsx) 格式文件</li>
            <li>文件大小不超过 10MB</li>
            <li>必须包含"原词"列</li>
            <li>可选列：原词描述、替换词、优先级、置信度、替换词描述</li>
            <li>优先级填写："优先推荐"或"普通推荐"</li>
            <li>置信度格式：数字或百分比(如：90% 或 0.9)</li>
            <li>重复的原词将被跳过</li>
            <li>导入前请先下载模板文件</li>
          </ul>
        </div>
        
        <div class="template-download">
          <el-button type="primary" link @click="downloadTemplate">
            <Download :size="16" />
            下载导入模板
          </el-button>
        </div>
        
        <el-upload
          :before-upload="handleFileUpload"
          :show-file-list="true"
          :limit="1"
          accept=".xlsx,.xls"
          drag
        >
          <div class="upload-area">
            <Upload :size="48" />
            <div class="upload-text">
              <p>将文件拖到此处，或<span>点击上传</span></p>
              <p class="upload-hint">仅支持 Excel (.xlsx, .xls) 格式文件</p>
            </div>
          </div>
        </el-upload>
        
        <div v-if="importing" class="import-progress">
          <el-progress 
            :percentage="importProgress" 
            :status="importProgress === 100 ? 'success' : 'active'"
          />
          <p>正在导入数据，请稍候...</p>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showImportDialog = false" :disabled="importing">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="importData"
            :loading="importing"
            :disabled="!importFile"
          >
            开始导入
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { 
  Search, 
  Plus, 
  Edit2, 
  Trash2,
  Volume2,
  MessageSquare,
  TrendingUp,
  Star,
  Eye,
  ChevronLeft,
  ChevronRight,
  Upload,
  Download
} from 'lucide-vue-next'

import AdminLayout from '@/components/admin/AdminLayout.vue'
import { 
  getOriginalWords, 
  createOriginalWord, 
  updateOriginalWord, 
  deleteOriginalWord,
  createHomophoneReplacement,
  updateHomophoneReplacement,
  deleteHomophoneReplacement
} from '@/api/homophone-words'

interface HomophoneReplacement {
  id: number
  replacement_word: string
  priority: number
  confidence_score: number
  usage_count: number
  description?: string
  created_at: string
}

interface OriginalWord {
  id: number
  original_word: string
  description?: string
  created_at: string
  updated_at: string
  replacements: HomophoneReplacement[]
}

const loading = ref(false)
const saving = ref(false)

const mappings = ref<OriginalWord[]>([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const showAddDialog = ref(false)
const editingOriginalWord = ref<OriginalWord | null>(null)

const originalWordFormRef = ref<FormInstance>()
const originalWordForm = reactive({
  original_word: '',
  description: ''
})

const originalWordFormRules: FormRules = {
  original_word: [
    { required: true, message: '请输入原词', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const filteredMappings = computed(() => {
  let result = mappings.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(mapping => 
      mapping.original_word.toLowerCase().includes(keyword) ||
      mapping.replacements.some(r => r.replacement_word.toLowerCase().includes(keyword))
    )
  }

  return result
})

const paginatedMappings = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMappings.value.slice(start, end)
})

const originalWordsCount = computed(() => mappings.value.length)

const totalReplacements = computed(() => 
  mappings.value.reduce((sum, mapping) => sum + mapping.replacements.length, 0)
)

const averageReplacements = computed(() => {
  if (mappings.value.length === 0) return '0.0'
  const avg = totalReplacements.value / mappings.value.length
  return avg.toFixed(1)
})

const priorityReplacements = computed(() => 
  mappings.value.reduce((sum, mapping) => 
    sum + mapping.replacements.filter(r => r.priority === 1).length, 0
  )
)

const totalPages = computed(() => Math.ceil(filteredMappings.value.length / pageSize.value))

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2
  const range = []
  const rangeWithDots = []
  
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }
  
  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }
  
  rangeWithDots.push(...range)
  
  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else {
    rangeWithDots.push(total)
  }
  
  return rangeWithDots.filter((item, index, arr) => arr.indexOf(item) === index && item !== 1 || index === 0)
})

// 生命周期
onMounted(async () => {
  await loadMappings()
})

// 方法
const loadMappings = async () => {
  loading.value = true
  try {
    mappings.value = await getOriginalWords()
  } catch (error) {
    console.error('加载谐音词映射失败:', error)
    ElMessage.error('加载谐音词映射失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const editOriginalWord = (word: OriginalWord) => {
  editingOriginalWord.value = word
  Object.assign(originalWordForm, {
    original_word: word.original_word,
    description: word.description || ''
  })
  showAddDialog.value = true
}

const deleteOriginalWordHandler = async (word: OriginalWord) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除原词 "${word.original_word}" 及其所有谐音词吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteOriginalWord(word.id)
    ElMessage.success('删除成功')
    await loadMappings()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除原词失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const saveOriginalWord = async () => {
  if (!originalWordFormRef.value) return
  
  await originalWordFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      if (editingOriginalWord.value) {
        await updateOriginalWord(editingOriginalWord.value.id, originalWordForm)
        ElMessage.success('更新成功')
      } else {
        await createOriginalWord(originalWordForm)
        ElMessage.success('添加成功')
      }
      
      showAddDialog.value = false
      resetOriginalWordForm()
      await loadMappings()
    } catch (error: any) {
      console.error('保存原词失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const resetOriginalWordForm = () => {
  editingOriginalWord.value = null
  Object.assign(originalWordForm, {
    original_word: '',
    description: ''
  })
  originalWordFormRef.value?.clearValidate()
}

// 辅助方法
const getReplacementCountClass = (count: number) => {
  if (count === 0) return 'count-zero'
  if (count <= 2) return 'count-low'
  if (count <= 5) return 'count-medium'
  return 'count-high'
}

const getPriorityCount = (replacements: HomophoneReplacement[]) => {
  return replacements.filter(r => r.priority === 1).length
}

const getAverageUsage = (replacements: HomophoneReplacement[]) => {
  if (replacements.length === 0) return '0'
  const total = replacements.reduce((sum, r) => sum + r.usage_count, 0)
  return (total / replacements.length).toFixed(1)
}

// 替换词管理方法
const showAddReplacementForm = () => {
  editingReplacement.value = null
  resetReplacementForm()
  showAddReplacementDialog.value = true
}

const editReplacement = (replacement: HomophoneReplacement) => {
  editingReplacement.value = replacement
  Object.assign(replacementForm, {
    replacement_word: replacement.replacement_word,
    priority: replacement.priority,
    confidence_score: replacement.confidence_score,
    description: replacement.description || ''
  })
  showAddReplacementDialog.value = true
}

const deleteReplacementHandler = async (replacement: HomophoneReplacement) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除替换词 "${replacement.replacement_word}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteHomophoneReplacement(replacement.id)
    ElMessage.success('删除成功')
    
    // 从本地列表中移除
    const index = replacements.value.findIndex(r => r.id === replacement.id)
    if (index > -1) {
      replacements.value.splice(index, 1)
    }
    
    // 刷新主列表
    await loadMappings()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除替换词失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const saveReplacement = async () => {
  if (!replacementFormRef.value || !currentOriginalWord.value) return
  
  await replacementFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      if (editingReplacement.value) {
        // 更新替换词
        const updated = await updateHomophoneReplacement(
          editingReplacement.value.id,
          replacementForm
        )
        ElMessage.success('更新成功')
        
        // 更新本地列表
        const index = replacements.value.findIndex(r => r.id === editingReplacement.value!.id)
        if (index > -1) {
          replacements.value[index] = updated
        }
      } else {
        // 创建新替换词
        const newReplacement = await createHomophoneReplacement({
          original_word_id: currentOriginalWord.value.id,
          ...replacementForm
        })
        ElMessage.success('添加成功')
        
        // 添加到本地列表
        replacements.value.push(newReplacement)
      }
      
      showAddReplacementDialog.value = false
      resetReplacementForm()
      
      // 刷新主列表
      await loadMappings()
    } catch (error: any) {
      console.error('保存替换词失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const resetReplacementForm = () => {
  editingReplacement.value = null
  Object.assign(replacementForm, {
    replacement_word: '',
    priority: 0,
    confidence_score: 0.8,
    description: ''
  })
  replacementFormRef.value?.clearValidate()
}

const closeReplacementsDialog = () => {
  showReplacementsDialog.value = false
  currentOriginalWord.value = null
  replacements.value = []
}

// 导入导出功能
const exportData = async () => {
  try {
    const { utils, writeFile } = await import('xlsx')
    
    // 准备Excel数据
    const excelData = []
    mappings.value.forEach(mapping => {
      if (mapping.replacements.length === 0) {
        // 没有替换词的原词
        excelData.push({
          '原词': mapping.original_word,
          '原词描述': mapping.description || '',
          '替换词': '',
          '优先级': '',
          '置信度': '',
          '替换词描述': ''
        })
      } else {
        // 有替换词的原词
        mapping.replacements.forEach(replacement => {
          excelData.push({
            '原词': mapping.original_word,
            '原词描述': mapping.description || '',
            '替换词': replacement.replacement_word,
            '优先级': replacement.priority === 1 ? '优先推荐' : '普通推荐',
            '置信度': (replacement.confidence_score * 100).toFixed(0) + '%',
            '替换词描述': replacement.description || ''
          })
        })
      }
    })
    
    const worksheet = utils.json_to_sheet(excelData)
    const workbook = utils.book_new()
    utils.book_append_sheet(workbook, worksheet, '谐音词数据')
    
    const fileName = `谐音词数据-${new Date().toISOString().split('T')[0]}.xlsx`
    writeFile(workbook, fileName)
    
    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleFileUpload = (file: File) => {
  importFile.value = file
  return false // 阻止自动上传
}

const importData = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  
  importing.value = true
  importProgress.value = 0
  
  try {
    const { read, utils } = await import('xlsx')
    
    // 读取Excel文件
    const arrayBuffer = await importFile.value.arrayBuffer()
    const workbook = read(arrayBuffer)
    
    // 获取第一个工作表
    const firstSheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[firstSheetName]
    
    // 转换为JSON数据
    const jsonData = utils.sheet_to_json(worksheet)
    
    if (!Array.isArray(jsonData) || jsonData.length === 0) {
      throw new Error('Excel文件为空或格式错误')
    }
    
    // 验证必要的列
    const firstRow = jsonData[0]
    if (!firstRow['原词']) {
      throw new Error('Excel文件缺少必要的列：原词')
    }
    
    // 按原词分组数据
    const groupedData = new Map()
    
    jsonData.forEach((row: any) => {
      const originalWord = row['原词']?.toString().trim()
      if (!originalWord) return
      
      if (!groupedData.has(originalWord)) {
        groupedData.set(originalWord, {
          original_word: originalWord,
          description: row['原词描述']?.toString().trim() || '',
          replacements: []
        })
      }
      
      // 如果有替换词，添加到替换词列表
      const replacementWord = row['替换词']?.toString().trim()
      if (replacementWord) {
        const priority = row['优先级']?.toString().includes('优先') ? 1 : 0
        let confidenceScore = 0.8
        
        if (row['置信度']) {
          const confidenceStr = row['置信度'].toString().replace('%', '')
          const confidenceNum = parseFloat(confidenceStr) / 100
          if (!isNaN(confidenceNum) && confidenceNum >= 0 && confidenceNum <= 1) {
            confidenceScore = confidenceNum
          }
        }
        
        groupedData.get(originalWord).replacements.push({
          replacement_word: replacementWord,
          priority,
          confidence_score: confidenceScore,
          description: row['替换词描述']?.toString().trim() || ''
        })
      }
    })
    
    const total = groupedData.size
    let processed = 0
    
    for (const [_, item] of groupedData) {
      try {
        // 创建原词
        const originalWord = await createOriginalWord({
          original_word: item.original_word,
          description: item.description
        })
        
        // 创建替换词
        for (const replacement of item.replacements) {
          await createHomophoneReplacement({
            original_word_id: originalWord.id,
            replacement_word: replacement.replacement_word,
            priority: replacement.priority,
            confidence_score: replacement.confidence_score,
            description: replacement.description
          })
        }
        
        processed++
        importProgress.value = Math.round((processed / total) * 100)
      } catch (error: any) {
        console.warn(`导入 "${item.original_word}" 失败:`, error)
      }
    }
    
    await loadMappings()
    showImportDialog.value = false
    importFile.value = null
    ElMessage.success(`导入完成，成功处理 ${processed}/${total} 条记录`)
    
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error(`导入失败: ${error.message}`)
  } finally {
    importing.value = false
    importProgress.value = 0
  }
}

const downloadTemplate = async () => {
  try {
    // 创建一个包含数据验证说明的模板
    const templateData = [
      {
        '原词': '示例原词1',
        '原词描述': '这是一个示例原词的描述',
        '替换词': '示例替换词1',
        '优先级': '优先推荐',
        '置信度': '90%',
        '替换词描述': '这是一个示例替换词的描述'
      },
      {
        '原词': '示例原词1',
        '原词描述': '这是一个示例原词的描述',
        '替换词': '示例替换词2',
        '优先级': '普通推荐',
        '置信度': '80%',
        '替换词描述': '另一个替换词'
      },
      {
        '原词': '示例原词2',
        '原词描述': '另一个示例原词',
        '替换词': '',
        '优先级': '',
        '置信度': '',
        '替换词描述': ''
      }
    ]
    
    // 添加说明表
    const instructionData = [
      { '字段名': '原词', '说明': '必填项，要替换的原始词语', '示例': '敏感词' },
      { '字段名': '原词描述', '说明': '可选项，对原词的描述', '示例': '这是一个需要替换的词' },
      { '字段名': '替换词', '说明': '可选项，用来替换原词的词语', '示例': '和谐词' },
      { '字段名': '优先级', '说明': '可选项，选择：优先推荐 或 普通推荐', '示例': '优先推荐' },
      { '字段名': '置信度', '说明': '可选项，格式：百分比(90%)或小数(0.9)', '示例': '90%' },
      { '字段名': '替换词描述', '说明': '可选项，对替换词的描述', '示例': '这是替换后的词' }
    ]
    
    const { utils, writeFile } = await import('xlsx')
    const workbook = utils.book_new()
    
    // 创建数据表
    const dataWorksheet = utils.json_to_sheet(templateData)
    utils.book_append_sheet(workbook, dataWorksheet, '数据表')
    
    // 创建说明表
    const instructionWorksheet = utils.json_to_sheet(instructionData)
    utils.book_append_sheet(workbook, instructionWorksheet, '填写说明')
    
    // 创建选项表（用于数据验证）
    const optionsData = [
      { '优先级选项': '优先推荐' },
      { '优先级选项': '普通推荐' }
    ]
    const optionsWorksheet = utils.json_to_sheet(optionsData)
    utils.book_append_sheet(workbook, optionsWorksheet, '选项表')
    
    writeFile(workbook, '谐音词导入模板.xlsx')
    
    ElMessage.success('模板下载成功，请查看"填写说明"表了解各字段要求')
  } catch (error) {
    console.error('模板下载失败:', error)
    ElMessage.error('模板下载失败')
  }
}

// 替换词管理相关状态
const showReplacementsDialog = ref(false)
const currentOriginalWord = ref<OriginalWord | null>(null)
const replacements = ref<HomophoneReplacement[]>([])
const showAddReplacementDialog = ref(false)
const editingReplacement = ref<HomophoneReplacement | null>(null)

// 导入导出相关状态
const showImportDialog = ref(false)
const importFile = ref<File | null>(null)
const importProgress = ref(0)
const importing = ref(false)

const replacementFormRef = ref<FormInstance>()
const replacementForm = reactive({
  replacement_word: '',
  priority: 0,
  confidence_score: 0.8,
  description: ''
})

const replacementFormRules: FormRules = {
  replacement_word: [
    { required: true, message: '请输入替换词', trigger: 'blur' },
    { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  confidence_score: [
    { required: true, message: '请输入置信度', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: '置信度范围为 0-1', trigger: 'blur' }
  ]
}

const viewReplacements = (mapping: OriginalWord) => {
  currentOriginalWord.value = mapping
  replacements.value = [...mapping.replacements]
  showReplacementsDialog.value = true
}
</script>

<style lang="scss" scoped>
.homophone-words-page {
  min-height: 100vh;
  background: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

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

// 页面工具栏 - 与违禁词页面相同
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
        
        &.replacements {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
        }
        
        &.ratio {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          color: white;
        }
        
        &.priority {
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

// 现代化按钮系统 - 与违禁词页面相同
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

// 数据表格容器 - 与违禁词页面相同结构，但内容为谐音词特化
.data-table-container {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 32px;
    border-bottom: 1px solid #f3f4f6;
    background: #fafafa;
    
    .table-title {
      display: flex;
      align-items: center;
      gap: 12px;
      
      > span {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
      }
      
      .table-count {
        font-size: 14px;
        color: #6b7280;
        background: #f3f4f6;
        padding: 4px 12px;
        border-radius: 20px;
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
        padding: 80px 32px;
        text-align: center;
        
        svg {
          color: #d1d5db;
          margin-bottom: 16px;
        }
        
        h3 {
          font-size: 18px;
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
          transition: all 0.2s ease;
          
          &:hover {
            background: #f8fafc;
          }
          
          .row-main {
            display: flex;
            align-items: center;
            padding: 24px 32px;
            gap: 24px;
            
            .word-info {
              flex: 1;
              
              .word-text {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 12px;
                
                .word-content {
                  font-size: 16px;
                  font-weight: 600;
                  color: #111827;
                }
                
                .word-meta {
                  display: flex;
                  gap: 8px;
                  
                  .replacements-count,
                  .priority-count {
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                  }
                  
                  .replacements-count {
                    &.count-zero { background: #f3f4f6; color: #6b7280; }
                    &.count-low { background: #fef3c7; color: #d97706; }
                    &.count-medium { background: #dbeafe; color: #2563eb; }
                    &.count-high { background: #f0fdf4; color: #16a34a; }
                  }
                  
                  .priority-count {
                    background: #f3e8ff;
                    color: #8b5cf6;
                  }
                }
              }
              
              .replacements-preview {
                .replacement-items {
                  display: flex;
                  flex-wrap: wrap;
                  gap: 6px;
                  
                  .replacement-item {
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    padding: 3px 8px;
                    background: #f1f5f9;
                    color: #475569;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    
                    &.priority {
                      background: #fef3c7;
                      color: #d97706;
                      
                      svg {
                        color: #f59e0b;
                      }
                    }
                  }
                  
                  .more-count {
                    padding: 3px 8px;
                    background: #e5e7eb;
                    color: #6b7280;
                    border-radius: 6px;
                    font-size: 12px;
                    font-style: italic;
                  }
                }
              }
            }
            
            .word-meta-info {
              text-align: right;
              
              .create-time {
                font-size: 13px;
                color: #9ca3af;
                margin-bottom: 4px;
              }
              
              .usage-stats {
                font-size: 12px;
                color: #6b7280;
              }
            }
            
            .row-actions {
              display: flex;
              align-items: center;
              gap: 16px;
              
              .action-buttons {
                display: flex;
                gap: 4px;
                
                .action-btn {
                  width: 36px;
                  height: 36px;
                  border: none;
                  border-radius: 8px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  cursor: pointer;
                  transition: all 0.2s ease;
                  
                  &.view {
                    color: #6b7280;
                    background: transparent;
                    
                    &:hover {
                      background: #e0e7ff;
                      color: #4f46e5;
                    }
                  }
                  
                  &.edit {
                    color: #6b7280;
                    background: transparent;
                    
                    &:hover {
                      background: #f3f4f6;
                      color: #374151;
                    }
                  }
                  
                  &.delete {
                    color: #ef4444;
                    background: transparent;
                    
                    &:hover {
                      background: #fef2f2;
                      color: #dc2626;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    
    // 现代化分页器 - 与违禁词页面相同
    .modern-pagination {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 32px;
      border-top: 1px solid #f3f4f6;
      background: #fafafa;
      
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
          color: #6b7280;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover:not(:disabled) {
            background: #f9fafb;
            border-color: #d1d5db;
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
            color: #6b7280;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            
            &:hover {
              background: #f9fafb;
              border-color: #d1d5db;
            }
            
            &.active {
              background: #667eea;
              color: white;
              border-color: #667eea;
            }
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .page-toolbar {
    .toolbar-section {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
      
      .search-group {
        justify-content: space-between;
        
        .search-input input {
          width: 100%;
          min-width: 250px;
        }
      }
      
      .action-group {
        justify-content: center;
      }
    }
    
    .stats-cards {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  .data-table-container {
    .table-header {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
    }
    
    .modern-table {
      .table-rows .table-row .row-main {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
        
        .word-meta-info {
          text-align: left;
        }
        
        .row-actions {
          justify-content: space-between;
        }
      }
    }
  }
}

// 替换词管理对话框样式
.replacements-manager {
  .manager-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f0f0f0;
    
    .word-info {
      flex: 1;
      
      .original-word {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin-right: 12px;
      }
      
      .word-desc {
        font-size: 14px;
        color: #666;
        background: #f5f5f5;
        padding: 4px 8px;
        border-radius: 4px;
      }
    }
  }
  
  .replacements-list {
    max-height: 400px;
    overflow-y: auto;
    
    .replacement-item {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 16px;
      margin-bottom: 12px;
      background: #fafafa;
      border: 1px solid #e8e8e8;
      border-radius: 8px;
      transition: all 0.2s ease;
      
      &:hover {
        background: #f0f9ff;
        border-color: #d1e9ff;
      }
      
      .replacement-content {
        flex: 1;
        
        .replacement-word {
          margin-bottom: 12px;
          
          .word-text {
            font-size: 16px;
            font-weight: 500;
            color: #333;
            margin-right: 12px;
          }
          
          .word-badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 8px;
          }
        }
        
        .replacement-meta {
          .meta-item {
            display: flex;
            align-items: center;
            margin-bottom: 4px;
            font-size: 13px;
            
            .meta-label {
              color: #666;
              margin-right: 8px;
              min-width: 60px;
            }
            
            .meta-value {
              color: #333;
            }
          }
        }
      }
      
      .replacement-actions {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-left: 16px;
        
        .action-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          border: none;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          white-space: nowrap;
          
          &.edit-btn {
            background: #f0f9ff;
            color: #0369a1;
            border: 1px solid #e0f2fe;
            
            &:hover {
              background: #e0f2fe;
              border-color: #bae6fd;
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(3, 105, 161, 0.15);
            }
            
            &:active {
              transform: translateY(0);
            }
          }
          
          &.delete-btn {
            background: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
            
            &:hover {
              background: #fee2e2;
              border-color: #fca5a5;
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(220, 38, 38, 0.15);
            }
            
            &:active {
              transform: translateY(0);
            }
          }
          
          span {
            font-weight: 500;
          }
          
          svg {
            flex-shrink: 0;
          }
        }
      }
    }
  }
  
  .empty-replacements {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    
    .empty-content {
      text-align: center;
      
      svg {
        color: #d1d5db;
        margin-bottom: 16px;
      }
      
      h4 {
        font-size: 18px;
        font-weight: 500;
        color: #374151;
        margin-bottom: 8px;
      }
      
      p {
        color: #6b7280;
        margin-bottom: 24px;
      }
    }
  }
}

@media (max-width: 768px) {
  .page-toolbar {
    .stats-cards {
      grid-template-columns: 1fr;
    }
  }
  
  .data-table-container {
    margin: 0 -20px;
    border-radius: 0;
    border-left: none;
    border-right: none;
    
    .table-header,
    .modern-pagination {
      padding: 16px 20px;
    }
    
    .modern-table .table-rows .table-row .row-main {
      padding: 16px 20px;
    }
  }
  
  .replacements-manager {
    .manager-header {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
    }
    
    .replacements-list {
      max-height: 300px;
      
      .replacement-item {
        flex-direction: column;
        align-items: stretch;
        
        .replacement-actions {
          flex-direction: row;
          justify-content: flex-end;
          margin-left: 0;
          margin-top: 12px;
          gap: 8px;
          
          .action-btn {
            padding: 6px 10px;
            font-size: 12px;
            
            span {
              display: none;
            }
            
            svg {
              margin: 0;
            }
          }
        }
      }
    }
  }
}

// 导入对话框样式
.import-container {
  .import-tips {
    margin-bottom: 20px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    
    h4 {
      margin-bottom: 12px;
      color: #333;
      font-size: 16px;
    }
    
    ul {
      margin: 0;
      padding-left: 20px;
      
      li {
        margin-bottom: 4px;
        color: #666;
        font-size: 14px;
      }
    }
  }
  
  .template-download {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .upload-area {
    text-align: center;
    padding: 40px 20px;
    
    svg {
      color: #ddd;
      margin-bottom: 16px;
    }
    
    .upload-text {
      p {
        margin: 8px 0;
        
        &:first-child {
          font-size: 16px;
          color: #333;
          
          span {
            color: #409eff;
            cursor: pointer;
          }
        }
        
        &.upload-hint {
          font-size: 12px;
          color: #999;
        }
      }
    }
  }
  
  .import-progress {
    margin-top: 20px;
    
    p {
      text-align: center;
      margin-top: 8px;
      color: #666;
      font-size: 14px;
    }
  }
}
</style>