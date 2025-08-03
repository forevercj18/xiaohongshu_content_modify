import { apiClient } from './index'

export interface DashboardStats {
  total_detections: number
  total_optimizations: number
  total_prohibited_words: number
  total_homophone_words: number
  recent_activity: Array<{
    type: 'detection' | 'optimization'
    content_preview: string
    score_before?: number
    score_after?: number
    created_at: string
  }>
}

export interface UsageStats {
  date: string
  detections: number
  optimizations: number
  avg_processing_time: number
}

export interface UsageStatsQuery {
  days?: number
  start_date?: string
  end_date?: string
}

// 获取仪表板统计数据
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await apiClient.get('/stats/dashboard')
  return response
}

// 获取使用统计数据
export const getUsageStats = async (query: UsageStatsQuery = {}): Promise<UsageStats[]> => {
  const response = await apiClient.get('/stats/usage', {
    params: query
  })
  return response
}

// 获取违禁词统计
export const getProhibitedWordsStats = async (): Promise<{
  total: number
  by_category: Record<string, number>
  by_severity: Record<string, number>
  active_count: number
  inactive_count: number
}> => {
  const response = await apiClient.get('/stats/prohibited-words/categories')
  return response.data
}

// 获取谐音词统计
export const getHomophoneWordsStats = async (): Promise<{
  total_original_words: number
  total_replacements: number
  average_replacements_per_word: number
  high_priority_count: number
  usage_distribution: Array<{
    original_word: string
    usage_count: number
  }>
}> => {
  const response = await apiClient.get('/stats/homophone-words/usage')
  return response.data
}

// 导出统计数据
export const exportStatsData = async (type: 'dashboard' | 'usage' | 'prohibited-words' | 'homophone-words'): Promise<Blob> => {
  const response = await apiClient.get(`/stats/export/${type}`, {
    responseType: 'blob'
  })
  return response.data
}