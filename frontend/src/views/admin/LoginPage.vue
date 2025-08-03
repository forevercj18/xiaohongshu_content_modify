<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="logo">
            <span class="logo-icon">🔐</span>
            <h1>管理员登录</h1>
          </div>
          <p class="subtitle">小红书内容优化工具 - 后台管理</p>
        </div>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名"
              size="large"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="authStore.isLoading"
              @click="handleLogin"
              class="login-button"
            >
              {{ authStore.isLoading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <p class="default-account">
            默认账户: <span class="highlight">admin</span> / <span class="highlight">admin123</span>
          </p>
          <router-link to="/" class="back-link">
            <ArrowLeft :size="16" />
            返回首页
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, ArrowLeft } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      console.log('准备登录...')
      await authStore.login(loginForm.username, loginForm.password)
      console.log('认证store返回成功，准备跳转...')
      ElMessage.success('登录成功')
      
      // 添加延迟确保状态更新完成
      setTimeout(() => {
        console.log('开始跳转到dashboard')
        router.push('/admin/dashboard')
      }, 100)
    } catch (error: any) {
      console.error('登录处理错误:', error)
      ElMessage.error(error.response?.data?.detail || '登录失败')
    }
  })
}

// 检查是否已登录
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/admin/dashboard')
  }
})
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  
  .logo {
    margin-bottom: 16px;
    
    .logo-icon {
      font-size: 48px;
      display: block;
      margin-bottom: 16px;
    }
    
    h1 {
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
  }
  
  .subtitle {
    color: var(--text-secondary);
    font-size: 14px;
    margin: 0;
  }
}

.login-form {
  .login-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 500;
  }
}

.login-footer {
  margin-top: 32px;
  text-align: center;
  
  .default-account {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 16px;
    
    .highlight {
      color: var(--primary);
      font-weight: 500;
      background: var(--primary-10);
      padding: 2px 6px;
      border-radius: 4px;
    }
  }
  
  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 14px;
    transition: color 0.2s ease;
    
    &:hover {
      color: var(--primary);
    }
  }
}

// 响应式设计
@media (max-width: 480px) {
  .login-card {
    padding: 24px;
  }
  
  .login-header {
    .logo {
      .logo-icon {
        font-size: 36px;
      }
      
      h1 {
        font-size: 20px;
      }
    }
  }
}
</style>