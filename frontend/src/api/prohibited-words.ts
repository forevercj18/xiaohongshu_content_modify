import { apiClient } from './index'

export interface ProhibitedWord {
  id: number
  word: string
  category: string
  severity: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateProhibitedWordRequest {
  word: string
  category: string
  severity: string
  description?: string
  is_active?: boolean
}

export interface UpdateProhibitedWordRequest {
  word?: string
  category?: string
  severity?: string
  description?: string
  is_active?: boolean
}

// 获取所有违禁词
export const getProhibitedWords = async (): Promise<ProhibitedWord[]> => {
  const response = await apiClient.get('/admin/prohibited-words')
  return response
}

// 创建违禁词
export const createProhibitedWord = async (data: CreateProhibitedWordRequest): Promise<ProhibitedWord> => {
  const response = await apiClient.post('/admin/prohibited-words', data)
  return response
}

// 更新违禁词
export const updateProhibitedWord = async (id: number, data: UpdateProhibitedWordRequest): Promise<ProhibitedWord> => {
  const response = await apiClient.put(`/admin/prohibited-words/${id}`, data)
  return response
}

// 删除违禁词
export const deleteProhibitedWord = async (id: number): Promise<void> => {
  await apiClient.delete(`/admin/prohibited-words/${id}`)
}

// 批量创建违禁词
export const batchCreateProhibitedWords = async (words: CreateProhibitedWordRequest[]): Promise<ProhibitedWord[]> => {
  const response = await apiClient.post('/admin/prohibited-words/batch', { words })
  return response
}

// 搜索违禁词
export const searchProhibitedWords = async (query: string): Promise<ProhibitedWord[]> => {
  const response = await apiClient.get('/admin/prohibited-words/search', {
    params: { q: query }
  })
  return response
}