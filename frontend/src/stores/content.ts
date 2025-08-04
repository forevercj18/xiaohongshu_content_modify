import { defineStore } from 'pinia'
import { analyzeContent, optimizeContent, getContentHistory } from '@/api/content'
import { emojiApi, type EmojiSuggestion, type EmojiRecommendation } from '@/api/emoji'

interface DetectedIssue {
  id: string
  type: string
  word: string
  start_pos: number
  end_pos: number
  position?: number // 保持向后兼容
  risk_level: number
  category: string
  reason: string
  suggestions: string[]
  context: string
  confidence: number
  severity: string
  replacement_options?: {
    replacement: string
    type: string
    confidence: number
    priority: number
  }[]
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
    isLoadingEmojiSuggestions: false,
    // 高亮交互相关状态
    selectedIssue: null as DetectedIssue | null,
    resolvedIssues: new Set<string>(),
    showReplacementPanel: false,
    showTooltip: false,
    tooltipPosition: { x: 0, y: 0 }
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
    },
    
    // 高亮交互相关方法
    selectIssue(issue: DetectedIssue) {
      this.selectedIssue = issue
    },
    
    clearSelectedIssue() {
      this.selectedIssue = null
      this.showTooltip = false
    },
    
    showIssueTooltip(issue: DetectedIssue, position: { x: number; y: number }) {
      this.selectedIssue = issue
      this.tooltipPosition = position
      this.showTooltip = true
    },
    
    hideTooltip() {
      this.showTooltip = false
    },
    
    replaceWord(issue: DetectedIssue, replacement: string) {
      const startPos = issue.start_pos
      const endPos = issue.end_pos
      
      // 替换文本内容
      const newContent = 
        this.currentContent.substring(0, startPos) + 
        replacement + 
        this.currentContent.substring(endPos)
      
      this.currentContent = newContent
      
      // 标记问题为已解决
      this.resolvedIssues.add(issue.id)
      
      // 更新其他问题的位置（如果有必要）
      this.updateIssuePositions(startPos, endPos - startPos, replacement.length)
      
      // 清除选中状态
      this.clearSelectedIssue()
    },
    
    updateIssuePositions(changeStartPos: number, originalLength: number, newLength: number) {
      const lengthDiff = newLength - originalLength
      
      // 更新后续问题的位置
      this.detectedIssues.forEach(issue => {
        if (issue.start_pos > changeStartPos) {
          issue.start_pos += lengthDiff
          issue.end_pos += lengthDiff
        }
      })
    },
    
    ignoreIssue(issueId: string) {
      this.resolvedIssues.add(issueId)
      if (this.selectedIssue?.id === issueId) {
        this.clearSelectedIssue()
      }
    },
    
    toggleReplacementPanel() {
      this.showReplacementPanel = !this.showReplacementPanel
    },
    
    applyAllHomophones() {
      const homophoneIssues = this.detectedIssues.filter(
        issue => issue.type === 'homophone_word' && !this.resolvedIssues.has(issue.id)
      )
      
      // 从后往前替换，避免位置偏移问题
      const sortedIssues = [...homophoneIssues].sort((a, b) => b.start_pos - a.start_pos)
      
      for (const issue of sortedIssues) {
        if (issue.suggestions.length > 0) {
          this.replaceWord(issue, issue.suggestions[0])
        } else if (issue.replacement_options && issue.replacement_options.length > 0) {
          const bestOption = issue.replacement_options.reduce((best, current) => {
            return current.priority > best.priority ? current : best
          })
          this.replaceWord(issue, bestOption.replacement)
        }
      }
    },
    
    resetResolvedIssues() {
      this.resolvedIssues.clear()
      this.clearSelectedIssue()
    }
  }
})