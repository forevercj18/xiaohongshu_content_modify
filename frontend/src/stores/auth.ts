import { defineStore } from 'pinia'
import { login, getProfile } from '@/api/auth'

interface User {
  id: number
  username: string
  email?: string
  role: string
  permissions?: Record<string, any>
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('admin_token') || '',
    user: null as User | null,
    isLoading: false
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    hasPermission: (state) => (module: string, action: string) => {
      if (!state.user?.permissions) return false
      return state.user.permissions[module]?.[action] === true
    }
  },
  
  actions: {
    async login(username: string, password: string) {
      this.isLoading = true
      try {
        console.log('开始登录请求:', { username })
        const response = await login({ username, password })
        console.log('登录响应:', response)
        
        this.token = response.access_token
        
        // 解析permissions字段
        const userInfo = { ...response.user_info }
        if (typeof userInfo.permissions === 'string') {
          try {
            userInfo.permissions = JSON.parse(userInfo.permissions)
          } catch (e) {
            console.warn('解析permissions失败:', e)
            userInfo.permissions = {}
          }
        }
        
        this.user = userInfo
        
        localStorage.setItem('admin_token', this.token)
        console.log('登录成功，token已保存')
        return true
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchProfile() {
      try {
        const user = await getProfile()
        this.user = user
      } catch (error) {
        this.logout()
        throw error
      }
    },
    
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('admin_token')
    },
    
    async initAuth() {
      if (this.token && !this.user) {
        try {
          await this.fetchProfile()
        } catch {
          this.logout()
        }
      }
    }
  }
})