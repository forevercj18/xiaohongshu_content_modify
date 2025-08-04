import api from './index'

export interface WhitelistPattern {
  id: number
  prohibited_word: string
  pattern: string
  description?: string
  category?: string
  example?: string
  is_active: number
  priority: number
  created_by?: string
  created_at: string
  updated_at: string
}

export interface WhitelistPatternCreate {
  prohibited_word: string
  pattern: string
  description?: string
  category?: string
  example?: string
  priority?: number
}

export interface WhitelistPatternUpdate {
  pattern?: string
  description?: string
  category?: string
  example?: string
  priority?: number
  is_active?: number
}

export interface WhitelistListResponse {
  patterns: WhitelistPattern[]
  pagination: {
    page: number
    size: number
    total: number
    pages: number
  }
}

export interface WhitelistTestRequest {
  pattern: string
  test_text: string
}

export interface WhitelistTestResponse {
  pattern: string
  test_text: string
  is_match: boolean
  matches: string[]
  match_positions: Array<[number, number]>
}

export interface WhitelistStats {
  overview: {
    total_patterns: number
    active_patterns: number
    inactive_patterns: number
  }
  by_category: Array<{
    category: string
    count: number
  }>
  by_word: Array<{
    word: string
    count: number
  }>
}

// 获取白名单模式列表
export const getWhitelistPatterns = async (params?: {
  page?: number
  size?: number
  prohibited_word?: string
  category?: string
  is_active?: number
}): Promise<WhitelistListResponse> => {
  const response = await api.get('/admin/whitelist/list', { params })
  return response
}

// 创建白名单模式
export const createWhitelistPattern = async (data: WhitelistPatternCreate): Promise<WhitelistPattern> => {
  const response = await api.post('/admin/whitelist/create', data)
  return response
}

// 更新白名单模式
export const updateWhitelistPattern = async (id: number, data: WhitelistPatternUpdate): Promise<WhitelistPattern> => {
  const response = await api.put(`/admin/whitelist/${id}`, data)
  return response
}

// 删除白名单模式
export const deleteWhitelistPattern = async (id: number): Promise<{ message: string }> => {
  const response = await api.delete(`/admin/whitelist/${id}`)
  return response
}

// 获取白名单分类
export const getWhitelistCategories = async (): Promise<{ categories: string[] }> => {
  const response = await api.get('/admin/whitelist/categories')
  return response
}

// 测试白名单模式
export const testWhitelistPattern = async (data: WhitelistTestRequest): Promise<WhitelistTestResponse> => {
  const response = await api.post('/admin/whitelist/test', data)
  return response
}

// 获取白名单统计信息
export const getWhitelistStats = async (): Promise<WhitelistStats> => {
  const response = await api.get('/admin/whitelist/stats')
  return response
}