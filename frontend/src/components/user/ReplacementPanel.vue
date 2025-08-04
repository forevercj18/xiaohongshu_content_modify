<template>
  <div v-if="visible" class="replacement-panel">
    <div class="panel-header">
      <h3>批量替换工具</h3>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>
    
    <div class="panel-content">
      <!-- 统计信息 -->
      <div class="stats-section">
        <div class="stat-item">
          <span class="label">违禁词</span>
          <span class="count prohibited">{{ prohibitedCount }}</span>
        </div>
        <div class="stat-item">
          <span class="label">谐音词机会</span>
          <span class="count homophone">{{ homophoneCount }}</span>
        </div>
        <div class="stat-item">
          <span class="label">总问题</span>
          <span class="count total">{{ totalCount }}</span>
        </div>
      </div>
      
      <!-- 批量操作 -->
      <div class="batch-actions">
        <button 
          @click="handleApplyAllHomophones"
          :disabled="homophoneCount === 0"
          class="batch-btn primary"
        >
          应用所有谐音词替换 ({{ homophoneCount }})
        </button>
        <button 
          @click="handleApplyRecommended"
          :disabled="recommendedCount === 0"
          class="batch-btn secondary"
        >
          应用推荐替换 ({{ recommendedCount }})
        </button>
      </div>
      
      <!-- 问题列表 -->
      <div class="issues-list">
        <div class="list-header">
          <span>待处理问题</span>
          <div class="filter-buttons">
            <button 
              :class="{ active: filter === 'all' }"
              @click="filter = 'all'"
              class="filter-btn"
            >
              全部
            </button>
            <button 
              :class="{ active: filter === 'prohibited' }"
              @click="filter = 'prohibited'"
              class="filter-btn"
            >
              违禁词
            </button>
            <button 
              :class="{ active: filter === 'homophone' }"
              @click="filter = 'homophone'"
              class="filter-btn"
            >
              谐音词
            </button>
          </div>
        </div>
        
        <div class="issues-container">
          <div 
            v-for="issue in filteredIssues"
            :key="issue.id"
            class="issue-item"
            :class="{ 
              active: selectedIssue?.id === issue.id,
              resolved: resolvedIssues.has(issue.id)
            }"
            @click="selectIssue(issue)"
          >
            <div class="issue-header">
              <span class="word">{{ issue.word }}</span>
              <span class="type-badge" :class="issue.type">
                {{ getTypeText(issue.type) }}
              </span>
              <span class="severity" :class="issue.severity">
                {{ getSeverityText(issue.severity) }}
              </span>
            </div>
            
            <div class="issue-content">
              <div class="reason">{{ issue.reason }}</div>
              <div v-if="issue.suggestions.length > 0" class="suggestions">
                <span class="suggestions-label">建议:</span>
                <span class="suggestions-text">
                  {{ issue.suggestions.slice(0, 2).join(', ') }}
                  <span v-if="issue.suggestions.length > 2">...</span>
                </span>
              </div>
            </div>
            
            <div class="issue-actions">
              <button 
                v-if="issue.type === 'homophone_word'"
                @click.stop="handleQuickReplace(issue)"
                class="quick-btn"
                :disabled="resolvedIssues.has(issue.id)"
              >
                快速替换
              </button>
              <button 
                @click.stop="handleIgnoreIssue(issue)"
                class="ignore-btn"
                :disabled="resolvedIssues.has(issue.id)"
              >
                忽略
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 详细替换选项 -->
      <div v-if="selectedIssue" class="detail-panel">
        <div class="detail-header">
          <span>{{ selectedIssue.word }} - 替换选项</span>
        </div>
        
        <div class="replacement-options">
          <div 
            v-for="(suggestion, index) in selectedIssue.suggestions"
            :key="index"
            class="replacement-option"
            @click="handleReplaceWord(selectedIssue, suggestion)"
          >
            <span class="replacement-text">{{ suggestion }}</span>
            <span class="replace-icon">→</span>
          </div>
          
          <!-- 谐音词的高级选项 -->
          <div 
            v-if="selectedIssue.type === 'homophone_word' && selectedIssue.replacement_options"
            class="advanced-options"
          >
            <div class="options-title">高级选项</div>
            <div 
              v-for="option in selectedIssue.replacement_options"
              :key="option.replacement"
              class="advanced-option"
              @click="handleReplaceWord(selectedIssue, option.replacement)"
            >
              <div class="option-main">
                <span class="replacement-text">{{ option.replacement }}</span>
                <span class="option-type">{{ getReplacementTypeText(option.type) }}</span>
              </div>
              <div class="option-meta">
                <span class="confidence">{{ Math.round(option.confidence * 100) }}%</span>
                <span class="priority">优先级: {{ option.priority }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface DetectedIssue {
  id: string
  type: string
  word: string
  start_pos: number
  end_pos: number
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

interface Props {
  issues: DetectedIssue[]
  visible: boolean
  resolvedIssues: Set<string>
}

interface Emits {
  (e: 'close'): void
  (e: 'replace-word', issue: DetectedIssue, replacement: string): void
  (e: 'ignore-issue', issueId: string): void
  (e: 'apply-all-homophones'): void
  (e: 'navigate-to-issue', issue: DetectedIssue): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const filter = ref<'all' | 'prohibited' | 'homophone'>('all')
const selectedIssue = ref<DetectedIssue | null>(null)

// 统计数据
const prohibitedCount = computed(() => 
  props.issues.filter(issue => 
    issue.type === 'prohibited_word' && !props.resolvedIssues.has(issue.id)
  ).length
)

const homophoneCount = computed(() => 
  props.issues.filter(issue => 
    issue.type === 'homophone_word' && !props.resolvedIssues.has(issue.id)
  ).length
)

const totalCount = computed(() => 
  props.issues.filter(issue => !props.resolvedIssues.has(issue.id)).length
)

const recommendedCount = computed(() => 
  props.issues.filter(issue => 
    !props.resolvedIssues.has(issue.id) && 
    issue.suggestions.length > 0 && 
    issue.confidence > 0.8
  ).length
)

// 过滤后的问题列表
const filteredIssues = computed(() => {
  let filtered = props.issues.filter(issue => !props.resolvedIssues.has(issue.id))
  
  if (filter.value === 'prohibited') {
    filtered = filtered.filter(issue => issue.type === 'prohibited_word')
  } else if (filter.value === 'homophone') {
    filtered = filtered.filter(issue => issue.type === 'homophone_word')
  }
  
  // 按严重程度排序
  return filtered.sort((a, b) => {
    const severityOrder = { high: 3, medium: 2, low: 1 }
    return severityOrder[b.severity] - severityOrder[a.severity] || 
           b.risk_level - a.risk_level
  })
})

// 获取类型文本
const getTypeText = (type: string): string => {
  switch (type) {
    case 'prohibited_word': return '违禁词'
    case 'homophone_word': return '谐音词'
    default: return '未知'
  }
}

// 获取严重程度文本
const getSeverityText = (severity: string): string => {
  switch (severity) {
    case 'high': return '高'
    case 'medium': return '中'
    case 'low': return '低'
    default: return '-'
  }
}

// 获取替换类型文本
const getReplacementTypeText = (type: string): string => {
  switch (type) {
    case 'pinyin': return '拼音'
    case 'similar': return '相似字'
    case 'symbol': return '符号'
    case 'emoji': return '表情'
    default: return '其他'
  }
}

// 选择问题
const selectIssue = (issue: DetectedIssue) => {
  selectedIssue.value = issue
  emit('navigate-to-issue', issue)
}

// 处理快速替换
const handleQuickReplace = (issue: DetectedIssue) => {
  if (issue.suggestions.length > 0) {
    emit('replace-word', issue, issue.suggestions[0])
  } else if (issue.replacement_options && issue.replacement_options.length > 0) {
    const bestOption = issue.replacement_options.reduce((best, current) => {
      return current.priority > best.priority ? current : best
    })
    emit('replace-word', issue, bestOption.replacement)
  }
}

// 处理忽略问题
const handleIgnoreIssue = (issue: DetectedIssue) => {
  emit('ignore-issue', issue.id)
  if (selectedIssue.value?.id === issue.id) {
    selectedIssue.value = null
  }
}

// 处理替换词汇
const handleReplaceWord = (issue: DetectedIssue, replacement: string) => {
  emit('replace-word', issue, replacement)
  selectedIssue.value = null
}

// 处理应用所有谐音词
const handleApplyAllHomophones = () => {
  emit('apply-all-homophones')
}

// 处理应用推荐替换
const handleApplyRecommended = () => {
  const recommendedIssues = props.issues.filter(issue => 
    !props.resolvedIssues.has(issue.id) && 
    issue.suggestions.length > 0 && 
    issue.confidence > 0.8
  )
  
  for (const issue of recommendedIssues) {
    emit('replace-word', issue, issue.suggestions[0])
  }
}
</script>

<style lang="scss" scoped>
.replacement-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background: white;
  border-left: 1px solid var(--border-color);
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  
  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .close-btn {
      width: 28px;
      height: 28px;
      border: none;
      background: none;
      color: var(--text-secondary);
      cursor: pointer;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      
      &:hover {
        background: var(--hover-bg);
        color: var(--text-primary);
      }
    }
  }
  
  .panel-content {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  .stats-section {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    
    .stat-item {
      text-align: center;
      
      .label {
        display: block;
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 4px;
      }
      
      .count {
        display: block;
        font-size: 18px;
        font-weight: 600;
        
        &.prohibited {
          color: #dc2626;
        }
        
        &.homophone {
          color: #22c55e;
        }
        
        &.total {
          color: var(--text-primary);
        }
      }
    }
  }
  
  .batch-actions {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .batch-btn {
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      &.primary {
        background: var(--primary);
        color: white;
        border: 1px solid var(--primary);
        
        &:hover:not(:disabled) {
          background: var(--primary-dark);
          transform: translateY(-1px);
        }
      }
      
      &.secondary {
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        
        &:hover:not(:disabled) {
          background: var(--hover-bg);
        }
      }
    }
  }
  
  .issues-list {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    
    .list-header {
      padding: 12px 20px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      
      .filter-buttons {
        display: flex;
        gap: 4px;
        
        .filter-btn {
          padding: 4px 8px;
          border: none;
          background: var(--bg-secondary);
          color: var(--text-secondary);
          border-radius: 4px;
          font-size: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &.active {
            background: var(--primary);
            color: white;
          }
          
          &:hover:not(.active) {
            background: var(--hover-bg);
            color: var(--text-primary);
          }
        }
      }
    }
    
    .issues-container {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
      
      .issue-item {
        padding: 12px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover {
          border-color: var(--primary);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        &.active {
          border-color: var(--primary);
          background: var(--primary-10);
        }
        
        &.resolved {
          opacity: 0.6;
          pointer-events: none;
        }
        
        .issue-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          
          .word {
            font-weight: 600;
            color: var(--text-primary);
          }
          
          .type-badge {
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 500;
            
            &.prohibited_word {
              background: #fef2f2;
              color: #dc2626;
            }
            
            &.homophone_word {
              background: #f0fdf4;
              color: #22c55e;
            }
          }
          
          .severity {
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 500;
            
            &.high {
              background: #fee2e2;
              color: #dc2626;
            }
            
            &.medium {
              background: #fef3c7;
              color: #d97706;
            }
            
            &.low {
              background: #f0f9ff;
              color: #0284c7;
            }
          }
        }
        
        .issue-content {
          margin-bottom: 8px;
          
          .reason {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 4px;
          }
          
          .suggestions {
            font-size: 11px;
            color: var(--text-secondary);
            
            .suggestions-label {
              font-weight: 500;
            }
          }
        }
        
        .issue-actions {
          display: flex;
          gap: 6px;
          
          .quick-btn,
          .ignore-btn {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s ease;
            
            &:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }
          }
          
          .quick-btn {
            background: var(--primary);
            color: white;
            border: 1px solid var(--primary);
            
            &:hover:not(:disabled) {
              background: var(--primary-dark);
            }
          }
          
          .ignore-btn {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            
            &:hover:not(:disabled) {
              background: var(--hover-bg);
              color: var(--text-primary);
            }
          }
        }
      }
    }
  }
  
  .detail-panel {
    border-top: 1px solid var(--border-color);
    background: var(--bg-secondary);
    
    .detail-header {
      padding: 12px 20px;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      border-bottom: 1px solid var(--border-color);
    }
    
    .replacement-options {
      padding: 12px;
      max-height: 200px;
      overflow-y: auto;
      
      .replacement-option {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        margin-bottom: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover {
          border-color: var(--primary);
          background: white;
        }
        
        .replacement-text {
          font-weight: 500;
          color: var(--text-primary);
        }
        
        .replace-icon {
          color: var(--primary);
        }
      }
      
      .advanced-options {
        margin-top: 12px;
        
        .options-title {
          font-size: 12px;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 8px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .advanced-option {
          padding: 8px 12px;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          margin-bottom: 6px;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover {
            border-color: var(--primary);
            background: white;
          }
          
          .option-main {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
            
            .replacement-text {
              font-weight: 500;
              color: var(--text-primary);
            }
            
            .option-type {
              padding: 1px 6px;
              background: var(--bg-primary);
              border-radius: 8px;
              font-size: 10px;
              color: var(--text-secondary);
            }
          }
          
          .option-meta {
            display: flex;
            gap: 12px;
            font-size: 10px;
            color: var(--text-secondary);
            
            .confidence {
              color: var(--success);
            }
          }
        }
      }
    }
  }
}

// 动画
.replacement-panel {
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}
</style>