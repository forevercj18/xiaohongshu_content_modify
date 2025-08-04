<template>
  <div class="whitelist-management-page">
    <AdminLayout>
      <template #header>
        <div class="page-header">
          <div class="header-content">
            <div class="title-section">
              <h1 class="page-title">白名单管理</h1>
              <p class="page-subtitle">管理违禁词白名单规则，支持正则表达式匹配模式</p>
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
                placeholder="搜索违禁词、模式、描述..."
                @input="handleSearch"
              />
            </div>
            
            <div class="filter-select">
              <select v-model="selectedCategory" @change="handleFilter">
                <option value="">所有分类</option>
                <option 
                  v-for="category in categories" 
                  :key="category" 
                  :value="category"
                >
                  {{ category }}
                </option>
              </select>
            </div>
            
            <div class="filter-select">
              <select v-model="selectedStatus" @change="handleFilter">
                <option value="">所有状态</option>
                <option value="1">已启用</option>
                <option value="0">已禁用</option>
              </select>
            </div>
          </div>
          
          <div class="action-group">
            <button class="btn btn-secondary" @click="showTestDialog = true">
              <TestTube :size="16" />
              测试模式
            </button>
            <button class="btn btn-secondary" @click="exportData">
              <Download :size="16" />
              导出数据
            </button>
            <button class="btn btn-primary" @click="showAddDialog = true">
              <Plus :size="16" />
              添加规则
            </button>
          </div>
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon total">
              <Shield :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.overview.total_patterns }}</div>
              <div class="stat-label">规则总数</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon active">
              <CheckCircle :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.overview.active_patterns }}</div>
              <div class="stat-label">已启用</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon disabled">
              <XCircle :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.overview.inactive_patterns }}</div>
              <div class="stat-label">已禁用</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon categories">
              <Tag :size="18" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.by_category.length }}</div>
              <div class="stat-label">分类数量</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 现代化数据表格 -->
      <div class="data-table-container">
        <div class="table-header">
          <div class="table-title">
            <span>白名单规则</span>
            <div class="table-count">{{ filteredPatterns.length }} 条记录</div>
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
            <div v-if="paginatedPatterns.length === 0" class="empty-state">
              <Shield :size="48" />
              <h3>暂无数据</h3>
              <p>{{ searchKeyword ? '未找到匹配的白名单规则' : '还没有添加任何白名单规则' }}</p>
              <button v-if="!searchKeyword" class="btn btn-primary" @click="showAddDialog = true">
                添加第一个规则
              </button>
            </div>
            
            <div v-else class="table-rows">
              <div
                v-for="pattern in paginatedPatterns"
                :key="pattern.id"
                class="table-row"
                :class="{ disabled: pattern.is_active === 0 }"
              >
                <div class="row-main">
                  <div class="pattern-info">
                    <div class="pattern-text">
                      <span class="prohibited-word">{{ pattern.prohibited_word }}</span>
                      <div class="pattern-meta">
                        <span class="pattern-regex" :title="pattern.pattern">
                          <Code :size="14" />
                          {{ pattern.pattern }}
                        </span>
                        <span v-if="pattern.category" class="category-badge">
                          {{ pattern.category }}
                        </span>
                        <span class="priority-badge" :class="`priority-${pattern.priority}`">
                          优先级 {{ pattern.priority }}
                        </span>
                        <span class="status-badge" :class="{ active: pattern.is_active === 1 }">
                          {{ pattern.is_active === 1 ? '启用' : '禁用' }}
                        </span>
                      </div>
                    </div>
                    
                    <div class="pattern-description" v-if="pattern.description">
                      {{ pattern.description }}
                    </div>
                    
                    <div class="pattern-example" v-if="pattern.example">
                      <span class="example-label">示例：</span>
                      <span class="example-text">{{ pattern.example }}</span>
                    </div>
                  </div>
                  
                  <div class="pattern-meta-info">
                    <div class="create-info">
                      <span>创建于 {{ formatDate(pattern.created_at) }}</span>
                      <span v-if="pattern.created_by">by {{ pattern.created_by }}</span>
                    </div>
                  </div>
                  
                  <div class="row-actions">
                    <div class="status-toggle">
                      <label class="toggle-switch">
                        <input
                          type="checkbox"
                          :checked="pattern.is_active === 1"
                          @change="updatePatternStatus(pattern, $event)"
                        />
                        <span class="toggle-slider"></span>
                      </label>
                    </div>
                    
                    <div class="action-buttons">
                      <button
                        class="action-btn test"
                        @click="testPattern(pattern)"
                        title="测试规则"
                      >
                        <TestTube :size="16" />
                      </button>
                      <button
                        class="action-btn edit"
                        @click="editPattern(pattern)"
                        title="编辑"
                      >
                        <Edit2 :size="16" />
                      </button>
                      <button
                        class="action-btn delete"
                        @click="deletePattern(pattern)"
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
          <div class="modern-pagination" v-if="filteredPatterns.length > pageSize">
            <div class="pagination-info">
              显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredPatterns.length) }} 条，
              共 {{ filteredPatterns.length }} 条记录
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
      :title="editingPattern ? '编辑白名单规则' : '添加白名单规则'"
      width="600px"
    >
      <el-form
        ref="patternFormRef"
        :model="patternForm"
        :rules="patternFormRules"
        label-width="100px"
      >
        <el-form-item label="违禁词" prop="prohibited_word">
          <el-input
            v-model="patternForm.prohibited_word"
            placeholder="请输入违禁词"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="匹配模式" prop="pattern">
          <el-input
            v-model="patternForm.pattern"
            placeholder="请输入正则表达式模式"
            clearable
          />
          <div class="form-help">
            <small>正则表达式用于匹配包含该违禁词的安全表达，例如：r".*我家的.*第一.*"</small>
          </div>
        </el-form-item>
        
        <el-form-item label="分类">
          <el-input
            v-model="patternForm.category"
            placeholder="可选：规则分类"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="patternForm.description"
            type="textarea"
            placeholder="可选：描述该规则的作用"
            :rows="3"
          />
        </el-form-item>
        
        <el-form-item label="示例">
          <el-input
            v-model="patternForm.example"
            placeholder="可选：匹配示例"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="优先级">
          <el-select v-model="patternForm.priority" style="width: 100%;">
            <el-option label="1 - 最低" :value="1" />
            <el-option label="2 - 较低" :value="2" />
            <el-option label="3 - 中等" :value="3" />
            <el-option label="4 - 较高" :value="4" />
            <el-option label="5 - 最高" :value="5" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="savePattern"
            :loading="saving"
          >
            {{ editingPattern ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 测试模式对话框 -->
    <el-dialog
      v-model="showTestDialog"
      title="测试白名单模式"
      width="700px"
    >
      <div class="test-container">
        <el-form label-width="100px">
          <el-form-item label="测试模式">
            <el-input
              v-model="testForm.pattern"
              placeholder="请输入要测试的正则表达式"
              clearable
            />
          </el-form-item>
          
          <el-form-item label="测试文本">
            <el-input
              v-model="testForm.test_text"
              type="textarea"
              placeholder="请输入要测试的文本内容"
              :rows="4"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              @click="runTest"
              :loading="testing"
            >
              <TestTube :size="16" />
              运行测试
            </el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="testResult" class="test-result">
          <h4>测试结果</h4>
          <div class="result-item">
            <strong>是否匹配：</strong>
            <span :class="testResult.is_match ? 'match-yes' : 'match-no'">
              {{ testResult.is_match ? '是' : '否' }}
            </span>
          </div>
          <div v-if="testResult.matches.length > 0" class="result-item">
            <strong>匹配内容：</strong>
            <div class="matches-list">
              <span
                v-for="(match, index) in testResult.matches"
                :key="index"
                class="match-item"
              >
                {{ match }}
              </span>
            </div>
          </div>
          <div v-if="testResult.match_positions.length > 0" class="result-item">
            <strong>匹配位置：</strong>
            <div class="positions-list">
              <span
                v-for="(pos, index) in testResult.match_positions"
                :key="index"
                class="position-item"
              >
                [{{ pos[0] }}, {{ pos[1] }}]
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTestDialog = false">关闭</el-button>
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
  TestTube,
  Shield,
  CheckCircle,
  XCircle,
  Tag,
  Code,
  Edit2, 
  Trash2,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'

import AdminLayout from '@/components/admin/AdminLayout.vue'
import {
  getWhitelistPatterns,
  createWhitelistPattern,
  updateWhitelistPattern,
  deleteWhitelistPattern,
  getWhitelistCategories,
  testWhitelistPattern,
  getWhitelistStats,
  type WhitelistPattern,
  type WhitelistTestResponse,
  type WhitelistStats
} from '@/api/whitelist'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const testing = ref(false)

const patterns = ref<WhitelistPattern[]>([])
const categories = ref<string[]>([])
const stats = ref<WhitelistStats>({
  overview: {
    total_patterns: 0,
    active_patterns: 0,
    inactive_patterns: 0
  },
  by_category: [],
  by_word: []
})

const searchKeyword = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 对话框状态
const showAddDialog = ref(false)
const showTestDialog = ref(false)
const editingPattern = ref<WhitelistPattern | null>(null)

// 表单数据
const patternFormRef = ref<FormInstance>()
const patternForm = reactive({
  prohibited_word: '',
  pattern: '',
  description: '',
  category: '',
  example: '',
  priority: 3
})

const patternFormRules: FormRules = {
  prohibited_word: [
    { required: true, message: '请输入违禁词', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  pattern: [
    { required: true, message: '请输入匹配模式', trigger: 'blur' },
    { min: 1, max: 500, message: '长度在 1 到 500 个字符', trigger: 'blur' }
  ]
}

// 测试表单
const testForm = reactive({
  pattern: '',
  test_text: ''
})

const testResult = ref<WhitelistTestResponse | null>(null)

// 计算属性
const filteredPatterns = computed(() => {
  let result = patterns.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(pattern => 
      pattern.prohibited_word.toLowerCase().includes(keyword) ||
      pattern.pattern.toLowerCase().includes(keyword) ||
      (pattern.description && pattern.description.toLowerCase().includes(keyword))
    )
  }

  if (selectedCategory.value) {
    result = result.filter(pattern => pattern.category === selectedCategory.value)
  }

  if (selectedStatus.value !== '') {
    result = result.filter(pattern => pattern.is_active === Number(selectedStatus.value))
  }

  return result
})

const paginatedPatterns = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPatterns.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredPatterns.value.length / pageSize.value))

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
  await loadData()
})

// 方法
const loadData = async () => {
  await Promise.all([
    loadPatterns(),
    loadCategories(),
    loadStats()
  ])
}

const loadPatterns = async () => {
  loading.value = true
  try {
    const response = await getWhitelistPatterns()
    patterns.value = response.patterns
  } catch (error) {
    console.error('加载白名单规则失败:', error)
    ElMessage.error('加载白名单规则失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await getWhitelistCategories()
    categories.value = response.categories
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const loadStats = async () => {
  try {
    const response = await getWhitelistStats()
    stats.value = response
  } catch (error) {
    console.error('加载统计失败:', error)
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

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const editPattern = (pattern: WhitelistPattern) => {
  editingPattern.value = pattern
  Object.assign(patternForm, {
    prohibited_word: pattern.prohibited_word,
    pattern: pattern.pattern,
    description: pattern.description || '',
    category: pattern.category || '',
    example: pattern.example || '',
    priority: pattern.priority
  })
  showAddDialog.value = true
}

const deletePattern = async (pattern: WhitelistPattern) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除白名单规则 "${pattern.prohibited_word}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteWhitelistPattern(pattern.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除白名单规则失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const updatePatternStatus = async (pattern: WhitelistPattern, event: Event) => {
  const target = event.target as HTMLInputElement
  const newStatus = target.checked ? 1 : 0
  
  try {
    await updateWhitelistPattern(pattern.id, { is_active: newStatus })
    pattern.is_active = newStatus
    ElMessage.success(newStatus ? '已启用' : '已禁用')
    await loadStats() // 更新统计
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('更新状态失败')
    // 回滚复选框状态
    target.checked = pattern.is_active === 1
  }
}

const savePattern = async () => {
  if (!patternFormRef.value) return
  
  await patternFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      if (editingPattern.value) {
        await updateWhitelistPattern(editingPattern.value.id, patternForm)
        ElMessage.success('更新成功')
      } else {
        await createWhitelistPattern(patternForm)
        ElMessage.success('添加成功')
      }
      
      showAddDialog.value = false
      resetForm()
      await loadData()
    } catch (error: any) {
      console.error('保存白名单规则失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const resetForm = () => {
  editingPattern.value = null
  Object.assign(patternForm, {
    prohibited_word: '',
    pattern: '',
    description: '',
    category: '',
    example: '',
    priority: 3
  })
  patternFormRef.value?.clearValidate()
}

const testPattern = (pattern: WhitelistPattern) => {
  testForm.pattern = pattern.pattern
  testForm.test_text = ''
  testResult.value = null
  showTestDialog.value = true
}

const runTest = async () => {
  if (!testForm.pattern || !testForm.test_text) {
    ElMessage.warning('请输入测试模式和测试文本')
    return
  }
  
  testing.value = true
  try {
    testResult.value = await testWhitelistPattern({
      pattern: testForm.pattern,
      test_text: testForm.test_text
    })
  } catch (error: any) {
    console.error('模式测试失败:', error)
    ElMessage.error(error.response?.data?.detail || '测试失败')
  } finally {
    testing.value = false
  }
}

const exportData = async () => {
  try {
    const { utils, writeFile } = await import('xlsx')
    
    // 准备Excel数据
    const excelData = patterns.value.map(pattern => ({
      '违禁词': pattern.prohibited_word,
      '匹配模式': pattern.pattern,
      '分类': pattern.category || '',
      '描述': pattern.description || '',
      '示例': pattern.example || '',
      '优先级': pattern.priority,
      '状态': pattern.is_active === 1 ? '启用' : '禁用',
      '创建者': pattern.created_by || '',
      '创建时间': formatDate(pattern.created_at)
    }))
    
    const worksheet = utils.json_to_sheet(excelData)
    const workbook = utils.book_new()
    utils.book_append_sheet(workbook, worksheet, '白名单规则')
    
    const fileName = `白名单规则-${new Date().toISOString().split('T')[0]}.xlsx`
    writeFile(workbook, fileName)
    
    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}
</script>

<style lang="scss" scoped>
.whitelist-management-page {
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
            
            .pattern-info {
              flex: 1;
              
              .pattern-text {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 8px;
                
                .prohibited-word {
                  font-size: 16px;
                  font-weight: 600;
                  color: #111827;
                }
                
                .pattern-meta {
                  display: flex;
                  gap: 8px;
                  align-items: center;
                  
                  .pattern-regex {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 12px;
                    color: #6b7280;
                    background: #f3f4f6;
                    padding: 2px 6px;
                    border-radius: 4px;
                    max-width: 200px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                  }
                  
                  .category-badge {
                    padding: 2px 8px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    background: #e0e7ff;
                    color: #3730a3;
                  }
                  
                  .priority-badge {
                    padding: 2px 8px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    
                    &.priority-1 { background: #f3f4f6; color: #6b7280; }
                    &.priority-2 { background: #e0f2fe; color: #0369a1; }
                    &.priority-3 { background: #f0fdf4; color: #16a34a; }
                    &.priority-4 { background: #fef3c7; color: #d97706; }
                    &.priority-5 { background: #fef2f2; color: #dc2626; }
                  }
                  
                  .status-badge {
                    padding: 2px 8px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    background: #f3f4f6;
                    color: #6b7280;
                    
                    &.active {
                      background: #f0fdf4;
                      color: #16a34a;
                    }
                  }
                }
              }
              
              .pattern-description {
                font-size: 14px;
                color: #6b7280;
                line-height: 1.5;
                margin-bottom: 4px;
              }
              
              .pattern-example {
                font-size: 13px;
                color: #9ca3af;
                
                .example-label {
                  font-weight: 500;
                }
                
                .example-text {
                  font-style: italic;
                }
              }
            }
            
            .pattern-meta-info {
              .create-info {
                font-size: 13px;
                color: #9ca3af;
                text-align: right;
                
                span {
                  display: block;
                }
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
                  
                  &.test {
                    color: #8b5cf6;
                    background: transparent;
                    
                    &:hover {
                      background: #f3f1ff;
                      color: #7c3aed;
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

// 表单辅助样式
.form-help {
  margin-top: 4px;
  
  small {
    color: #6b7280;
    font-size: 12px;
  }
}

// 测试容器样式
.test-container {
  .test-result {
    margin-top: 24px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    
    h4 {
      margin: 0 0 16px 0;
      color: #374151;
      font-size: 16px;
    }
    
    .result-item {
      margin-bottom: 12px;
      
      strong {
        color: #374151;
        margin-right: 8px;
      }
      
      .match-yes {
        color: #16a34a;
        font-weight: 600;
      }
      
      .match-no {
        color: #dc2626;
        font-weight: 600;
      }
      
      .matches-list,
      .positions-list {
        margin-top: 8px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        
        .match-item,
        .position-item {
          padding: 4px 8px;
          background: #e0e7ff;
          color: #3730a3;
          border-radius: 4px;
          font-size: 12px;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
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
</style>