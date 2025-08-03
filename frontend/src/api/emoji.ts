import { apiClient } from './index'

// 表情相关接口类型定义
export interface EmojiItem {
  id: number
  code: string
  name: string
  emoji_type: string
  category: string
  subcategory?: string
  description?: string
  keywords: string[]
  usage_count: number
  priority: number
  is_verified: number
  status: number
  created_by?: string
  created_at?: string
  updated_at?: string
}

export interface EmojiCategory {
  id: number
  name: string
  display_name: string
  description?: string
  icon?: string
  emoji_count: number
}

export interface CreateEmojiRequest {
  code: string
  name: string
  emoji_type: string
  category: string
  subcategory?: string
  description?: string
  keywords?: string[]
  priority?: number
}

export interface UpdateEmojiRequest {
  name?: string
  category?: string
  subcategory?: string
  description?: string
  keywords?: string[]
  priority?: number
  status?: number
}

// 表情推荐接口
export interface EmojiRecommendation {
  code: string
  name: string
  emoji_type: string
  category: string
  description?: string
  keywords: string[]
  reason: string
  confidence: number
  match_category: string
  usage_count: number
  priority: number
}

export interface EmojiRecommendationResponse {
  recommendations: EmojiRecommendation[]
  content_analysis: {
    content_types: string[]
    emotions: string[]
    keywords: string[]
  }
  total: number
}

export interface EmojiSuggestion {
  描述: string
  建议: string
  场景: string[]
  推荐理由: string
  置信度: number
}

export interface EmojiSuggestionResponse {
  suggestions: EmojiSuggestion[]
  analysis: {
    content_types: string[]
    emotions: string[]
    keywords: string[]
  }
  message: string
}

// 用户端API (无需认证)
export const emojiApi = {
  // 获取表情列表
  getEmojiList: (params?: {
    category?: string
    emoji_type?: string
    keyword?: string
    limit?: number
  }) => {
    return apiClient.get('/emoji/list', { params })
  },

  // 获取表情分类
  getCategories: () => {
    return apiClient.get('/emoji/categories')
  },

  // 搜索表情
  searchEmojis: (keyword: string) => {
    return apiClient.get('/emoji/search', { 
      params: { q: keyword } 
    })
  },

  // 记录表情使用
  logUsage: (data: {
    emoji_id: number
    usage_type: string
    user_session?: string
    content_id?: number
    position?: number
    context?: string
  }) => {
    return apiClient.post('/emoji/usage', data)
  },

  // 智能表情推荐
  recommendEmojis: (content: string, limit: number = 8): Promise<EmojiRecommendationResponse> => {
    return apiClient.post('/emoji/recommend', { content, limit })
  },

  // 内容优化表情建议
  suggestEmojis: (originalContent: string, optimizedContent?: string): Promise<EmojiSuggestionResponse> => {
    return apiClient.post('/emoji/suggest', { 
      original_content: originalContent,
      optimized_content: optimizedContent 
    })
  }
}

// 管理员API (需要认证)
export const emojiAdminApi = {
  // 获取表情列表 (管理员)
  getEmojiList: (params?: {
    category?: string
    status?: number
    page?: number
    size?: number
  }) => {
    return apiClient.get('/emoji/admin/list', { params })
  },

  // 创建表情
  createEmoji: (data: CreateEmojiRequest) => {
    return apiClient.post('/emoji/admin/create', data)
  },

  // 更新表情
  updateEmoji: (emojiId: number, data: UpdateEmojiRequest) => {
    return apiClient.put(`/emoji/admin/${emojiId}`, data)
  },

  // 删除表情
  deleteEmoji: (emojiId: number) => {
    return apiClient.delete(`/emoji/admin/${emojiId}`)
  },

  // 获取表情统计
  getStats: () => {
    return apiClient.get('/emoji/admin/stats')
  }
}

// 导出所有表情相关API
export { emojiApi as default }