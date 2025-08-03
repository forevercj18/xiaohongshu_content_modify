<template>
  <AdminLayout>
    <template #header>
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">账号管理</h1>
            <p class="page-subtitle">管理系统管理员账号，分配权限和角色</p>
          </div>
        </div>
      </div>
    </template>

    <div class="admin-users-content">
      <!-- 搜索和筛选 -->
      <div class="search-section">
        <div class="search-controls">
          <div class="search-filters">
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户名或邮箱..."
              style="width: 300px"
              @input="handleSearch"
              clearable
            >
              <template #prefix>
                <Search :size="16" />
              </template>
            </el-input>
            <el-select
              v-model="roleFilter"
              placeholder="筛选角色"
              style="width: 150px"
              @change="handleFilter"
              clearable
            >
              <el-option label="超级管理员" value="super_admin" />
              <el-option label="管理员" value="admin" />
            </el-select>
            <el-button @click="resetFilters">
              <RefreshCcw :size="16" />
              重置
            </el-button>
          </div>
          <div class="action-controls">
            <el-button 
              type="primary" 
              @click="showAddDialog = true"
              class="add-user-btn"
            >
              <Plus :size="16" />
              新增管理员
            </el-button>
          </div>
        </div>
      </div>

      <!-- 管理员列表 -->
      <div class="users-section">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="users.length === 0" class="empty-container">
          <Users :size="48" class="empty-icon" />
          <h3>暂无管理员</h3>
          <p>还没有创建任何管理员账号</p>
          <el-button type="primary" @click="showAddDialog = true">创建第一个管理员</el-button>
        </div>

        <!-- 用户卡片列表 -->
        <div v-else class="users-grid">
          <div 
            v-for="user in users" 
            :key="user.id" 
            class="user-card"
            :class="{ disabled: user.status === 0 }"
          >
            <!-- 卡片头部 -->
            <div class="card-header">
              <div class="user-avatar">
                <User :size="20" />
              </div>
              <div class="user-info">
                <h3 class="user-name">{{ user.username }}</h3>
                <span class="user-role" :class="getRoleClass(user.role)">
                  {{ getRoleText(user.role) }}
                </span>
              </div>
              <el-dropdown @command="handleUserAction" trigger="click">
                <el-button type="text" class="action-btn">
                  <MoreHorizontal :size="16" />
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item 
                      :command="{ action: 'toggle-status', user }"
                      :disabled="user.id === currentUserId"
                    >
                      {{ user.status === 1 ? '禁用账号' : '启用账号' }}
                    </el-dropdown-item>
                    <el-dropdown-item 
                      :command="{ action: 'reset-password', user }"
                    >
                      重置密码
                    </el-dropdown-item>
                    <el-dropdown-item 
                      :command="{ action: 'delete', user }"
                      :disabled="user.id === currentUserId || user.role === 'super_admin'"
                      class="danger-item"
                    >
                      删除账号
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            
            <!-- 卡片内容 -->
            <div class="card-content">
              <div class="user-detail">
                <Mail :size="14" />
                <span>{{ user.email }}</span>
              </div>
              <div class="user-detail">
                <Calendar :size="14" />
                <span>创建于 {{ formatDate(user.created_at) }}</span>
              </div>
              <div v-if="user.last_login_at" class="user-detail">
                <Clock :size="14" />
                <span>最后登录 {{ formatDate(user.last_login_at) }}</span>
              </div>
            </div>

            <!-- 卡片底部 -->
            <div class="card-footer">
              <div class="status-badge" :class="getStatusClass(user.status)">
                {{ user.status === 1 ? '正常' : '禁用' }}
              </div>
              <div class="permissions-info">
                {{ getPermissionsSummary(user.permissions) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增管理员对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增管理员"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="addFormRef"
        :model="addForm"
        :rules="addFormRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="addForm.email" placeholder="请输入邮箱" type="email" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="addForm.password" 
            placeholder="请输入密码" 
            type="password" 
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="addForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="超级管理员" value="super_admin" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddUser" :loading="submitting">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="重置密码"
      width="400px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordFormRules"
        label-width="80px"
      >
        <el-form-item label="新密码" prop="new_password">
          <el-input 
            v-model="passwordForm.new_password" 
            placeholder="请输入新密码" 
            type="password" 
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword" :loading="submitting">
          重置
        </el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Search, 
  RefreshCcw, 
  Users, 
  User, 
  MoreHorizontal,
  Mail,
  Calendar,
  Clock
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { adminApi } from '@/api/admin'
import AdminLayout from '@/components/admin/AdminLayout.vue'

const authStore = useAuthStore()

// 当前用户ID
const currentUserId = computed(() => authStore.user?.id)

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const searchQuery = ref('')
const roleFilter = ref('')

// 对话框状态
const showAddDialog = ref(false)
const showPasswordDialog = ref(false)
const selectedUser = ref(null)

// 表单数据
const addForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'admin'
})

const passwordForm = reactive({
  new_password: ''
})

// 表单验证规则
const addFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const passwordFormRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ]
}

// 表单引用
const addFormRef = ref()
const passwordFormRef = ref()

// 获取角色文本
const getRoleText = (role: string) => {
  switch (role) {
    case 'super_admin': return '超级管理员'
    case 'admin': return '管理员'
    default: return '未知'
  }
}

// 获取角色样式类
const getRoleClass = (role: string) => {
  switch (role) {
    case 'super_admin': return 'role-super'
    case 'admin': return 'role-admin'
    default: return 'role-default'
  }
}

// 获取状态样式类
const getStatusClass = (status: number) => {
  return status === 1 ? 'status-active' : 'status-disabled'
}

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 获取权限摘要
const getPermissionsSummary = (permissions: any) => {
  if (!permissions) return '无权限'
  
  try {
    const perms = typeof permissions === 'string' ? JSON.parse(permissions) : permissions
    const modules = Object.keys(perms).filter(key => {
      const modulePerms = perms[key]
      return Object.values(modulePerms).some(v => v === true)
    })
    
    return modules.length > 0 ? `${modules.length} 个模块权限` : '无权限'
  } catch {
    return '权限解析失败'
  }
}

// 加载管理员列表
const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value || undefined,
      role: roleFilter.value || undefined
    }
    const response = await adminApi.getAdminUsers(params)
    users.value = response || []
    console.log('Loaded users:', users.value)
  } catch (error) {
    console.error('Load users error:', error)
    ElMessage.error('加载管理员列表失败')
    users.value = []
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  loadUsers()
}

// 筛选处理
const handleFilter = () => {
  loadUsers()
}

// 重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  roleFilter.value = ''
  loadUsers()
}

// 用户操作处理
const handleUserAction = async ({ action, user }) => {
  selectedUser.value = user
  
  switch (action) {
    case 'toggle-status':
      await handleToggleStatus(user)
      break
    case 'reset-password':
      showPasswordDialog.value = true
      break
    case 'delete':
      await handleDeleteUser(user)
      break
  }
}

// 切换用户状态
const handleToggleStatus = async (user) => {
  const action = user.status === 1 ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${user.username} 吗？`, '确认操作', {
      type: 'warning'
    })
    
    const newStatus = user.status === 1 ? 0 : 1
    await adminApi.updateAdminStatus(user.id, newStatus)
    
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败`)
    }
  }
}

// 删除用户
const handleDeleteUser = async (user) => {
  // 前端双重检查
  if (user.role === 'super_admin') {
    ElMessage.error('不能删除超级管理员账号')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除管理员 "${user.username}" 吗？此操作不可撤销！`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await adminApi.deleteAdminUser(user.id)
    ElMessage.success('管理员删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除管理员失败:', error)
      console.error('错误详情:', {
        response: error.response,
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      })
      ElMessage.error(error.response?.data?.detail || error.message || '删除失败')
    }
  }
}

// 新增管理员
const handleAddUser = async () => {
  if (!addFormRef.value) return
  
  try {
    await addFormRef.value.validate()
    submitting.value = true
    
    await adminApi.createAdminUser(addForm)
    
    ElMessage.success('管理员创建成功')
    showAddDialog.value = false
    resetForm()
    loadUsers()
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('创建管理员失败')
    }
  } finally {
    submitting.value = false
  }
}

// 重置密码
const handleResetPassword = async () => {
  if (!passwordFormRef.value || !selectedUser.value) return
  
  try {
    await passwordFormRef.value.validate()
    submitting.value = true
    
    await adminApi.resetAdminPassword(selectedUser.value.id, {
      new_password: passwordForm.new_password
    })
    
    ElMessage.success('密码重置成功')
    showPasswordDialog.value = false
    passwordForm.new_password = ''
  } catch (error) {
    ElMessage.error('密码重置失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(addForm, {
    username: '',
    email: '',
    password: '',
    role: 'admin'
  })
  addFormRef.value?.resetFields()
}

// 组件挂载时加载数据
onMounted(() => {
  loadUsers()
})
</script>

<style lang="scss" scoped>
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

.admin-users-content {
  
  .search-section {
    background: white;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    
    .search-controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      
      .search-filters {
        display: flex;
        gap: 16px;
        align-items: center;
        flex-wrap: wrap;
        flex: 1;
      }
      
      .action-controls {
        .add-user-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          border-radius: 8px;
          padding: 12px 20px;
          font-weight: 600;
          font-size: 14px;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
          transition: all 0.2s ease;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
          }
          
          &:active {
            transform: translateY(0);
          }
        }
      }
    }
  }
  
  .users-section {
    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e5e7eb;
      
      .loading-spinner {
        width: 32px;
        height: 32px;
        border: 3px solid #f3f4f6;
        border-top: 3px solid #2563eb;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 16px;
      }
      
      p {
        color: #6b7280;
        font-size: 14px;
      }
    }
    
    .empty-container {
      text-align: center;
      padding: 60px 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e5e7eb;
      
      .empty-icon {
        color: #9ca3af;
        margin-bottom: 16px;
      }
      
      h3 {
        color: #1f2937;
        margin-bottom: 8px;
        font-size: 18px;
        font-weight: 600;
      }
      
      p {
        color: #6b7280;
        margin-bottom: 24px;
        font-size: 14px;
      }
    }
    
    .users-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
      
      .user-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
        border: 1px solid #e5e7eb;
        
        &:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
          border-color: #2563eb;
        }
        
        &.disabled {
          opacity: 0.6;
          background: #f9fafb;
          
          .user-name {
            text-decoration: line-through;
          }
        }
        
        .card-header {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 16px;
          
          .user-avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            flex-shrink: 0;
          }
          
          .user-info {
            flex: 1;
            
            .user-name {
              font-size: 16px;
              font-weight: 600;
              color: #1f2937;
              margin-bottom: 4px;
            }
            
            .user-role {
              font-size: 12px;
              padding: 2px 8px;
              border-radius: 12px;
              font-weight: 500;
              
              &.role-super {
                background: rgba(239, 68, 68, 0.1);
                color: #ef4444;
              }
              
              &.role-admin {
                background: rgba(37, 99, 235, 0.1);
                color: #2563eb;
              }
            }
          }
          
          .action-btn {
            color: #9ca3af;
            border: none;
            background: transparent;
            padding: 4px;
            
            &:hover {
              color: #1f2937;
              background: #f3f4f6;
            }
          }
        }
        
        .card-content {
          margin-bottom: 16px;
          
          .user-detail {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #6b7280;
            font-size: 13px;
            margin-bottom: 8px;
            
            &:last-child {
              margin-bottom: 0;
            }
          }
        }
        
        .card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 12px;
          border-top: 1px solid #f3f4f6;
          
          .status-badge {
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: 500;
            
            &.status-active {
              background: rgba(16, 185, 129, 0.1);
              color: #10b981;
            }
            
            &.status-disabled {
              background: rgba(239, 68, 68, 0.1);
              color: #ef4444;
            }
          }
          
          .permissions-info {
            font-size: 12px;
            color: #9ca3af;
          }
        }
      }
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .page-header {
    .header-content {
      .title-section {
        .page-title {
          font-size: 24px;
        }
        
        .page-subtitle {
          font-size: 14px;
        }
      }
    }
  }
  
  .admin-users-content {
    .search-section {
      padding: 20px;
      
      .search-controls {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
        
        .search-filters {
          flex-direction: column;
          align-items: stretch;
          
          :deep(.el-input), :deep(.el-select) {
            width: 100% !important;
          }
        }
        
        .action-controls {
          .add-user-btn {
            width: 100%;
            justify-content: center;
          }
        }
      }
    }
    
    .users-grid {
      grid-template-columns: 1fr !important;
    }
  }
}

@media (max-width: 1024px) {
  .admin-users-content {
    .search-section .search-controls {
      flex-direction: column;
      align-items: stretch;
      gap: 16px;
      
      .search-filters {
        justify-content: flex-start;
      }
    }
  }
}

// 删除按钮样式
:deep(.danger-item) {
  color: #ef4444 !important;
  
  &:hover {
    background-color: #fef2f2 !important;
    color: #dc2626 !important;
  }
}
</style>