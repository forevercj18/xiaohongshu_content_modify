<template>
  <div class="detection-card" :class="type">
    <div class="card-header">
      <div class="card-icon" :class="type">
        <component :is="icon" :size="18" />
      </div>
      <div class="card-info">
        <h4>{{ title }}</h4>
        <span v-if="count !== undefined" class="card-status">
          {{ count > 0 ? `发现 ${count} 个问题` : '暂无问题' }}
        </span>
        <span v-else-if="score !== undefined" class="score">
          {{ score }}分
        </span>
        <span v-else-if="suggestions && suggestions.length > 0" class="ai-tag">
          {{ suggestions.length }} 条建议
        </span>
        <span v-else class="card-status">
          暂无数据
        </span>
      </div>
    </div>
    
    <div class="card-content">
      <!-- 违禁词问题列表 -->
      <div v-if="issues && issues.length > 0" class="issue-list">
        <div 
          v-for="issue in issues.slice(0, 3)" 
          :key="`${issue.word}-${issue.position}`"
          class="issue-item"
        >
          <div class="issue-word">{{ issue.word }}</div>
          <div class="issue-risk" :class="getRiskClass(issue.risk_level)">
            {{ getRiskText(issue.risk_level) }}
          </div>
        </div>
        <div v-if="issues.length > 3" class="more-issues">
          还有 {{ issues.length - 3 }} 个问题...
        </div>
      </div>
      
      <!-- 优化建议列表 -->
      <div v-if="suggestions && suggestions.length > 0" class="suggestion-list">
        <div 
          v-for="suggestion in suggestions.slice(0, 3)" 
          :key="suggestion.type"
          class="suggestion-item"
          :class="suggestion.priority"
        >
          <div class="suggestion-title">{{ suggestion.title }}</div>
          <div class="suggestion-desc">{{ suggestion.description }}</div>
        </div>
      </div>
      
      <!-- 分数展示 -->
      <div v-if="score !== undefined" class="score-display">
        <div class="score-circle" :class="getScoreClass(score)">
          <span class="score-value">{{ score }}</span>
          <span class="score-label">分</span>
        </div>
        <div class="score-text">
          {{ getScoreText(score) }}
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="isEmpty" class="empty-state">
        <span>{{ getEmptyText() }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

interface Props {
  title: string
  icon: any
  type: 'warning' | 'info' | 'success'
  count?: number
  score?: number
  issues?: DetectedIssue[]
  suggestions?: OptimizationSuggestion[]
}

const props = defineProps<Props>()

const isEmpty = computed(() => {
  if (props.count !== undefined) return props.count === 0
  if (props.score !== undefined) return props.score === 0
  if (props.issues) return props.issues.length === 0
  if (props.suggestions) return props.suggestions.length === 0
  return true
})

const getRiskClass = (level: number) => {
  switch (level) {
    case 3: return 'high'
    case 2: return 'medium'
    case 1: return 'low'
    default: return 'low'
  }
}

const getRiskText = (level: number) => {
  switch (level) {
    case 3: return '高风险'
    case 2: return '中风险'
    case 1: return '低风险'
    default: return '低风险'
  }
}

const getScoreClass = (score: number) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
}

const getScoreText = (score: number) => {
  if (score >= 80) return '内容质量优秀'
  if (score >= 60) return '内容质量良好'
  if (score >= 40) return '内容质量一般'
  if (score > 0) return '内容需要优化'
  return '请先分析内容'
}

const getEmptyText = () => {
  switch (props.type) {
    case 'warning': return '请先检测内容'
    case 'info': return '请先分析内容'
    case 'success': return '请先检测内容'
    default: return '暂无数据'
  }
}
</script>

<style lang="scss" scoped>
.detection-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  transition: border-color 0.2s ease;
  
  &:hover {
    border-color: var(--primary-30);
  }
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    
    .card-icon {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      
      &.warning { 
        background: var(--warning-10); 
        color: var(--warning); 
      }
      &.info { 
        background: var(--info-10); 
        color: var(--info); 
      }
      &.success { 
        background: var(--success-10); 
        color: var(--success); 
      }
    }
    
    .card-info {
      flex: 1;
      
      h4 {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
      }
      
      .card-status {
        font-size: 12px;
        color: var(--text-secondary);
      }
      
      .score {
        font-size: 12px;
        color: var(--text-primary);
        font-weight: 600;
      }
      
      .ai-tag {
        font-size: 12px;
        color: var(--success);
        font-weight: 500;
      }
    }
  }
  
  .card-content {
    .issue-list {
      .issue-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid var(--border-color);
        
        &:last-child {
          border-bottom: none;
        }
        
        .issue-word {
          font-size: 14px;
          color: var(--text-primary);
          font-weight: 500;
        }
        
        .issue-risk {
          font-size: 12px;
          padding: 2px 8px;
          border-radius: 12px;
          
          &.high {
            background: var(--danger-10);
            color: var(--danger);
          }
          &.medium {
            background: var(--warning-10);
            color: var(--warning);
          }
          &.low {
            background: var(--info-10);
            color: var(--info);
          }
        }
      }
      
      .more-issues {
        font-size: 12px;
        color: var(--text-muted);
        text-align: center;
        padding: 8px 0;
      }
    }
    
    .suggestion-list {
      .suggestion-item {
        padding: 8px 0;
        border-bottom: 1px solid var(--border-color);
        
        &:last-child {
          border-bottom: none;
        }
        
        .suggestion-title {
          font-size: 14px;
          color: var(--text-primary);
          font-weight: 500;
          margin-bottom: 4px;
        }
        
        .suggestion-desc {
          font-size: 12px;
          color: var(--text-secondary);
          line-height: 1.4;
        }
        
        &.high .suggestion-title {
          color: var(--danger);
        }
        &.medium .suggestion-title {
          color: var(--warning);
        }
        &.low .suggestion-title {
          color: var(--info);
        }
      }
    }
    
    .score-display {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .score-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 3px solid;
        
        &.excellent { border-color: var(--success); color: var(--success); }
        &.good { border-color: var(--info); color: var(--info); }
        &.fair { border-color: var(--warning); color: var(--warning); }
        &.poor { border-color: var(--danger); color: var(--danger); }
        
        .score-value {
          font-size: 18px;
          font-weight: 700;
          line-height: 1;
        }
        
        .score-label {
          font-size: 10px;
          line-height: 1;
        }
      }
      
      .score-text {
        flex: 1;
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
    
    .empty-state {
      text-align: center;
      padding: 20px 0;
      color: var(--text-muted);
      font-size: 14px;
    }
  }
}
</style>