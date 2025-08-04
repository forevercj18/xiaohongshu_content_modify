<template>
  <header class="top-nav">
    <div class="nav-left">
      <router-link to="/" class="logo">
        <span class="logo-icon">✨</span>
        <span class="logo-text">小红书内容优化</span>
      </router-link>
    </div>
    
    <nav class="nav-center">
      <router-link to="/" class="nav-link" :class="{ active: $route.name === 'home' }">
        内容优化
      </router-link>
      <router-link to="/history" class="nav-link" :class="{ active: $route.name === 'history' }">
        历史记录
      </router-link>
    </nav>
    
    <div class="nav-right">
      <el-button 
        type="text" 
        class="nav-btn"
        @click="themeStore.toggleTheme()"
      >
        <component :is="themeStore.currentTheme === 'light' ? Moon : Sun" :size="18" />
      </el-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>

<style lang="scss" scoped>
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 1000;
  backdrop-filter: blur(8px);
  
  .nav-left {
    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      color: var(--text-primary);
      font-weight: 600;
      font-size: 16px;
      
      .logo-icon {
        font-size: 20px;
      }
      
      .logo-text {
        @media (max-width: 767px) {
          display: none;
        }
      }
    }
  }
  
  .nav-center {
    display: flex;
    gap: 32px;
    
    .nav-link {
      text-decoration: none;
      color: var(--text-secondary);
      font-weight: 500;
      padding: 8px 16px;
      border-radius: 6px;
      transition: all 0.2s ease;
      
      &:hover {
        color: var(--text-primary);
        background: var(--hover-bg);
      }
      
      &.active {
        color: var(--primary);
        background: var(--primary-10);
      }
    }
    
    @media (max-width: 767px) {
      display: none;
    }
  }
  
  .nav-right {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .nav-btn {
      padding: 8px 16px;
      border: none;
      background: transparent;
      border-radius: 6px;
      cursor: pointer;
      transition: background-color 0.2s ease;
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 14px;
      
      &:hover {
        background: var(--hover-bg);
        color: var(--text-primary);
      }
    }
  }
  
  @media (max-width: 767px) {
    padding: 0 16px;
  }
}
</style>