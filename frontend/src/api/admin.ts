import { apiClient } from './index'

// 管理员用户相关接口
export const adminApi = {
  // 获取管理员列表
  getAdminUsers: (params?: {
    page?: number
    limit?: number
    search?: string
    role?: string
  }) => {
    return apiClient.get('/admin/users', { params })
  },

  // 创建管理员
  createAdminUser: (data: {
    username: string
    password: string
    email: string
    role: string
    permissions?: any
  }) => {
    return apiClient.post('/admin/users', data)
  },

  // 更新管理员状态
  updateAdminStatus: (userId: number, status: number) => {
    return apiClient.put(`/admin/users/${userId}/status`, null, {
      params: { status }
    })
  },

  // 重置管理员密码
  resetAdminPassword: (userId: number, data: { new_password: string }) => {
    return apiClient.post(`/admin/users/${userId}/reset-password`, data)
  },

  // 删除管理员
  deleteAdminUser: (userId: number) => {
    return apiClient.delete(`/admin/users/${userId}`)
  },

  // 获取管理员日志
  getAdminLogs: (params?: {
    page?: number
    limit?: number
    action?: string
    target_type?: string
    admin_username?: string
  }) => {
    return apiClient.get('/admin/logs', { params })
  },

  // 获取管理员统计概要
  getAdminStatsSummary: () => {
    return apiClient.get('/admin/stats/summary')
  }
}