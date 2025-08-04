<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
            </svg>
          </div>
          <span v-if="!sidebarCollapsed" class="logo-text">小红书优化</span>
        </div>
        <el-button
          type="text"
          class="collapse-btn"
          @click="toggleSidebar"
        >
          <Menu :size="18" />
        </el-button>
      </div>
      
      <nav class="sidebar-nav">
        <div class="nav-section">
          <div v-if="!sidebarCollapsed" class="nav-title">工作空间</div>
          <router-link
            to="/management/dashboard"
            class="nav-item"
            :class="{ active: $route.name === 'management-dashboard' }"
          >
            <div class="nav-icon">
              <BarChart3 :size="18" />
            </div>
            <span v-if="!sidebarCollapsed" class="nav-label">仪表盘</span>
            <div v-if="!sidebarCollapsed && $route.name === 'management-dashboard'" class="nav-indicator"></div>
          </router-link>
          
          <router-link
            to="/management/prohibited-words"
            class="nav-item"
            :class="{ active: $route.name === 'management-prohibited-words' }"
          >
            <div class="nav-icon">
              <AlertTriangle :size="18" />
            </div>
            <span v-if="!sidebarCollapsed" class="nav-label">违禁词管理</span>
            <div v-if="!sidebarCollapsed && $route.name === 'management-prohibited-words'" class="nav-indicator"></div>
          </router-link>
          
          <router-link
            to="/management/homophone-words"
            class="nav-item"
            :class="{ active: $route.name === 'management-homophone-words' }"
          >
            <div class="nav-icon">
              <Volume2 :size="18" />
            </div>
            <span v-if="!sidebarCollapsed" class="nav-label">谐音词管理</span>
            <div v-if="!sidebarCollapsed && $route.name === 'management-homophone-words'" class="nav-indicator"></div>
          </router-link>
          
          <router-link
            to="/management/emojis"
            class="nav-item"
            :class="{ active: $route.name === 'management-emojis' }"
          >
            <div class="nav-icon">
              <Smile :size="18" />
            </div>
            <span v-if="!sidebarCollapsed" class="nav-label">表情管理</span>
            <div v-if="!sidebarCollapsed && $route.name === 'management-emojis'" class="nav-indicator"></div>
          </router-link>
          
          <router-link
            to="/management/whitelist"
            class="nav-item"
            :class="{ active: $route.name === 'management-whitelist' }"
          >
            <div class="nav-icon">
              <Shield :size="18" />
            </div>
            <span v-if="!sidebarCollapsed" class="nav-label">白名单管理</span>
            <div v-if="!sidebarCollapsed && $route.name === 'management-whitelist'" class="nav-indicator"></div>
          </router-link>
        </div>
        
        <div class="nav-section" v-if="canManageUsers">
          <div v-if="!sidebarCollapsed" class="nav-title">系统管理</div>
          <router-link
            to="/management/users"
            class="nav-item"
            :class="{ active: $route.name === 'management-users' }"
          >
            <div class="nav-icon">
              <Users :size="18" />
            </div>
            <span v-if="!sidebarCollapsed" class="nav-label">账号管理</span>
            <div v-if="!sidebarCollapsed && $route.name === 'management-users'" class="nav-indicator"></div>
          </router-link>
        </div>
        
        <div class="nav-section">
          <div v-if="!sidebarCollapsed" class="nav-title">工具</div>
          <a href="/" target="_blank" class="nav-item">
            <div class="nav-icon">
              <ExternalLink :size="18" />
            </div>
            <span v-if="!sidebarCollapsed" class="nav-label">内容检测页面</span>
          </a>
        </div>
      </nav>
      
      <div class="sidebar-footer">
        <div class="user-info" v-if="!sidebarCollapsed">
          <div class="user-avatar">
            <User :size="20" />
          </div>
          <div class="user-details">
            <div class="user-name">{{ authStore.user?.username }}</div>
            <div class="user-role">{{ getRoleText(authStore.user?.role) }}</div>
          </div>
        </div>
        <el-button
          type="text"
          class="logout-btn"
          @click="handleLogout"
          :title="sidebarCollapsed ? '退出登录' : ''"
        >
          <LogOut :size="20" />
          <span v-if="!sidebarCollapsed">退出登录</span>
        </el-button>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部栏 -->
      <header class="main-header">
        <div class="header-content">
          <slot name="header" />
        </div>
        <div class="header-actions">
          <el-button
            type="text"
            @click="themeStore.toggleTheme()"
            class="theme-toggle"
          >
            <component :is="themeStore.currentTheme === 'light' ? 'Moon' : 'Sun'" :size="18" />
          </el-button>
        </div>
      </header>
      
      <!-- 页面内容 -->
      <main class="page-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Menu,
  BarChart3,
  AlertTriangle,
  Volume2,
  ExternalLink,
  User,
  LogOut,
  Moon,
  Sun,
  Users,
  Smile,
  Shield
} from 'lucide-vue-next'

import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const sidebarCollapsed = ref(false)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const getRoleText = (role?: string) => {
  switch (role) {
    case 'super_admin': return '超级管理员'
    case 'admin': return '管理员'
    default: return '用户'
  }
}

const canManageUsers = computed(() => {
  // 超级管理员始终可以管理用户
  if (authStore.user?.role === 'super_admin') {
    return true
  }
  
  const permissions = authStore.user?.permissions
  if (typeof permissions === 'string') {
    try {
      const parsed = JSON.parse(permissions)
      return parsed.user_management?.read === true
    } catch {
      return false
    }
  }
  return permissions?.user_management?.read === true
})

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/management/login')
  } catch {
    // 用户取消
  }
}

// 检查认证状态
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/management/login')
    return
  }
  
  if (!authStore.user) {
    try {
      await authStore.fetchProfile()
    } catch {
      router.push('/management/login')
    }
  }
})
</script>

<style lang="scss" scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(20px);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.05);
  
  &.collapsed {
    width: 72px;
  }
  
  .sidebar-header {
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    border-bottom: 1px solid #f3f4f6;
    
    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 600;
      color: #111827;
      
      .logo-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.25);
      }
      
      .logo-text {
        font-size: 15px;
        font-weight: 600;
        letter-spacing: -0.01em;
      }
    }
    
    .collapse-btn {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      color: #6b7280;
      background: transparent;
      transition: all 0.2s ease;
      
      &:hover {
        background: #f3f4f6;
        color: #374151;
      }
    }
  }
  
  .sidebar-nav {
    flex: 1;
    padding: 24px 0;
    overflow-y: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    
    &::-webkit-scrollbar {
      display: none;
    }
    
    .nav-section {
      margin-bottom: 32px;
      
      .nav-title {
        font-size: 11px;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        margin: 0 24px 16px;
        letter-spacing: 0.05em;
      }
      
      .nav-item {
        position: relative;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 24px;
        margin: 0 12px;
        color: #6b7280;
        text-decoration: none;
        border-radius: 8px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        
        .nav-icon {
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        }
        
        .nav-label {
          font-size: 14px;
          font-weight: 500;
          letter-spacing: -0.01em;
        }
        
        .nav-indicator {
          position: absolute;
          right: 8px;
          width: 6px;
          height: 6px;
          background: #667eea;
          border-radius: 50%;
          opacity: 0;
          transform: scale(0.5);
          transition: all 0.2s ease;
        }
        
        &:hover {
          background: #f8fafc;
          color: #374151;
          transform: translateY(-1px);
          
          .nav-icon {
            transform: scale(1.1);
          }
        }
        
        &.active {
          background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
          color: #667eea;
          border: 1px solid #667eea20;
          
          .nav-indicator {
            opacity: 1;
            transform: scale(1);
          }
          
          .nav-icon {
            color: #667eea;
          }
        }
      }
    }
  }
  
  .sidebar-footer {
    padding: 20px 24px;
    border-top: 1px solid #f3f4f6;
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      padding: 12px;
      background: #f8fafc;
      border-radius: 12px;
      
      .user-avatar {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.15);
      }
      
      .user-details {
        flex: 1;
        
        .user-name {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
          letter-spacing: -0.01em;
        }
        
        .user-role {
          font-size: 12px;
          color: #6b7280;
          margin-top: 1px;
        }
      }
    }
    
    .logout-btn {
      width: 100%;
      justify-content: flex-start;
      gap: 12px;
      padding: 10px 12px;
      color: #6b7280;
      border-radius: 8px;
      transition: all 0.2s ease;
      
      &:hover {
        background: #fef2f2;
        color: #dc2626;
      }
    }
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fafafa;
}

.main-header {
  height: 72px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 10;
  
  .header-content {
    flex: 1;
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .theme-toggle {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      color: #6b7280;
      background: transparent;
      transition: all 0.2s ease;
      
      &:hover {
        background: #f3f4f6;
        color: #374151;
        transform: scale(1.05);
      }
    }
  }
}

.page-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #e5e7eb transparent;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #e5e7eb;
    border-radius: 3px;
    
    &:hover {
      background: #d1d5db;
    }
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
    
    &.collapsed {
      width: 72px;
    }
  }
  
  .page-content {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &.collapsed {
      transform: translateX(0);
      width: 72px;
    }
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .main-header {
    padding: 0 20px;
  }
  
  .page-content {
    padding: 20px;
  }
}

// 暗色主题支持
@media (prefers-color-scheme: dark) {
  .admin-layout {
    background: #0f172a;
  }
  
  .sidebar {
    background: #1e293b;
    border-color: #334155;
    
    .sidebar-header {
      border-color: #334155;
      
      .logo {
        color: #f1f5f9;
      }
    }
    
    .sidebar-nav {
      .nav-title {
        color: #64748b;
      }
      
      .nav-item {
        color: #94a3b8;
        
        &:hover {
          background: #334155;
          color: #f1f5f9;
        }
        
        &.active {
          background: rgba(102, 126, 234, 0.1);
          color: #a5b4fc;
        }
      }
    }
    
    .sidebar-footer {
      border-color: #334155;
      
      .user-info {
        background: #334155;
        
        .user-name {
          color: #f1f5f9;
        }
        
        .user-role {
          color: #94a3b8;
        }
      }
    }
  }
  
  .main-header {
    background: rgba(30, 41, 59, 0.8);
    border-color: #334155;
  }
  
  .main-content {
    background: #0f172a;
  }
}
</style>