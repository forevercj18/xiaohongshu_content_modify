import { apiClient } from './index'

export interface HomophoneReplacement {
  id: number
  original_word_id: number
  replacement_word: string
  priority: number
  confidence_score: number
  usage_count: number
  description?: string
  created_at: string
  updated_at: string
}

export interface OriginalWord {
  id: number
  original_word: string
  description?: string
  created_at: string
  updated_at: string
  replacements: HomophoneReplacement[]
}

export interface CreateOriginalWordRequest {
  original_word: string
  description?: string
}

export interface UpdateOriginalWordRequest {
  original_word?: string
  description?: string
}

export interface CreateHomophoneReplacementRequest {
  original_word_id: number
  replacement_word: string
  priority: number
  confidence_score: number
  description?: string
}

export interface UpdateHomophoneReplacementRequest {
  replacement_word?: string
  priority?: number
  confidence_score?: number
  description?: string
}

// 获取所有原词及其谐音词
export const getOriginalWords = async (): Promise<OriginalWord[]> => {
  const response = await apiClient.get('/admin/original-words')
  return response
}

// 创建原词
export const createOriginalWord = async (data: CreateOriginalWordRequest): Promise<OriginalWord> => {
  const response = await apiClient.post('/admin/original-words', data)
  return response
}

// 更新原词
export const updateOriginalWord = async (id: number, data: UpdateOriginalWordRequest): Promise<OriginalWord> => {
  const response = await apiClient.put(`/admin/original-words/${id}`, data)
  return response
}

// 删除原词
export const deleteOriginalWord = async (id: number): Promise<void> => {
  await apiClient.delete(`/admin/original-words/${id}`)
}

// 创建谐音词替换
export const createHomophoneReplacement = async (data: CreateHomophoneReplacementRequest): Promise<HomophoneReplacement> => {
  const response = await apiClient.post('/admin/homophone-replacements', data)
  return response
}

// 更新谐音词替换
export const updateHomophoneReplacement = async (id: number, data: UpdateHomophoneReplacementRequest): Promise<HomophoneReplacement> => {
  const response = await apiClient.put(`/admin/homophone-replacements/${id}`, data)
  return response
}

// 删除谐音词替换
export const deleteHomophoneReplacement = async (id: number): Promise<void> => {
  await apiClient.delete(`/admin/homophone-replacements/${id}`)
}

// 搜索原词
export const searchOriginalWords = async (query: string): Promise<OriginalWord[]> => {
  const response = await apiClient.get('/admin/original-words/search', {
    params: { q: query }
  })
  return response
}

// 批量创建谐音词映射
export const batchCreateHomophoneMappings = async (mappings: Array<{
  original_word: string
  replacement_word: string
  priority: number
  confidence_score: number
  description?: string
}>): Promise<void> => {
  const response = await apiClient.post('/admin/homophone-mappings/batch', { mappings })
  return response
}