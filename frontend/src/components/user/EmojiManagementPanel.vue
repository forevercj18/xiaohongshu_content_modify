<template>
  <div class="emoji-management-panel">
    <!-- 操作区域 -->
    <div class="panel-header">
      <h4>表情管理</h4>
      <el-button 
        type="primary" 
        size="small" 
        @click="showAddDialog = true"
        :icon="Plus"
      >
        添加表情
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-mini">
      <div class="stat-item">
        <span class="stat-label">总数</span>
        <span class="stat-value">{{ stats.total_emojis }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">启用</span>
        <span class="stat-value">{{ stats.active_emojis }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">使用次数</span>
        <span class="stat-value">{{ stats.total_usage }}</span>
      </div>
    </div>

    <!-- 搜索过滤 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        size="small"
        placeholder="搜索表情..."
        @input="handleSearch"
      >
        <template #prefix>
          <Search :size="14" />
        </template>
      </el-input>
      
      <el-select 
        v-model="filterType" 
        size="small" 
        placeholder="类型"
        style="width: 80px; margin-top: 8px;"
        @change="handleFilter"
      >
        <el-option label="全部" value=""></el-option>
        <el-option label="R系列" value="R"></el-option>
        <el-option label="H系列" value="H"></el-option>
      </el-select>
    </div>

    <!-- 表情列表 -->
    <div class="emoji-list" v-loading="loading">
      <div 
        v-for="emoji in filteredEmojis" 
        :key="emoji.id" 
        class="emoji-item"
      >
        <div class="emoji-info">
          <div class="emoji-code">{{ emoji.code }}</div>
          <div class="emoji-name">{{ emoji.name }}</div>
          <div class="emoji-meta">
            <el-tag :type="emoji.emoji_type === 'R' ? 'success' : 'warning'" size="small">
              {{ emoji.emoji_type }}
            </el-tag>
            <span class="usage-count">{{ emoji.usage_count }}次</span>
          </div>
        </div>
        <div class="emoji-actions">
          <el-switch 
            v-model="emoji.status" 
            size="small"
            :active-value="1" 
            :inactive-value="0"
            @change="handleStatusChange(emoji)"
          />
          <el-dropdown trigger="click">
            <el-button type="text" size="small" :icon="MoreVertical" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="editEmoji(emoji)">
                  <Edit :size="14" style="margin-right: 4px;" />
                  编辑
                </el-dropdown-item>
                <el-dropdown-item @click="deleteEmoji(emoji)" divided>
                  <Trash2 :size="14" style="margin-right: 4px;" />
                  删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <div v-if="filteredEmojis.length === 0" class="empty-state">
        <div class="empty-icon">🎭</div>
        <div class="empty-text">暂无表情数据</div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total > pagination.size" class="pagination-mini">
      <el-pagination
        v-model:current-page="pagination.page"
        :page-size="pagination.size"
        :total="pagination.total"
        layout="prev, pager, next"
        small
        @current-change="handlePageChange"
      />
    </div>

    <!-- 添加/编辑表情对话框 -->
    <el-dialog 
      v-model="showAddDialog" 
      :title="editingEmoji ? '编辑表情' : '添加表情'"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="emojiForm" :rules="formRules" ref="emojiFormRef" label-width="80px">
        <el-form-item label="表情代码" prop="code">
          <el-input 
            v-model="emojiForm.code" 
            placeholder="[开心R]"
            :disabled="!!editingEmoji"
          />
        </el-form-item>
        
        <el-form-item label="表情名称" prop="name">
          <el-input v-model="emojiForm.name" placeholder="开心" />
        </el-form-item>
        
        <el-form-item label="表情类型" prop="emoji_type">
          <el-radio-group v-model="emojiForm.emoji_type">
            <el-radio value="R">R系列</el-radio>
            <el-radio value="H">H系列</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select v-model="emojiForm.category" placeholder="选择分类">
            <el-option 
              v-for="cat in categories" 
              :key="cat.name" 
              :label="cat.display_name" 
              :value="cat.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级">
          <el-rate v-model="emojiForm.priority" max="5" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEmoji" :loading="saving">
          {{ editingEmoji ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  MoreVertical 
} from 'lucide-vue-next'
import { emojiAdminApi, emojiApi } from '@/api/emoji'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const editingEmoji = ref(null)
const searchKeyword = ref('')
const filterType = ref('')

const emojis = ref([])
const categories = ref([])
const stats = reactive({
  total_emojis: 0,
  active_emojis: 0,
  total_usage: 0
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 表单数据
const emojiForm = reactive({
  code: '',
  name: '',
  emoji_type: 'R',
  category: '',
  priority: 3
})

const emojiFormRef = ref()

// 表单验证规则
const formRules = {
  code: [
    { required: true, message: '请输入表情代码', trigger: 'blur' },
    { pattern: /^\[.+[RH]\]$/, message: '代码格式应为[表情名R]或[表情名H]', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入表情名称', trigger: 'blur' }
  ],
  emoji_type: [
    { required: true, message: '请选择表情类型', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

// 计算属性
const filteredEmojis = computed(() => {
  let filtered = emojis.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(emoji => 
      emoji.code.toLowerCase().includes(keyword) ||
      emoji.name.toLowerCase().includes(keyword)
    )
  }
  
  if (filterType.value) {
    filtered = filtered.filter(emoji => emoji.emoji_type === filterType.value)
  }
  
  return filtered
})

// 方法
const fetchEmojis = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size
    }
    
    const response = await emojiAdminApi.getEmojiList(params)
    emojis.value = response.emojis
    pagination.total = response.pagination.total
  } catch (error) {
    ElMessage.error('获取表情列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await emojiApi.getCategories()
    categories.value = response.categories
  } catch (error) {
    ElMessage.error('获取分类失败')
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
  // 搜索在计算属性中处理，这里可以添加防抖逻辑
}

const handleFilter = () => {
  // 过滤在计算属性中处理
}

const handleStatusChange = async (emoji) => {
  try {
    await emojiAdminApi.updateEmoji(emoji.id, { status: emoji.status })
    ElMessage.success('状态更新成功')
    fetchStats() // 更新统计
  } catch (error) {
    ElMessage.error('状态更新失败')
    emoji.status = emoji.status === 1 ? 0 : 1 // 回滚
  }
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchEmojis()
}

const editEmoji = (emoji) => {
  editingEmoji.value = emoji
  Object.assign(emojiForm, {
    code: emoji.code,
    name: emoji.name,
    emoji_type: emoji.emoji_type,
    category: emoji.category,
    priority: emoji.priority
  })
  showAddDialog.value = true
}

const deleteEmoji = async (emoji) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除表情 "${emoji.code}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await emojiAdminApi.deleteEmoji(emoji.id)
    ElMessage.success('删除成功')
    refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetForm = () => {
  editingEmoji.value = null
  Object.assign(emojiForm, {
    code: '',
    name: '',
    emoji_type: 'R',
    category: '',
    priority: 3
  })
  if (emojiFormRef.value) {
    emojiFormRef.value.resetFields()
  }
}

const saveEmoji = async () => {
  try {
    await emojiFormRef.value.validate()
    saving.value = true
    
    const data = {
      name: emojiForm.name,
      emoji_type: emojiForm.emoji_type,
      category: emojiForm.category,
      priority: emojiForm.priority
    }
    
    if (editingEmoji.value) {
      // 更新
      await emojiAdminApi.updateEmoji(editingEmoji.value.id, data)
      ElMessage.success('更新成功')
    } else {
      // 创建
      data.code = emojiForm.code
      await emojiAdminApi.createEmoji(data)
      ElMessage.success('创建成功')
    }
    
    showAddDialog.value = false
    refreshData()
  } catch (error) {
    ElMessage.error(editingEmoji.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.emoji-management-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.panel-header h4 {
  margin: 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

.stats-mini {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 8px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 2px;
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: bold;
  color: var(--el-color-primary);
}

.search-section {
  margin-bottom: 16px;
}

.emoji-list {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 12px;
}

.emoji-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  margin-bottom: 8px;
  background: white;
}

.emoji-item:hover {
  background: var(--el-bg-color-page);
}

.emoji-info {
  flex: 1;
}

.emoji-code {
  font-size: 14px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.emoji-name {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.emoji-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.usage-count {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.emoji-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-placeholder);
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.empty-text {
  font-size: 14px;
}

.pagination-mini {
  padding: 8px 0;
  text-align: center;
  border-top: 1px solid var(--el-border-color-light);
}
</style>