import api from './index'

export interface ContentRequest {
  content: string
  user_session?: string
}

export interface DetectedIssue {
  type: string
  word: string
  position: number
  risk_level: number
  suggestions: string[]
}

export interface OptimizationSuggestion {
  type: string
  title: string
  description: string
  priority: string
}

export interface ContentAnalysisResponse {
  detected_issues: DetectedIssue[]
  content_score: number
  suggestions: OptimizationSuggestion[]
  processing_time: number
}

export interface ContentOptimizeRequest {
  content: string
  apply_suggestions?: string[]
  user_session?: string
}

export interface ContentOptimizeResponse {
  optimized_content: string
  applied_changes: Array<Record<string, any>>
  score_improvement: number
  processing_time: number
}

export interface HistoryItem {
  id: number
  original_content: string
  optimized_content?: string
  content_score_before?: number
  content_score_after?: number
  created_at: string
}

export interface HistoryRequest {
  user_session?: string
  limit?: number
}

export const analyzeContent = (data: ContentRequest): Promise<ContentAnalysisResponse> => {
  return api.post('/content/analyze', data)
}

export const optimizeContent = (data: ContentOptimizeRequest): Promise<ContentOptimizeResponse> => {
  return api.post('/content/optimize', data)
}

export const getContentHistory = (params: HistoryRequest): Promise<HistoryItem[]> => {
  return api.get('/content/history', { params })
}