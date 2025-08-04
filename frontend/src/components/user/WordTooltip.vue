<template>
  <div 
    v-if="visible && issue"
    class="word-tooltip"
    :style="tooltipStyle"
    @click.stop
  >
    <div class="tooltip-header">
      <div class="word-info">
        <span class="word">{{ issue.word }}</span>
        <span class="type-badge" :class="issue.type">
          {{ getTypeText(issue.type) }}
        </span>
      </div>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>
    
    <div class="tooltip-content">
      <!-- 问题描述 -->
      <div class="issue-description">
        <div class="description-header">
          <span class="icon">{{ getTypeIcon(issue.type) }}</span>
          <span class="text">{{ issue.reason }}</span>
        </div>
        <div class="confidence" v-if="issue.confidence">
          置信度: {{ Math.round(issue.confidence * 100) }}%
        </div>
      </div>
      
      <!-- 上下文 -->
      <div v-if="issue.context" class="context-section">
        <div class="section-title">上下文</div>
        <div class="context-text">{{ issue.context }}</div>
      </div>
      
      <!-- 建议替换 -->
      <div v-if="issue.suggestions.length > 0" class="suggestions-section">
        <div class="section-title">建议替换</div>
        <div class="suggestions-list">
          <button
            v-for="(suggestion, index) in issue.suggestions"
            :key="index"
            @click="handleSuggestionClick(suggestion)"
            class="suggestion-item"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
      
      <!-- 替换选项（仅谐音词） -->
      <div v-if="issue.type === 'homophone_word' && issue.replacement_options" class="replacement-options">
        <div class="section-title">替换选项</div>
        <div class="options-list">
          <div
            v-for="option in issue.replacement_options"
            :key="option.replacement"
            class="option-item"
            @click="handleReplacementClick(option)"
          >
            <div class="option-content">
              <span class="replacement-word">{{ option.replacement }}</span>
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
    
    <div class="tooltip-actions">
      <button 
        v-if="issue.type === 'prohibited_word'"
        @click="handleIgnore"
        class="action-btn secondary"
      >
        忽略此次
      </button>
      <button 
        v-if="issue.type === 'homophone_word'"
        @click="handleApplyBest"
        class="action-btn primary"
      >
        应用最佳替换
      </button>
      <button 
        @click="handleEdit"
        class="action-btn primary"
      >
        手动编辑
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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
  issue: DetectedIssue | null
  visible: boolean
  position: { x: number; y: number } | null
}

interface Emits {
  (e: 'close'): void
  (e: 'replace-word', suggestion: string): void
  (e: 'ignore-issue', issueId: string): void
  (e: 'edit-manually', issue: DetectedIssue): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 计算Tooltip位置
const tooltipStyle = computed(() => {
  if (!props.position) return {}
  
  return {
    left: props.position.x + 'px',
    top: props.position.y + 'px',
    transform: 'translate(-50%, -100%)'
  }
})

// 获取类型文本
const getTypeText = (type: string): string => {
  switch (type) {
    case 'prohibited_word':
      return '违禁词'
    case 'homophone_word':
      return '谐音词'
    default:
      return '未知类型'
  }
}

// 获取类型图标
const getTypeIcon = (type: string): string => {
  switch (type) {
    case 'prohibited_word':
      return '⚠️'
    case 'homophone_word':
      return '🔄'
    default:
      return '❓'
  }
}

// 获取替换类型文本
const getReplacementTypeText = (type: string): string => {
  switch (type) {
    case 'pinyin':
      return '拼音替换'
    case 'similar':
      return '相似字'
    case 'symbol':
      return '符号替换'
    case 'emoji':
      return '表情符号'
    default:
      return '其他'
  }
}

// 处理建议点击
const handleSuggestionClick = (suggestion: string) => {
  emit('replace-word', suggestion)
}

// 处理替换选项点击
const handleReplacementClick = (option: any) => {
  emit('replace-word', option.replacement)
}

// 处理忽略
const handleIgnore = () => {
  if (props.issue) {
    emit('ignore-issue', props.issue.id)
  }
}

// 处理应用最佳替换
const handleApplyBest = () => {
  if (props.issue?.replacement_options && props.issue.replacement_options.length > 0) {
    // 选择优先级最高的替换
    const bestOption = props.issue.replacement_options.reduce((best, current) => {
      if (current.priority > best.priority) return current
      if (current.priority === best.priority && current.confidence > best.confidence) return current
      return best
    })
    emit('replace-word', bestOption.replacement)
  } else if (props.issue?.suggestions.length > 0) {
    emit('replace-word', props.issue.suggestions[0])
  }
}

// 处理手动编辑
const handleEdit = () => {
  if (props.issue) {
    emit('edit-manually', props.issue)
  }
}
</script>

<style lang="scss" scoped>
.word-tooltip {
  position: fixed;
  z-index: 1000;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  min-width: 280px;
  max-width: 400px;
  backdrop-filter: blur(20px);
  
  .tooltip-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    
    .word-info {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .word {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .type-badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        
        &.prohibited_word {
          background: #fef2f2;
          color: #dc2626;
          border: 1px solid #fecaca;
        }
        
        &.homophone_word {
          background: #f0fdf4;
          color: #22c55e;
          border: 1px solid #bbf7d0;
        }
      }
    }
    
    .close-btn {
      width: 24px;
      height: 24px;
      border: none;
      background: none;
      color: var(--text-secondary);
      cursor: pointer;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      
      &:hover {
        background: var(--hover-bg);
        color: var(--text-primary);
      }
    }
  }
  
  .tooltip-content {
    padding: 16px;
    
    .issue-description {
      margin-bottom: 16px;
      
      .description-header {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 4px;
        
        .icon {
          font-size: 16px;
          line-height: 1;
        }
        
        .text {
          flex: 1;
          font-size: 14px;
          line-height: 1.4;
          color: var(--text-primary);
        }
      }
      
      .confidence {
        font-size: 12px;
        color: var(--text-secondary);
        margin-left: 24px;
      }
    }
    
    .context-section {
      margin-bottom: 16px;
      
      .context-text {
        padding: 8px 12px;
        background: var(--bg-secondary);
        border-radius: 6px;
        font-size: 13px;
        line-height: 1.4;
        color: var(--text-secondary);
        margin-top: 4px;
      }
    }
    
    .suggestions-section,
    .replacement-options {
      margin-bottom: 16px;
      
      .suggestions-list {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
        
        .suggestion-item {
          padding: 4px 12px;
          background: var(--primary-10);
          color: var(--primary);
          border: 1px solid var(--primary-20);
          border-radius: 16px;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover {
            background: var(--primary);
            color: white;
            transform: translateY(-1px);
          }
        }
      }
      
      .options-list {
        margin-top: 8px;
        
        .option-item {
          padding: 8px 12px;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          margin-bottom: 6px;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover {
            border-color: var(--primary);
            background: var(--primary-10);
          }
          
          .option-content {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
            
            .replacement-word {
              font-weight: 500;
              color: var(--text-primary);
            }
            
            .option-type {
              padding: 1px 6px;
              background: var(--bg-secondary);
              border-radius: 8px;
              font-size: 11px;
              color: var(--text-secondary);
            }
          }
          
          .option-meta {
            display: flex;
            gap: 12px;
            font-size: 11px;
            color: var(--text-secondary);
            
            .confidence {
              color: var(--success);
            }
          }
        }
      }
    }
    
    .section-title {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-primary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
  }
  
  .tooltip-actions {
    padding: 12px 16px;
    border-top: 1px solid var(--border-color);
    display: flex;
    gap: 8px;
    justify-content: flex-end;
    
    .action-btn {
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &.primary {
        background: var(--primary);
        color: white;
        border: 1px solid var(--primary);
        
        &:hover {
          background: var(--primary-dark);
          transform: translateY(-1px);
        }
      }
      
      &.secondary {
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        
        &:hover {
          background: var(--hover-bg);
        }
      }
    }
  }
}

// 动画
.word-tooltip {
  animation: tooltipFadeIn 0.2s ease-out;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -100%) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -100%) scale(1);
  }
}
</style>