<template>
  <div class="prohibited-words-page">
    <AdminLayout>
      <template #header>
        <div class="page-header">
          <div class="header-content">
            <div class="title-section">
              <h1 class="page-title">违禁词管理</h1>
              <p class="page-subtitle">管理内容检测中使用的违禁词库</p>
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
                placeholder="搜索违禁词、描述..."
                @input="handleSearch"
              />
            </div>
            
            <div class="filter-select">
              <select v-model="selectedCategory" @change="handleFilter">
                <option value="">所有分类</option>
                <option value="political">政治敏感</option>
                <option value="adult">色情低俗</option>
                <option value="violence">暴力血腥</option>
                <option value="commercial">商业广告</option>
                <option value="other">其他</option>
              </select>
            </div>
          </div>
          
          <div class="action-group">
            <button class="btn btn-secondary" @click="showImportDialog = true">
              <Upload :size="16" />
              批量导入
            </button>
            <button class="btn btn-secondary" @click="exportWords">
              <Download :size="16" />
              导出数据
            </button>
            <button class="btn btn-primary" @click="showAddDialog = true">
              <Plus :size="16" />
              添加违禁词
            </button>
          </div>
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon total">
              <AlertTriangle :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredWords.length }}</div>
              <div class="stat-label">违禁词总数</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon active">
              <CheckCircle :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredWords.filter(w => w.is_active).length }}</div>
              <div class="stat-label">已启用</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon disabled">
              <XCircle :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredWords.filter(w => !w.is_active).length }}</div>
              <div class="stat-label">已禁用</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon danger">
              <AlertTriangle :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredWords.filter(w => w.severity === 'high').length }}</div>
              <div class="stat-label">高风险词汇</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 现代化数据表格 -->
      <div class="data-table-container">
        <div class="table-header">
          <div class="table-title">
            <span>违禁词列表</span>
            <div class="table-count">{{ filteredWords.length }} 条记录</div>
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
            <div v-if="paginatedWords.length === 0" class="empty-state">
              <AlertTriangle :size="48" />
              <h3>暂无数据</h3>
              <p>{{ searchKeyword ? '未找到匹配的违禁词' : '还没有添加任何违禁词' }}</p>
              <button v-if="!searchKeyword" class="btn btn-primary" @click="showAddDialog = true">
                添加第一个违禁词
              </button>
            </div>
            
            <div v-else class="table-rows">
              <div
                v-for="word in paginatedWords"
                :key="word.id"
                class="table-row"
                :class="{ disabled: !word.is_active }"
              >
                <div class="row-main">
                  <div class="word-info">
                    <div class="word-text">
                      <span class="word-content">{{ word.word }}</span>
                      <div class="word-meta">
                        <span class="category-badge" :class="`category-${word.category}`">
                          {{ getCategoryText(word.category) }}
                        </span>
                        <span class="severity-badge" :class="`severity-${word.severity}`">
                          {{ getSeverityText(word.severity) }}
                        </span>
                        <span class="status-badge" :class="{ active: word.is_active }">
                          {{ word.is_active ? '已启用' : '已禁用' }}
                        </span>
                      </div>
                    </div>
                    
                    <div class="word-description">
                      {{ word.description || '暂无描述' }}
                    </div>
                  </div>
                  
                  <div class="word-meta-info">
                    <div class="create-time">
                      <span>创建于 {{ formatDate(word.created_at) }}</span>
                    </div>
                  </div>
                  
                  <div class="row-actions">
                    <div class="status-toggle">
                      <label class="toggle-switch">
                        <input
                          type="checkbox"
                          :checked="word.is_active"
                          @change="updateWordStatus(word, $event)"
                        />
                        <span class="toggle-slider"></span>
                      </label>
                    </div>
                    
                    <div class="action-buttons">
                      <button
                        class="action-btn edit"
                        @click="editWord(word)"
                        title="编辑"
                      >
                        <Edit2 :size="16" />
                      </button>
                      <button
                        class="action-btn delete"
                        @click="deleteWord(word)"
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
          <div class="modern-pagination" v-if="filteredWords.length > pageSize">
            <div class="pagination-info">
              显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredWords.length) }} 条，
              共 {{ filteredWords.length }} 条记录
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
      :title="editingWord ? '编辑违禁词' : '添加违禁词'"
      width="500px"
    >
      <el-form
        ref="wordFormRef"
        :model="wordForm"
        :rules="wordFormRules"
        label-width="80px"
      >
        <el-form-item label="违禁词" prop="word">
          <el-input
            v-model="wordForm.word"
            placeholder="请输入违禁词"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select
            v-model="wordForm.category"
            placeholder="选择分类"
            style="width: 100%;"
          >
            <el-option label="政治敏感" value="political" />
            <el-option label="色情低俗" value="adult" />
            <el-option label="暴力血腥" value="violence" />
            <el-option label="商业广告" value="commercial" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="严重程度" prop="severity">
          <el-select
            v-model="wordForm.severity"
            placeholder="选择严重程度"
            style="width: 100%;"
          >
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="wordForm.description"
            type="textarea"
            placeholder="可选：添加描述信息"
            :rows="3"
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch
            v-model="wordForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="saveWord"
            :loading="saving"
          >
            {{ editingWord ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入违禁词"
      width="600px"
    >
      <div class="import-container">
        <div class="import-tips">
          <h4>导入说明：</h4>
          <ul>
            <li>支持 Excel (.xlsx) 格式文件</li>
            <li>文件大小不超过 10MB</li>
            <li>必须包含"违禁词"列</li>
            <li>可选列：分类、严重程度、描述、状态</li>
            <li>分类选项：政治敏感、色情低俗、暴力血腥、商业广告、其他</li>
            <li>严重程度选项：低、中、高</li>
            <li>状态选项：启用、禁用</li>
            <li>重复的违禁词将被跳过</li>
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
  Download, 
  Upload,
  Edit2, 
  Trash2,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'

import AdminLayout from '@/components/admin/AdminLayout.vue'
import { getProhibitedWords, createProhibitedWord, updateProhibitedWord, deleteProhibitedWord } from '@/api/prohibited-words'

interface ProhibitedWord {
  id: number
  word: string
  category: string
  severity: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

const loading = ref(false)
const saving = ref(false)

const words = ref<ProhibitedWord[]>([])
const searchKeyword = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const showAddDialog = ref(false)
const editingWord = ref<ProhibitedWord | null>(null)

// 导入导出相关状态
const showImportDialog = ref(false)
const importFile = ref<File | null>(null)
const importProgress = ref(0)
const importing = ref(false)

const wordFormRef = ref<FormInstance>()
const wordForm = reactive({
  word: '',
  category: '',
  severity: 'medium',
  description: '',
  is_active: true
})

const wordFormRules: FormRules = {
  word: [
    { required: true, message: '请输入违禁词', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  severity: [
    { required: true, message: '请选择严重程度', trigger: 'change' }
  ]
}

// 计算属性
const filteredWords = computed(() => {
  let result = words.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(word => 
      word.word.toLowerCase().includes(keyword) ||
      (word.description && word.description.toLowerCase().includes(keyword))
    )
  }

  if (selectedCategory.value) {
    result = result.filter(word => word.category === selectedCategory.value)
  }

  return result
})

const paginatedWords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredWords.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredWords.value.length / pageSize.value))

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
  await loadWords()
})

// 方法
const loadWords = async () => {
  loading.value = true
  try {
    words.value = await getProhibitedWords()
  } catch (error) {
    console.error('加载违禁词失败:', error)
    ElMessage.error('加载违禁词失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const getCategoryText = (category: string) => {
  const map: Record<string, string> = {
    political: '政治敏感',
    adult: '色情低俗',
    violence: '暴力血腥',
    commercial: '商业广告',
    other: '其他'
  }
  return map[category] || category
}

const getCategoryTagType = (category: string) => {
  const map: Record<string, string> = {
    political: 'danger',
    adult: 'warning',
    violence: 'danger',
    commercial: 'info',
    other: ''
  }
  return map[category] || ''
}

const getSeverityText = (severity: string) => {
  const map: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高'
  }
  return map[severity] || severity
}

const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = {
    low: 'success',
    medium: 'warning',
    high: 'danger'
  }
  return map[severity] || ''
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const editWord = (word: ProhibitedWord) => {
  editingWord.value = word
  Object.assign(wordForm, {
    word: word.word,
    category: word.category,
    severity: word.severity,
    description: word.description || '',
    is_active: word.is_active
  })
  showAddDialog.value = true
}

const deleteWord = async (word: ProhibitedWord) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除违禁词 "${word.word}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteProhibitedWord(word.id)
    ElMessage.success('删除成功')
    await loadWords()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除违禁词失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const updateWordStatus = async (word: ProhibitedWord, event: Event) => {
  const target = event.target as HTMLInputElement
  const newStatus = target.checked
  
  try {
    await updateProhibitedWord(word.id, { is_active: newStatus })
    word.is_active = newStatus // 更新本地状态
    ElMessage.success(newStatus ? '已启用' : '已禁用')
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('更新状态失败')
    // 回滚复选框状态
    target.checked = word.is_active
  }
}

const saveWord = async () => {
  if (!wordFormRef.value) return
  
  await wordFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      if (editingWord.value) {
        await updateProhibitedWord(editingWord.value.id, wordForm)
        ElMessage.success('更新成功')
      } else {
        await createProhibitedWord(wordForm)
        ElMessage.success('添加成功')
      }
      
      showAddDialog.value = false
      resetForm()
      await loadWords()
    } catch (error: any) {
      console.error('保存违禁词失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const resetForm = () => {
  editingWord.value = null
  Object.assign(wordForm, {
    word: '',
    category: '',
    severity: 'medium',
    description: '',
    is_active: true
  })
  wordFormRef.value?.clearValidate()
}

// 导入导出功能
const exportWords = async () => {
  try {
    const { utils, writeFile } = await import('xlsx')
    
    // 准备Excel数据
    const excelData = words.value.map(word => ({
      '违禁词': word.word,
      '分类': getCategoryText(word.category),
      '严重程度': getSeverityText(word.severity),
      '描述': word.description || '',
      '状态': word.is_active ? '启用' : '禁用'
    }))
    
    const worksheet = utils.json_to_sheet(excelData)
    const workbook = utils.book_new()
    utils.book_append_sheet(workbook, worksheet, '违禁词数据')
    
    const fileName = `违禁词数据-${new Date().toISOString().split('T')[0]}.xlsx`
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
    if (!firstRow['违禁词']) {
      throw new Error('Excel文件缺少必要的列：违禁词')
    }
    
    const total = jsonData.length
    let processed = 0
    
    for (const row of jsonData) {
      try {
        const word = row['违禁词']?.toString().trim()
        if (!word) continue
        
        // 分类映射
        const categoryMap: { [key: string]: string } = {
          '政治敏感': 'political',
          '色情低俗': 'adult', 
          '暴力血腥': 'violence',
          '商业广告': 'commercial',
          '其他': 'other'
        }
        
        const categoryText = row['分类']?.toString().trim() || '其他'
        const category = categoryMap[categoryText] || 'other'
        
        // 严重程度映射
        const severityMap: { [key: string]: string } = {
          '低': 'low',
          '中': 'medium',
          '高': 'high'
        }
        
        const severityText = row['严重程度']?.toString().trim() || '中'
        const severity = severityMap[severityText] || 'medium'
        
        // 状态
        const statusText = row['状态']?.toString().trim() || '启用'
        const is_active = statusText === '启用'
        
        await createProhibitedWord({
          word,
          category,
          severity,
          description: row['描述']?.toString().trim() || '',
          is_active
        })
        
        processed++
        importProgress.value = Math.round((processed / total) * 100)
      } catch (error: any) {
        console.warn(`导入 "${row['违禁词']}" 失败:`, error)
      }
    }
    
    await loadWords()
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
        '违禁词': '示例违禁词1',
        '分类': '政治敏感',
        '严重程度': '高',
        '描述': '这是一个示例违禁词的描述',
        '状态': '启用'
      },
      {
        '违禁词': '示例违禁词2',
        '分类': '色情低俗',
        '严重程度': '中',
        '描述': '',
        '状态': '禁用'
      },
      {
        '违禁词': '示例违禁词3',
        '分类': '暴力血腥',
        '严重程度': '低',
        '描述': '另一个示例描述',
        '状态': '启用'
      }
    ]
    
    // 添加说明表
    const instructionData = [
      { '字段名': '违禁词', '说明': '必填项，需要检测的违禁词语', '可选值': '无限制', '示例': '敏感词汇' },
      { '字段名': '分类', '说明': '可选项，违禁词的分类', '可选值': '政治敏感/色情低俗/暴力血腥/商业广告/其他', '示例': '政治敏感' },
      { '字段名': '严重程度', '说明': '可选项，违禁词的严重程度', '可选值': '低/中/高', '示例': '高' },
      { '字段名': '描述', '说明': '可选项，对违禁词的描述说明', '可选值': '无限制', '示例': '这是一个政治敏感词汇' },
      { '字段名': '状态', '说明': '可选项，是否启用该违禁词', '可选值': '启用/禁用', '示例': '启用' }
    ]
    
    // 选项表
    const optionsData = [
      { '分类选项': '政治敏感', '严重程度选项': '低', '状态选项': '启用' },
      { '分类选项': '色情低俗', '严重程度选项': '中', '状态选项': '禁用' },
      { '分类选项': '暴力血腥', '严重程度选项': '高', '状态选项': '' },
      { '分类选项': '商业广告', '严重程度选项': '', '状态选项': '' },
      { '分类选项': '其他', '严重程度选项': '', '状态选项': '' }
    ]
    
    const { utils, writeFile } = await import('xlsx')
    const workbook = utils.book_new()
    
    // 创建数据表
    const dataWorksheet = utils.json_to_sheet(templateData)
    utils.book_append_sheet(workbook, dataWorksheet, '数据表')
    
    // 创建说明表
    const instructionWorksheet = utils.json_to_sheet(instructionData)
    utils.book_append_sheet(workbook, instructionWorksheet, '填写说明')
    
    // 创建选项表
    const optionsWorksheet = utils.json_to_sheet(optionsData)
    utils.book_append_sheet(workbook, optionsWorksheet, '选项表')
    
    writeFile(workbook, '违禁词导入模板.xlsx')
    
    ElMessage.success('模板下载成功，请查看"填写说明"表了解各字段要求')
  } catch (error) {
    console.error('模板下载失败:', error)
    ElMessage.error('模板下载失败')
  }
}
</script>

<style lang="scss" scoped>
.prohibited-words-page {
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
        
        &.disabled {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          color: white;
        }
        
        &.danger {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
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
          
          &.disabled {
            opacity: 0.6;
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
                margin-bottom: 8px;
                
                .word-content {
                  font-size: 16px;
                  font-weight: 600;
                  color: #111827;
                }
                
                .word-meta {
                  display: flex;
                  gap: 8px;
                  
                  .category-badge,
                  .severity-badge,
                  .status-badge {
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                  }
                  
                  .category-badge {
                    &.category-political { background: #fef2f2; color: #dc2626; }
                    &.category-adult { background: #fef3c7; color: #d97706; }
                    &.category-violence { background: #fef2f2; color: #dc2626; }
                    &.category-commercial { background: #eff6ff; color: #2563eb; }
                    &.category-other { background: #f3f4f6; color: #6b7280; }
                  }
                  
                  .severity-badge {
                    &.severity-low { background: #f0fdf4; color: #16a34a; }
                    &.severity-medium { background: #fef3c7; color: #d97706; }
                    &.severity-high { background: #fef2f2; color: #dc2626; }
                  }
                  
                  .status-badge {
                    background: #f3f4f6;
                    color: #6b7280;
                    
                    &.active {
                      background: #f0fdf4;
                      color: #16a34a;
                    }
                  }
                }
              }
              
              .word-description {
                font-size: 14px;
                color: #6b7280;
                line-height: 1.5;
              }
            }
            
            .word-meta-info {
              .create-time {
                font-size: 13px;
                color: #9ca3af;
              }
            }
            
            .row-actions {
              display: flex;
              align-items: center;
              gap: 16px;
              
              .status-toggle {
                .toggle-switch {
                  position: relative;
                  display: inline-block;
                  width: 48px;
                  height: 24px;
                  
                  input {
                    opacity: 0;
                    width: 0;
                    height: 0;
                    
                    &:checked + .toggle-slider {
                      background: #10b981;
                      
                      &:before {
                        transform: translateX(24px);
                      }
                    }
                  }
                  
                  .toggle-slider {
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: #d1d5db;
                    transition: 0.2s;
                    border-radius: 24px;
                    
                    &:before {
                      position: absolute;
                      content: "";
                      height: 20px;
                      width: 20px;
                      left: 2px;
                      bottom: 2px;
                      background: white;
                      transition: 0.2s;
                      border-radius: 50%;
                      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    }
                  }
                }
              }
              
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
    
    // 现代化分页器
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
        
        .row-actions {
          justify-content: space-between;
        }
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