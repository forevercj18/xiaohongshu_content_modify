import { defineStore } from 'pinia'

export type Theme = 'light' | 'dark'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: 'light' as Theme
  }),
  
  actions: {
    initTheme() {
      // 从本地存储获取主题设置
      const savedTheme = localStorage.getItem('theme') as Theme
      if (savedTheme) {
        this.currentTheme = savedTheme
      } else {
        // 检测系统主题偏好
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        this.currentTheme = prefersDark ? 'dark' : 'light'
      }
      
      this.applyTheme()
      
      // 监听系统主题变化
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
          this.currentTheme = e.matches ? 'dark' : 'light'
          this.applyTheme()
        }
      })
    },
    
    toggleTheme() {
      this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light'
      this.applyTheme()
      localStorage.setItem('theme', this.currentTheme)
    },
    
    setTheme(theme: Theme) {
      this.currentTheme = theme
      this.applyTheme()
      localStorage.setItem('theme', theme)
    },
    
    applyTheme() {
      document.documentElement.setAttribute('data-theme', this.currentTheme)
    }
  }
})