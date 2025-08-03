<template>
  <div class="emoji-picker">
    <!-- 触发按钮 -->
    <el-button 
      type="default" 
      :icon="Smile" 
      @click="showPicker = !showPicker"
      class="emoji-trigger"
    >
      表情
    </el-button>
    
    <!-- 表情选择器弹窗 -->
    <el-popover
      v-model:visible="showPicker"
      placement="top"
      :width="360"
      trigger="manual"
      popper-class="emoji-picker-popover"
    >
      <template #reference>
        <span></span>
      </template>
      
      <div class="emoji-picker-content">
        <!-- 搜索框 -->
        <div class="emoji-search">
          <el-input
            v-model="searchText"
            placeholder="搜索表情..."
            size="small"
            :prefix-icon="Search"
            clearable
          />
        </div>
        
        <!-- 分类标签 -->
        <div class="emoji-categories">
          <el-button
            :type="activeCategory === 'smart' ? 'primary' : 'default'"
            size="small"
            @click="handleCategoryChange('smart')"
            class="category-btn smart-btn"
            :loading="activeCategory === 'smart' && isLoadingRecommendations"
          >
            <Sparkles :size="12" />
            智能推荐
          </el-button>
          <el-button
            v-for="(category, key) in categories"
            :key="key"
            :type="activeCategory === key ? 'primary' : 'default'"
            size="small"
            @click="handleCategoryChange(key)"
            class="category-btn"
          >
            {{ category.name }}
          </el-button>
        </div>
        
        <!-- 表情网格 -->
        <div class="emoji-grid">
          <div
            v-for="emoji in filteredEmojis"
            :key="emoji.emoji + emoji.name"
            class="emoji-item"
            @click="insertEmoji(emoji)"
            :title="`${emoji.name} - ${emoji.keywords.join(', ')}`"
          >
            <span class="emoji-char">{{ emoji.emoji }}</span>
            <span class="emoji-name">{{ emoji.name }}</span>
          </div>
        </div>
        
        <!-- 常用组合 -->
        <div v-if="!searchText && activeCategory === 'all'" class="emoji-combinations">
          <div class="combination-title">✨ 常用组合</div>
          <div class="combination-list">
            <div
              v-for="combo in commonCombinations"
              :key="combo"
              class="combination-item"
              @click="insertText(combo)"
            >
              {{ combo }}
            </div>
          </div>
        </div>
        
        <!-- 最近使用 -->
        <div v-if="recentEmojis.length > 0 && !searchText" class="recent-emojis">
          <div class="recent-title">🕐 最近使用</div>
          <div class="recent-list">
            <div
              v-for="emoji in recentEmojis.slice(0, 12)"
              :key="emoji.emoji + emoji.timestamp"
              class="recent-emoji"
              @click="insertEmoji(emoji)"
              :title="emoji.name"
            >
              {{ emoji.emoji }}
            </div>
          </div>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Smile, Search, Sparkles } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { emojiApi } from '@/api/emoji'
import { useContentStore } from '@/stores/content'

interface EmojiItem {
  emoji: string
  name: string
  keywords: string[]
}

interface Props {
  onInsert?: (text: string) => void
}

const props = defineProps<Props>()

const showPicker = ref(false)
const searchText = ref('')
const activeCategory = ref('all')
const recentEmojis = ref<(EmojiItem & { timestamp: number })[]>([])

// 表情数据
const emojiData = ref<any>({})

// 智能推荐相关
const contentStore = useContentStore()
const smartRecommendations = ref<EmojiItem[]>([])
const isLoadingRecommendations = ref(false)

// 分类定义
const categories = {
  all: { name: '全部', key: 'all' },
  emotion: { name: '情绪', key: '基础情绪' },
  theme: { name: '主题', key: '主题表情' },
  life: { name: '生活', key: '生活日常' },
  decoration: { name: '装饰', key: '装饰符号' }
}

// 常用组合
const commonCombinations = [
  '✨种草推荐✨',
  '🔥热门好物🔥',
  '💄美妆分享💄',
  '🍰治愈美食🍰',
  '👗穿搭灵感👗',
  '🏠居家好物🏠',
  '📚学习记录📚',
  '💪健身打卡💪'
]

// 获取所有表情
const allEmojis = computed(() => {
  const emojis: EmojiItem[] = []
  const data = emojiData.value?.小红书风格表情包?.分类
  
  if (!data) return emojis
  
  Object.values(data).forEach((category: any) => {
    Object.values(category).forEach((subcategory: any) => {
      if (Array.isArray(subcategory)) {
        emojis.push(...subcategory)
      }
    })
  })
  
  return emojis
})

// 过滤后的表情
const filteredEmojis = computed(() => {
  // 智能推荐模式
  if (activeCategory.value === 'smart') {
    if (searchText.value.trim()) {
      const search = searchText.value.toLowerCase()
      return smartRecommendations.value.filter(emoji => 
        emoji.name.toLowerCase().includes(search) ||
        emoji.keywords.some(keyword => keyword.toLowerCase().includes(search))
      )
    }
    return smartRecommendations.value
  }
  
  let emojis = allEmojis.value
  
  // 分类过滤
  if (activeCategory.value !== 'all') {
    const data = emojiData.value?.小红书风格表情包?.分类
    const categoryData = data?.[categories[activeCategory.value as keyof typeof categories].key]
    
    emojis = []
    if (categoryData) {
      Object.values(categoryData).forEach((subcategory: any) => {
        if (Array.isArray(subcategory)) {
          emojis.push(...subcategory)
        }
      })
    }
  }
  
  // 搜索过滤
  if (searchText.value.trim()) {
    const search = searchText.value.toLowerCase()
    emojis = emojis.filter(emoji => 
      emoji.name.toLowerCase().includes(search) ||
      emoji.keywords.some(keyword => keyword.toLowerCase().includes(search))
    )
  }
  
  return emojis
})

// 插入表情
const insertEmoji = (emoji: EmojiItem) => {
  insertText(emoji.emoji)
  addToRecent(emoji)
  ElMessage.success(`已插入：${emoji.name}`)
}

// 插入文本
const insertText = (text: string) => {
  if (props.onInsert) {
    props.onInsert(text)
  }
  showPicker.value = false
}

// 添加到最近使用
const addToRecent = (emoji: EmojiItem) => {
  const recent = { ...emoji, timestamp: Date.now() }
  
  // 移除重复项
  const filtered = recentEmojis.value.filter(item => item.emoji !== emoji.emoji)
  
  // 添加到开头
  recentEmojis.value = [recent, ...filtered].slice(0, 20)
  
  // 保存到本地存储
  localStorage.setItem('xiaohongshu_recent_emojis', JSON.stringify(recentEmojis.value))
}

// 加载表情数据
const loadEmojiData = async () => {
  try {
    // 使用新的表情API
    const response = await fetch('/api/emoji/list?limit=100')
    const data = await response.json()
    
    if (data.emojis) {
      // 转换API数据为组件需要的格式
      const convertedData = {
        小红书风格表情包: {
          分类: {}
        }
      }
      
      // 按分类组织表情数据
      data.emojis.forEach((emoji: any) => {
        const categoryKey = getCategoryDisplayName(emoji.category)
        if (!convertedData.小红书风格表情包.分类[categoryKey]) {
          convertedData.小红书风格表情包.分类[categoryKey] = {
            [emoji.subcategory || '默认']: []
          }
        }
        
        const subcategoryKey = emoji.subcategory || '默认'
        if (!convertedData.小红书风格表情包.分类[categoryKey][subcategoryKey]) {
          convertedData.小红书风格表情包.分类[categoryKey][subcategoryKey] = []
        }
        
        convertedData.小红书风格表情包.分类[categoryKey][subcategoryKey].push({
          emoji: emoji.code,  // 使用表情代码如 [开心R]
          name: emoji.name,
          keywords: emoji.keywords
        })
      })
      
      emojiData.value = convertedData
    }
  } catch (error) {
    console.error('加载表情数据失败:', error)
    ElMessage.error('表情数据加载失败')
  }
}

// 获取分类显示名称的辅助函数
const getCategoryDisplayName = (categoryName: string) => {
  const categoryMap: Record<string, string> = {
    'basic_emotions': '基础情绪',
    'reactions': '反应表情', 
    'actions': '生活日常',
    'social': '装饰符号'
  }
  return categoryMap[categoryName] || categoryName
}

// 加载最近使用的表情
const loadRecentEmojis = () => {
  try {
    const saved = localStorage.getItem('xiaohongshu_recent_emojis')
    if (saved) {
      recentEmojis.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('加载最近表情失败:', error)
  }
}

// 加载智能推荐
const loadSmartRecommendations = async () => {
  if (isLoadingRecommendations.value) return
  
  const content = contentStore.currentContent || contentStore.optimizedContent
  if (!content.trim()) {
    smartRecommendations.value = []
    return
  }
  
  isLoadingRecommendations.value = true
  try {
    const result = await emojiApi.recommendEmojis(content, 12)
    smartRecommendations.value = result.recommendations.map(rec => ({
      emoji: rec.code,
      name: rec.name,
      keywords: rec.keywords
    }))
  } catch (error) {
    console.error('加载智能推荐失败:', error)
    ElMessage.error('加载智能推荐失败')
  } finally {
    isLoadingRecommendations.value = false
  }
}

// 监听分类切换
const handleCategoryChange = (category: string) => {
  activeCategory.value = category
  if (category === 'smart') {
    loadSmartRecommendations()
  }
}

onMounted(() => {
  loadEmojiData()
  loadRecentEmojis()
})
</script>

<style lang="scss" scoped>
.emoji-picker {
  .emoji-trigger {
    border-radius: 6px;
    
    &:hover {
      color: var(--primary);
      border-color: var(--primary-30);
    }
  }
}

:deep(.emoji-picker-popover) {
  padding: 12px !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12) !important;
}

.emoji-picker-content {
  .emoji-search {
    margin-bottom: 12px;
  }
  
  .emoji-categories {
    display: flex;
    gap: 6px;
    margin-bottom: 12px;
    flex-wrap: wrap;
    
    .category-btn {
      height: 28px;
      padding: 0 12px;
      font-size: 12px;
      border-radius: 14px;
      
      &.smart-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        
        &:hover {
          opacity: 0.9;
        }
        
        svg {
          margin-right: 4px;
        }
      }
    }
  }
  
  .emoji-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 4px;
    max-height: 240px;
    overflow-y: auto;
    margin-bottom: 12px;
    
    .emoji-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 8px 4px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover {
        background: var(--hover-bg);
        transform: scale(1.05);
      }
      
      .emoji-char {
        font-size: 18px;
        margin-bottom: 2px;
      }
      
      .emoji-name {
        font-size: 10px;
        color: var(--text-muted);
        text-align: center;
        line-height: 1.2;
      }
    }
  }
  
  .emoji-combinations {
    border-top: 1px solid var(--border-color);
    padding-top: 12px;
    margin-bottom: 12px;
    
    .combination-title {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    
    .combination-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      
      .combination-item {
        padding: 4px 8px;
        background: var(--bg-secondary);
        border-radius: 12px;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover {
          background: var(--primary-10);
          color: var(--primary);
        }
      }
    }
  }
  
  .recent-emojis {
    border-top: 1px solid var(--border-color);
    padding-top: 12px;
    
    .recent-title {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    
    .recent-list {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      
      .recent-emoji {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover {
          background: var(--hover-bg);
          transform: scale(1.1);
        }
      }
    }
  }
}

/* 滚动条样式 */
.emoji-grid::-webkit-scrollbar {
  width: 4px;
}

.emoji-grid::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 2px;
}

.emoji-grid::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 2px;
  
  &:hover {
    background: var(--text-muted);
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  :deep(.emoji-picker-popover) {
    width: 300px !important;
  }
  
  .emoji-grid {
    grid-template-columns: repeat(5, 1fr);
    
    .emoji-item {
      padding: 6px 2px;
      
      .emoji-char {
        font-size: 16px;
      }
      
      .emoji-name {
        font-size: 9px;
      }
    }
  }
}
</style>