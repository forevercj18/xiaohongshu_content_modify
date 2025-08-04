<template>
  <div class="highlight-editor">
    <div class="editor-container">
      <!-- 高亮显示层 -->
      <div 
        class="highlight-layer"
        :style="{ minHeight: textareaHeight + 'px' }"
      >
        <div class="highlight-content" v-html="highlightedContent"></div>
      </div>
      
      <!-- 文本输入层 -->
      <textarea
        ref="textareaRef"
        v-model="localContent"
        @input="handleInput"
        @scroll="handleScroll"
        @focus="handleFocus"
        @blur="handleBlur"
        class="text-input"
        :placeholder="placeholder"
        :maxlength="maxLength"
        spellcheck="false"
      ></textarea>
      
      <!-- 字数统计 -->
      <div class="char-count">
        {{ localContent.length }} / {{ maxLength }}
      </div>
    </div>
    
    <!-- 问题导航器 -->
    <div v-if="issues.length > 0" class="issue-navigator">
      <div class="navigator-info">
        <span class="issue-count">{{ issues.length }}个问题</span>
        <span v-if="currentIssueIndex >= 0" class="current-position">
          第{{ currentIssueIndex + 1 }}个
        </span>
      </div>
      <div class="navigator-controls">
        <button 
          @click="navigateToPrevious"
          :disabled="currentIssueIndex <= 0"
          class="nav-btn"
          title="上一个问题"
        >
          ↑
        </button>
        <button 
          @click="navigateToNext"
          :disabled="currentIssueIndex >= issues.length - 1"
          class="nav-btn"
          title="下一个问题"
        >
          ↓
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'

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
}

interface Props {
  modelValue: string
  issues: DetectedIssue[]
  placeholder?: string
  maxLength?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'issue-click', issue: DetectedIssue): void
  (e: 'text-change', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '在这里输入您的小红书内容...',
  maxLength: 1000
})

const emit = defineEmits<Emits>()

const textareaRef = ref<HTMLTextAreaElement>()
const localContent = ref(props.modelValue)
const textareaHeight = ref(200)
const currentIssueIndex = ref(-1)
const isFocused = ref(false)

// 同步props和本地状态
watch(() => props.modelValue, (newValue) => {
  localContent.value = newValue
})

watch(localContent, (newValue) => {
  emit('update:modelValue', newValue)
  emit('text-change', newValue)
})

// 生成高亮内容
const highlightedContent = computed(() => {
  if (!localContent.value || props.issues.length === 0) {
    return escapeHtml(localContent.value).replace(/\n/g, '<br>')
  }
  
  let content = localContent.value
  const sortedIssues = [...props.issues].sort((a, b) => b.start_pos - a.start_pos)
  
  // 从后往前替换，避免位置偏移
  for (const issue of sortedIssues) {
    const word = content.substring(issue.start_pos, issue.end_pos)
    const highlightClass = getHighlightClass(issue)
    const tooltip = getTooltipText(issue)
    const highlightHtml = `<span class="${highlightClass}" data-issue-id="${issue.id}" data-tooltip="${tooltip}" onclick="handleIssueClick('${issue.id}')">${escapeHtml(word)}</span>`
    
    content = content.substring(0, issue.start_pos) + 
              highlightHtml + 
              content.substring(issue.end_pos)
  }
  
  return content.replace(/\n/g, '<br>')
})

// 获取高亮样式类
const getHighlightClass = (issue: DetectedIssue): string => {
  const baseClass = 'highlighted-word'
  const typeClass = issue.type === 'prohibited_word' ? 'prohibited' : 'homophone'
  const severityClass = issue.severity
  
  return `${baseClass} ${typeClass} ${severityClass}`
}

// 获取工具提示文本
const getTooltipText = (issue: DetectedIssue): string => {
  const typeText = issue.type === 'prohibited_word' ? '违禁词' : '谐音词'
  const severityText = issue.severity === 'high' ? '高风险' : 
                      issue.severity === 'medium' ? '中风险' : '低风险'
  return `${typeText} - ${severityText}`
}

// HTML转义
const escapeHtml = (text: string): string => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 处理输入
const handleInput = () => {
  updateTextareaHeight()
}

// 处理滚动同步
const handleScroll = () => {
  const textarea = textareaRef.value
  if (textarea) {
    const highlightLayer = document.querySelector('.highlight-layer') as HTMLElement
    if (highlightLayer) {
      highlightLayer.scrollTop = textarea.scrollTop
      highlightLayer.scrollLeft = textarea.scrollLeft
    }
  }
}

// 处理焦点
const handleFocus = () => {
  isFocused.value = true
}

const handleBlur = () => {
  isFocused.value = false
}

// 更新textarea高度
const updateTextareaHeight = async () => {
  await nextTick()
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    const newHeight = Math.max(200, textarea.scrollHeight)
    textarea.style.height = newHeight + 'px'
    textareaHeight.value = newHeight
  }
}

// 导航到上一个问题
const navigateToPrevious = () => {
  if (currentIssueIndex.value > 0) {
    currentIssueIndex.value--
    scrollToIssue(props.issues[currentIssueIndex.value])
  }
}

// 导航到下一个问题
const navigateToNext = () => {
  if (currentIssueIndex.value < props.issues.length - 1) {
    currentIssueIndex.value++
    scrollToIssue(props.issues[currentIssueIndex.value])
  }
}

// 滚动到指定问题
const scrollToIssue = (issue: DetectedIssue) => {
  const textarea = textareaRef.value
  if (textarea) {
    // 计算光标位置
    textarea.focus()
    textarea.setSelectionRange(issue.start_pos, issue.end_pos)
    
    // 滚动到可见区域
    const charHeight = 20 // 大概的字符高度
    const lineNumber = localContent.value.substring(0, issue.start_pos).split('\n').length
    const scrollTop = (lineNumber - 3) * charHeight
    
    textarea.scrollTop = Math.max(0, scrollTop)
    handleScroll()
  }
}

// 全局点击处理函数（需要暴露到window）
;(window as any).handleIssueClick = (issueId: string) => {
  const issue = props.issues.find(i => i.id === issueId)
  if (issue) {
    emit('issue-click', issue)
    // 更新当前问题索引
    currentIssueIndex.value = props.issues.findIndex(i => i.id === issueId)
  }
}

// 组件挂载时更新高度
onMounted(() => {
  updateTextareaHeight()
})

// 监听issues变化，重置导航
watch(() => props.issues, () => {
  currentIssueIndex.value = props.issues.length > 0 ? 0 : -1
})
</script>

<style lang="scss" scoped>
.highlight-editor {
  position: relative;
  
  .editor-container {
    position: relative;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    overflow: hidden;
    transition: border-color 0.2s ease;
    
    &:focus-within {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px var(--primary-10);
    }
  }
  
  .highlight-layer {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 1;
    
    .highlight-content {
      padding: 12px;
      font-family: inherit;
      font-size: 14px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-wrap: break-word;
      color: transparent;
      overflow: hidden;
    }
  }
  
  .text-input {
    position: relative;
    z-index: 2;
    width: 100%;
    min-height: 200px;
    padding: 12px;
    border: none;
    outline: none;
    resize: none;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
    background: transparent;
    color: var(--text-primary);
    
    &::placeholder {
      color: var(--text-secondary);
    }
  }
  
  .char-count {
    position: absolute;
    bottom: 8px;
    right: 12px;
    font-size: 12px;
    color: var(--text-secondary);
    background: var(--bg-primary);
    padding: 2px 6px;
    border-radius: 4px;
    z-index: 3;
  }
  
  .issue-navigator {
    position: absolute;
    top: 8px;
    right: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
    z-index: 3;
    
    .navigator-info {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .issue-count {
        color: var(--text-primary);
        font-weight: 500;
      }
      
      .current-position {
        color: var(--text-secondary);
      }
    }
    
    .navigator-controls {
      display: flex;
      gap: 2px;
      
      .nav-btn {
        width: 20px;
        height: 20px;
        border: none;
        border-radius: 3px;
        background: var(--bg-secondary);
        color: var(--text-primary);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        
        &:hover:not(:disabled) {
          background: var(--primary);
          color: white;
        }
        
        &:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }
      }
    }
  }
}

// 高亮样式 - 重新设计更舒适的视觉效果
:deep(.highlighted-word) {
  position: relative;
  cursor: pointer;
  border-radius: 2px;
  padding: 0 1px;
  transition: all 0.2s ease;
  display: inline-block;
  
  &.prohibited {
    // 违禁词样式 - 使用更柔和的下划线方式
    background: rgba(220, 38, 38, 0.08);
    color: inherit; // 保持原文字颜色
    border-bottom: 2px solid #dc2626;
    border-radius: 0;
    
    // 严重程度用不同的下划线样式区分
    &.high {
      border-bottom: 2px solid #dc2626;
      background: rgba(220, 38, 38, 0.12);
      box-shadow: inset 0 -2px 0 rgba(220, 38, 38, 0.3);
    }
    
    &.medium {
      border-bottom: 2px dotted #f59e0b;
      background: rgba(245, 158, 11, 0.08);
    }
    
    &.low {
      border-bottom: 1px dashed #10b981;
      background: rgba(16, 185, 129, 0.06);
    }
    
    // 悬停时显示小图标
    &::before {
      content: '';
      position: absolute;
      top: -2px;
      right: -2px;
      width: 6px;
      height: 6px;
      background: #dc2626;
      border-radius: 50%;
      opacity: 0;
      transition: opacity 0.2s ease;
    }
  }
  
  &.homophone {
    // 谐音词样式 - 使用更柔和的点线效果
    background: rgba(34, 197, 94, 0.06);
    color: inherit;
    border-bottom: 2px dotted #22c55e;
    border-radius: 0;
    position: relative;
    
    // 添加微妙的渐变效果
    &::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(34, 197, 94, 0.3) 25%, 
        rgba(34, 197, 94, 0.5) 50%, 
        rgba(34, 197, 94, 0.3) 75%, 
        transparent 100%
      );
      opacity: 0.6;
    }
    
    &::before {
      content: '';
      position: absolute;
      top: -2px;
      right: -2px;
      width: 6px;
      height: 6px;
      background: #22c55e;
      border-radius: 50%;
      opacity: 0;
      transition: opacity 0.2s ease;
    }
  }
  
  // 悬停效果更加微妙
  &:hover {
    background: rgba(59, 130, 246, 0.1);
    transform: none; // 移除放大效果
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    
    &::before {
      opacity: 1;
    }
    
    // 添加工具提示效果
    &::after {
      content: attr(data-tooltip);
      position: absolute;
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      white-space: nowrap;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
      z-index: 1000;
    }
    
    &:hover::after {
      opacity: 1;
    }
  }
  
  // 专门为深色主题优化
  [data-theme="dark"] & {
    &.prohibited {
      background: rgba(248, 113, 113, 0.15);
      border-bottom-color: #f87171;
      
      &.high {
        background: rgba(248, 113, 113, 0.2);
        box-shadow: inset 0 -2px 0 rgba(248, 113, 113, 0.4);
      }
    }
    
    &.homophone {
      background: rgba(34, 197, 94, 0.12);
      border-bottom-color: #4ade80;
      
      &::after {
        background: linear-gradient(90deg, 
          transparent 0%, 
          rgba(34, 197, 94, 0.4) 25%, 
          rgba(34, 197, 94, 0.6) 50%, 
          rgba(34, 197, 94, 0.4) 75%, 
          transparent 100%
        );
      }
      
      &::before {
        background: #4ade80;
      }
    }
    
    &:hover {
      background: rgba(147, 197, 253, 0.15);
    }
  }
}
</style>