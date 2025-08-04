<template>
  <div class="home-page">
    <!-- 顶部导航 -->
    <TopNavBar />
    
    <!-- 主内容区 -->
    <main class="main-content">
      <div class="content-wrapper">
        
        <!-- 左侧编辑区域 -->
        <section class="editor-section">
          <div class="editor-header">
            <h2 class="section-title">内容编辑器</h2>
            <div class="editor-stats">
              <div class="status-indicator" :class="statusClass">
                <span class="status-dot"></span>
                <span>{{ statusText }}</span>
              </div>
              <div class="editor-actions">
                <button 
                  v-if="contentStore.detectedIssues.length > 0"
                  @click="contentStore.toggleReplacementPanel()"
                  class="replacement-panel-btn"
                  :class="{ active: contentStore.showReplacementPanel }"
                >
                  批量处理 ({{ unresolvedIssuesCount }})
                </button>
              </div>
            </div>
          </div>
          
          <div class="editor-container">
            <!-- 使用新的高亮编辑器 -->
            <HighlightEditor
              v-model="currentContent"
              :issues="contentStore.detectedIssues"
              :max-length="1000"
              @issue-click="handleIssueClick"
              @text-change="handleTextChange"
            />
            
            <!-- 工具栏 -->
            <div class="editor-toolbar">
              <div class="toolbar-left">
                <el-button type="default" :icon="Upload" @click="importContent">
                  导入
                </el-button>
                <el-button type="default" @click="pasteContent">
                  粘贴
                </el-button>
                <EmojiPicker :on-insert="insertEmoji" />
              </div>
              <div class="toolbar-right">
                <el-button 
                  type="primary" 
                  :icon="Search" 
                  :loading="contentStore.isAnalyzing"
                  @click="analyzeContent"
                  :disabled="!currentContent.trim()"
                >
                  检测内容
                </el-button>
                <el-button 
                  type="success" 
                  :icon="Wand2" 
                  :loading="contentStore.isOptimizing"
                  @click="optimizeContent"
                  :disabled="!currentContent.trim()"
                >
                  智能优化
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- 优化结果区域 - 在编辑器区域内 -->
          <section v-if="contentStore.optimizedContent" class="results-section">
            <div class="results-header">
              <h3>优化后内容</h3>
              <div class="results-actions">
                <el-button type="default" :icon="Copy" @click="copyContent">
                  复制
                </el-button>
                <el-button type="default" :icon="Download" @click="exportContent">
                  导出
                </el-button>
              </div>
            </div>
            <div class="results-content">
              <div class="optimized-text">
                {{ contentStore.optimizedContent }}
              </div>
            </div>
          </section>
        </section>

        <!-- 右侧面板 -->
        <aside class="detection-sidebar">
          <div class="sidebar-header">
            <div class="sidebar-title">
              <span class="tab-label">
                <Search :size="16" />
                检测结果
              </span>
            </div>
            <el-button 
              v-if="themeStore.currentTheme === 'light'" 
              type="text" 
              @click="themeStore.toggleTheme()"
              :icon="Moon"
            />
            <el-button 
              v-else 
              type="text" 
              @click="themeStore.toggleTheme()"
              :icon="Sun"
            />
          </div>
          
          <!-- 检测结果内容 -->
          <div class="detection-cards">
            <!-- 违禁词检测卡片 -->
            <DetectionCard
              title="违禁词检测"
              :icon="AlertTriangle"
              :count="contentStore.detectedIssues.length"
              :issues="contentStore.detectedIssues"
              type="warning"
            />

            <!-- 结构分析卡片 -->
            <DetectionCard
              title="结构分析"
              :icon="Target"
              :score="contentStore.contentScore"
              type="info"
            />

            <!-- 优化建议卡片 -->
            <DetectionCard
              title="优化建议"
              :icon="Lightbulb"
              :suggestions="contentStore.suggestions"
              type="success"
            />

            <!-- 表情推荐卡片 -->
            <EmojiSuggestionCard
              :suggestions="contentStore.emojiSuggestions"
            />
          </div>
        </aside>
      </div>
    </main>
    
    <!-- 词汇详情Tooltip -->
    <WordTooltip
      :issue="contentStore.selectedIssue"
      :visible="contentStore.showTooltip"
      :position="contentStore.tooltipPosition"
      @close="contentStore.hideTooltip()"
      @replace-word="handleReplaceWord"
      @ignore-issue="handleIgnoreIssue"
      @edit-manually="handleIssueClick"
    />
    
    <!-- 批量替换面板 -->
    <ReplacementPanel
      :issues="contentStore.detectedIssues"
      :visible="contentStore.showReplacementPanel"
      :resolved-issues="contentStore.resolvedIssues"
      @close="contentStore.showReplacementPanel = false"
      @replace-word="handleReplaceWord"
      @ignore-issue="handleIgnoreIssue"
      @apply-all-homophones="handleApplyAllHomophones"
      @navigate-to-issue="handleNavigateToIssue"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, 
  Upload, 
  Copy, 
  Download, 
  Wand2, 
  AlertTriangle, 
  Target, 
  Lightbulb,
  Moon,
  Sun
} from 'lucide-vue-next'

import TopNavBar from '@/components/common/TopNavBar.vue'
import DetectionCard from '@/components/user/DetectionCard.vue'
import EmojiPicker from '@/components/user/EmojiPicker.vue'
import EmojiSuggestionCard from '@/components/user/EmojiSuggestionCard.vue'
import HighlightEditor from '@/components/user/HighlightEditor.vue'
import WordTooltip from '@/components/user/WordTooltip.vue'
import ReplacementPanel from '@/components/user/ReplacementPanel.vue'
import { useContentStore } from '@/stores/content'
import { useThemeStore } from '@/stores/theme'

const contentStore = useContentStore()
const themeStore = useThemeStore()

// 移除管理面板相关状态

// 初始化用户会话
contentStore.initUserSession()

const currentContent = computed({
  get: () => contentStore.currentContent,
  set: (value: string) => contentStore.setContent(value)
})

const statusClass = computed(() => {
  if (contentStore.isAnalyzing || contentStore.isOptimizing) return 'info'
  if (contentStore.detectedIssues.length > 0) return 'warning'
  if (contentStore.contentScore > 0) return 'success'
  return 'info'
})

const statusText = computed(() => {
  if (contentStore.isAnalyzing) return '分析中...'
  if (contentStore.isOptimizing) return '优化中...'
  if (contentStore.detectedIssues.length > 0) return `发现 ${contentStore.detectedIssues.length} 个问题`
  if (contentStore.contentScore > 0) return `质量评分: ${contentStore.contentScore}`
  return '准备就绪'
})

// 计算未解决的问题数量
const unresolvedIssuesCount = computed(() => {
  return contentStore.detectedIssues.filter(issue => 
    !contentStore.resolvedIssues.has(issue.id)
  ).length
})

const analyzeContent = async () => {
  try {
    await contentStore.analyzeCurrentContent()
    ElMessage.success('内容分析完成')
  } catch (error) {
    console.error('分析失败:', error)
  }
}

const optimizeContent = async () => {
  try {
    await contentStore.optimizeCurrentContent()
    ElMessage.success('内容优化完成')
  } catch (error) {
    console.error('优化失败:', error)
  }
}

const importContent = () => {
  // 创建文件输入元素
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.txt,.md'
  input.onchange = (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        currentContent.value = content
        ElMessage.success('文件导入成功')
      }
      reader.readAsText(file)
    }
  }
  input.click()
}

const pasteContent = async () => {
  try {
    const text = await navigator.clipboard.readText()
    currentContent.value = text
    ElMessage.success('内容粘贴成功')
  } catch {
    ElMessage.warning('无法访问剪贴板，请手动粘贴')
  }
}

const insertEmoji = (emoji: string) => {
  // 在当前光标位置插入表情符号
  const textarea = document.querySelector('.main-editor .el-textarea__inner') as HTMLTextAreaElement
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const value = currentContent.value
    const newValue = value.substring(0, start) + emoji + value.substring(end)
    currentContent.value = newValue
    
    // 恢复光标位置
    setTimeout(() => {
      textarea.focus()
      const newPosition = start + emoji.length
      textarea.setSelectionRange(newPosition, newPosition)
    }, 0)
  } else {
    // 如果无法获取光标位置，就添加到末尾
    currentContent.value += emoji
  }
}

const copyContent = () => {
  contentStore.copyOptimizedContent()
  ElMessage.success('内容已复制到剪贴板')
}

const exportContent = () => {
  if (!contentStore.optimizedContent) return
  
  const blob = new Blob([contentStore.optimizedContent], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `优化内容_${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('内容导出成功')
}

// 高亮交互事件处理
const handleIssueClick = (issue: any) => {
  // 计算点击位置，显示tooltip
  const position = { x: window.innerWidth / 2, y: window.innerHeight / 2 }
  contentStore.showIssueTooltip(issue, position)
}

const handleTextChange = (value: string) => {
  // 文本变化时重置已解决的问题
  if (value !== contentStore.currentContent) {
    contentStore.resetResolvedIssues()
  }
}

const handleReplaceWord = (issue: any, replacement: string) => {
  contentStore.replaceWord(issue, replacement)
  ElMessage.success(`已替换 "${issue.word}" 为 "${replacement}"`)
}

const handleIgnoreIssue = (issueId: string) => {
  contentStore.ignoreIssue(issueId)
  ElMessage.info('已忽略该问题')
}

const handleNavigateToIssue = (issue: any) => {
  contentStore.selectIssue(issue)
}

const handleApplyAllHomophones = () => {
  const count = contentStore.detectedIssues.filter(
    issue => issue.type === 'homophone_word' && !contentStore.resolvedIssues.has(issue.id)
  ).length
  
  contentStore.applyAllHomophones()
  ElMessage.success(`已应用 ${count} 个谐音词替换`)
}
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.main-content {
  padding-top: 64px; // 为顶部导航留出空间
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 32px;
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: calc(100vh - 64px);
  
  @media (max-width: 1400px) {
    grid-template-columns: 1fr 360px;
    gap: 24px;
  }
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr 320px;
    gap: 20px;
  }
  
  @media (max-width: 1023px) {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px;
    
    .detection-sidebar {
      order: -1;
    }
  }
}

.editor-section {
  .editor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    
    .section-title {
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .editor-stats {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .editor-actions {
        display: flex;
        gap: 8px;
        
        .replacement-panel-btn {
          padding: 6px 12px;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          background: var(--bg-secondary);
          color: var(--text-primary);
          font-size: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover {
            border-color: var(--primary);
            background: var(--primary-10);
            color: var(--primary);
          }
          
          &.active {
            border-color: var(--primary);
            background: var(--primary);
            color: white;
          }
        }
      }
    }
  }
  
  .editor-container {
    .main-editor {
      margin-bottom: 20px;
      padding: 24px;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      transition: all 0.2s ease;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      
      &:hover {
        border-color: var(--gray-400);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      &:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px var(--primary-10);
      }
      
      :deep(.el-textarea__inner) {
        background: transparent;
        border: none;
        padding: 0;
        color: var(--text-primary);
        font-size: 15px;
        line-height: 1.6;
        resize: vertical;
        min-height: 200px;
        
        &:focus {
          outline: none;
          box-shadow: none;
        }
        
        &::placeholder {
          color: var(--text-muted);
          font-style: italic;
        }
      }
      
      :deep(.el-textarea) {
        .el-textarea__inner {
          box-shadow: none;
        }
      }
    }
    
    .editor-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      margin-top: 8px;
      
      .toolbar-left,
      .toolbar-right {
        display: flex;
        gap: 12px;
        align-items: center;
      }
      
      .toolbar-left {
        &::after {
          content: '';
          width: 1px;
          height: 24px;
          background: var(--border-color);
          margin-left: 8px;
        }
      }
      
      // 自定义按钮样式，适配深色主题
      :deep(.el-button) {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        color: var(--text-secondary);
        border-radius: 8px;
        font-weight: 500;
        padding: 10px 16px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
      
      :deep(.el-button:hover) {
        background: var(--hover-bg);
        border-color: var(--gray-400);
        color: var(--text-primary);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
      }
      
      :deep(.el-button:active) {
        transform: translateY(0);
      }
      
      :deep(.el-button.is-disabled) {
        background: var(--hover-bg);
        border-color: var(--border-color);
        color: var(--text-muted);
        opacity: 0.6;
        cursor: not-allowed;
      }
      
      :deep(.el-button.is-disabled:hover) {
        transform: none;
        box-shadow: none;
        background: var(--hover-bg);
        border-color: var(--border-color);
        color: var(--text-muted);
      }
      
      :deep(.el-button--primary) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
      }
      
      :deep(.el-button--primary:hover) {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transform: translateY(-1px);
      }
      
      :deep(.el-button--primary.is-disabled) {
        background: var(--gray-400) !important;
        color: var(--gray-100) !important;
        opacity: 0.6;
      }
      
      :deep(.el-button--primary.is-disabled:hover) {
        background: var(--gray-400) !important;
        color: var(--gray-100) !important;
        transform: none;
        box-shadow: none;
      }
      
      :deep(.el-button--success) {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border: none;
        color: white;
      }
      
      :deep(.el-button--success:hover) {
        background: linear-gradient(135deg, #0d9f73 0%, #047857 100%);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        transform: translateY(-1px);
      }
      
      :deep(.el-button--success.is-disabled) {
        background: var(--gray-400) !important;
        color: var(--gray-100) !important;
        opacity: 0.6;
      }
      
      :deep(.el-button--success.is-disabled:hover) {
        background: var(--gray-400) !important;
        color: var(--gray-100) !important;
        transform: none;
        box-shadow: none;
      }
      
      :deep(.el-button--default) {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        color: var(--text-secondary);
      }
      
      :deep(.el-button--default:hover) {
        background: var(--hover-bg);
        border-color: var(--primary);
        color: var(--primary);
        transform: translateY(-1px);
      }
      
      :deep(.el-button .el-icon) {
        margin-right: 6px;
      }
      
      @media (max-width: 767px) {
        flex-direction: column;
        gap: 16px;
        padding: 16px;
        
        .toolbar-left,
        .toolbar-right {
          width: 100%;
          justify-content: center;
          gap: 8px;
        }
        
        .toolbar-left {
          &::after {
            display: none;
          }
        }
        
        :deep(.el-button) {
          flex: 1;
          min-width: 0;
          padding: 12px 8px;
          font-size: 14px;
        }
      }
    }
  }
}

.detection-sidebar {
  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    
    .sidebar-tabs {
      flex: 1;
      
      :deep(.el-tabs__header) {
        margin: 0;
        border-bottom: 1px solid var(--el-border-color-light);
      }
      
      :deep(.el-tabs__nav-wrap) {
        padding: 0;
      }
      
      :deep(.el-tabs__item) {
        padding: 8px 16px;
        font-size: 14px;
        
        .tab-label {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
  
  .detection-cards,
  .management-panel {
    display: flex;
    flex-direction: column;
    gap: 20px;
    height: calc(100vh - 200px);
    overflow-y: auto;
    padding-right: 8px;
    
    // 自定义滚动条样式
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-track {
      background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
      background: var(--gray-400);
      border-radius: 3px;
      opacity: 0.6;
      
      &:hover {
        background: var(--gray-500);
        opacity: 0.8;
      }
    }
  }
}

  // 编辑器区域内的优化结果
  .results-section {
    margin-top: 20px;
    
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0;
      padding: 16px 20px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px 12px 0 0;
      
      h3 {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
        
        &::before {
          content: '✨';
          font-size: 16px;
        }
      }
      
      .results-actions {
        display: flex;
        gap: 8px;
        
        :deep(.el-button) {
          padding: 8px 12px;
          font-size: 13px;
          background: var(--bg-primary);
          border: 1px solid var(--border-color);
          color: var(--text-secondary);
          
          &:hover {
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-1px);
          }
        }
      }
    }
    
    .results-content {
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-top: none;
      border-radius: 0 0 12px 12px;
      padding: 24px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      
      .optimized-text {
        font-size: 15px;
        line-height: 1.7;
        color: var(--text-primary);
        white-space: pre-wrap;
        word-wrap: break-word;
      }
    }
  }

</style>