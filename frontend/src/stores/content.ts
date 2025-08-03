import { defineStore } from 'pinia'
import { analyzeContent, optimizeContent, getContentHistory } from '@/api/content'
import { emojiApi, type EmojiSuggestion, type EmojiRecommendation } from '@/api/emoji'

interface DetectedIssue {
  type: string
  word: string
  position: number
  risk_level: number
  suggestions: string[]
}

interface OptimizationSuggestion {
  type: string
  title: string
  description: string
  priority: string
}

interface HistoryItem {
  id: number
  original_content: string
  optimized_content?: string
  content_score_before?: number
  content_score_after?: number
  created_at: string
}


export const useContentStore = defineStore('content', {
  state: () => ({
    currentContent: '',
    detectedIssues: [] as DetectedIssue[],
    suggestions: [] as OptimizationSuggestion[],
    optimizedContent: '',
    contentScore: 0,
    optimizedScore: 0,
    isAnalyzing: false,
    isOptimizing: false,
    history: [] as HistoryItem[],
    userSession: '',
    // 表情推荐相关状态
    emojiSuggestions: [] as EmojiSuggestion[],
    emojiRecommendations: [] as EmojiRecommendation[],
    isLoadingEmojiSuggestions: false
  }),
  
  actions: {
    setContent(content: string) {
      this.currentContent = content
    },
    
    async analyzeCurrentContent() {
      if (!this.currentContent.trim()) return
      
      this.isAnalyzing = true
      try {
        const result = await analyzeContent({
          content: this.currentContent,
          user_session: this.userSession
        })
        
        this.detectedIssues = result.detected_issues
        this.suggestions = result.suggestions
        this.contentScore = result.content_score
        
        return result
      } catch (error) {
        throw error
      } finally {
        this.isAnalyzing = false
      }
    },
    
    async optimizeCurrentContent(applySuggestions: string[] = []) {
      if (!this.currentContent.trim()) return
      
      this.isOptimizing = true
      try {
        const result = await optimizeContent({
          content: this.currentContent,
          apply_suggestions: applySuggestions,
          user_session: this.userSession
        })
        
        this.optimizedContent = result.optimized_content
        this.optimizedScore = result.score_improvement + this.contentScore
        
        // 优化完成后自动获取表情建议
        this.loadEmojiSuggestions()
        
        return result
      } catch (error) {
        throw error
      } finally {
        this.isOptimizing = false
      }
    },
    
    async loadHistory() {
      try {
        const history = await getContentHistory({
          user_session: this.userSession,
          limit: 20
        })
        this.history = history
      } catch (error) {
        console.error('加载历史记录失败:', error)
      }
    },
    
    initUserSession() {
      if (!this.userSession) {
        this.userSession = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      }
    },
    
    // 表情推荐相关方法
    async loadEmojiSuggestions() {
      if (!this.currentContent.trim() && !this.optimizedContent.trim()) return
      
      this.isLoadingEmojiSuggestions = true
      try {
        const result = await emojiApi.suggestEmojis(
          this.currentContent,
          this.optimizedContent || undefined
        )
        
        this.emojiSuggestions = result.suggestions
        return result
      } catch (error) {
        console.error('加载表情建议失败:', error)
        throw error
      } finally {
        this.isLoadingEmojiSuggestions = false
      }
    },
    
    async getEmojiRecommendations(content?: string) {
      const targetContent = content || this.currentContent || this.optimizedContent
      if (!targetContent.trim()) return
      
      try {
        const result = await emojiApi.recommendEmojis(targetContent)
        this.emojiRecommendations = result.recommendations
        return result
      } catch (error) {
        console.error('获取表情推荐失败:', error)
        throw error
      }
    },
    
    clearContent() {
      this.currentContent = ''
      this.detectedIssues = []
      this.suggestions = []
      this.optimizedContent = ''
      this.contentScore = 0
      this.optimizedScore = 0
      this.emojiSuggestions = []
      this.emojiRecommendations = []
    },
    
    copyOptimizedContent() {
      if (this.optimizedContent) {
        navigator.clipboard.writeText(this.optimizedContent)
      }
    }
  }
})