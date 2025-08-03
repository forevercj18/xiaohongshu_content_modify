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
              <span class="char-count">{{ currentContent.length }} / 1000</span>
              <div class="status-indicator" :class="statusClass">
                <span class="status-dot"></span>
                <span>{{ statusText }}</span>
              </div>
            </div>
          </div>
          
          <div class="editor-container">
            <el-input
              v-model="currentContent"
              type="textarea"
              :rows="12"
              placeholder="在这里输入您的小红书内容..."
              class="main-editor"
              :maxlength="1000"
              show-word-limit
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
        </section>

        <!-- 右侧面板 -->
        <aside class="detection-sidebar">
          <div class="sidebar-header">
            <el-tabs v-model="activeSidebarTab" class="sidebar-tabs">
              <el-tab-pane label="检测结果" name="detection">
                <template #label>
                  <span class="tab-label">
                    <Search :size="16" />
                    检测结果
                  </span>
                </template>
              </el-tab-pane>
              <el-tab-pane label="管理面板" name="management">
                <template #label>
                  <span class="tab-label">
                    <Settings :size="16" />
                    管理面板
                  </span>
                </template>
              </el-tab-pane>
            </el-tabs>
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
          
          <!-- 检测结果标签页内容 -->
          <div v-if="activeSidebarTab === 'detection'" class="detection-cards">
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

          <!-- 管理面板标签页内容 -->
          <div v-if="activeSidebarTab === 'management'" class="management-panel">
            <EmojiManagementPanel />
          </div>
        </aside>
      </div>

      <!-- 底部结果区域 -->
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
    </main>
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
  Sun,
  Settings
} from 'lucide-vue-next'

import TopNavBar from '@/components/common/TopNavBar.vue'
import DetectionCard from '@/components/user/DetectionCard.vue'
import EmojiPicker from '@/components/user/EmojiPicker.vue'
import EmojiSuggestionCard from '@/components/user/EmojiSuggestionCard.vue'
import EmojiManagementPanel from '@/components/user/EmojiManagementPanel.vue'
import { useContentStore } from '@/stores/content'
import { useThemeStore } from '@/stores/theme'

const contentStore = useContentStore()
const themeStore = useThemeStore()

// 侧边栏标签页状态
const activeSidebarTab = ref('detection')

// 检查URL参数并设置默认标签页
const urlParams = new URLSearchParams(window.location.search)
if (urlParams.get('tab') === 'management') {
  activeSidebarTab.value = 'management'
}

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
  grid-template-columns: 1fr 320px;
  gap: 24px;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  
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
      
      .char-count {
        font-size: 14px;
        color: var(--text-secondary);
      }
    }
  }
  
  .editor-container {
    .main-editor {
      margin-bottom: 16px;
      
      :deep(.el-textarea__inner) {
        background: var(--bg-primary);
        border-color: var(--border-color);
        color: var(--text-primary);
        
        &:focus {
          border-color: var(--primary);
          box-shadow: 0 0 0 2px var(--primary-10);
        }
      }
    }
    
    .editor-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .toolbar-left,
      .toolbar-right {
        display: flex;
        gap: 12px;
      }
      
      @media (max-width: 767px) {
        flex-direction: column;
        gap: 12px;
        
        .toolbar-left,
        .toolbar-right {
          width: 100%;
          justify-content: center;
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
    gap: 16px;
    height: calc(100vh - 200px);
    overflow-y: auto;
  }
}

.results-section {
  margin-top: 32px;
  padding: 0 24px 24px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
  
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .results-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .results-content {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 20px;
    
    .optimized-text {
      font-size: 16px;
      line-height: 1.6;
      color: var(--text-primary);
      white-space: pre-wrap;
    }
  }
}
</style>