<template>
  <div class="history-page">
    <TopNavBar />
    
    <main class="main-content">
      <div class="content-wrapper">
        <div class="page-header">
          <h1>历史记录</h1>
          <p>查看您的内容优化历史</p>
        </div>
        
        <div class="history-list">
          <div v-if="contentStore.history.length === 0" class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>暂无历史记录</h3>
            <p>开始使用内容优化功能后，历史记录将显示在这里。</p>
            <router-link to="/" class="btn btn-primary">
              开始优化内容
            </router-link>
          </div>
          
          <div v-else class="history-items">
            <div 
              v-for="item in contentStore.history" 
              :key="item.id"
              class="history-item"
            >
              <div class="item-header">
                <div class="item-time">
                  {{ formatDate(item.created_at) }}
                </div>
                <div class="item-scores">
                  <span v-if="item.content_score_before" class="score before">
                    优化前: {{ item.content_score_before }}分
                  </span>
                  <span v-if="item.content_score_after" class="score after">
                    优化后: {{ item.content_score_after }}分
                  </span>
                </div>
              </div>
              
              <div class="item-content">
                <div class="original-content">
                  <h4>原始内容</h4>
                  <p>{{ truncateText(item.original_content, 100) }}</p>
                </div>
                
                <div v-if="item.optimized_content" class="optimized-content">
                  <h4>优化后内容</h4>
                  <p>{{ truncateText(item.optimized_content, 100) }}</p>
                </div>
              </div>
              
              <div class="item-actions">
                <el-button type="text" @click="viewDetail(item)">
                  查看详情
                </el-button>
                <el-button type="text" @click="copyContent(item.optimized_content || item.original_content)">
                  复制内容
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import TopNavBar from '@/components/common/TopNavBar.vue'
import { useContentStore } from '@/stores/content'

const contentStore = useContentStore()

onMounted(async () => {
  await contentStore.loadHistory()
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const viewDetail = (item: any) => {
  // TODO: 实现详情查看功能
  ElMessage.info('详情查看功能正在开发中')
}

const copyContent = (content: string) => {
  navigator.clipboard.writeText(content)
  ElMessage.success('内容已复制到剪贴板')
}
</script>

<style lang="scss" scoped>
.history-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.main-content {
  padding-top: 64px;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 32px;
  
  h1 {
    font-size: 28px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
  }
  
  p {
    color: var(--text-secondary);
    font-size: 16px;
  }
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  h3 {
    font-size: 20px;
    color: var(--text-primary);
    margin-bottom: 8px;
  }
  
  p {
    color: var(--text-secondary);
    margin-bottom: 24px;
  }
}

.history-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  transition: border-color 0.2s ease;
  
  &:hover {
    border-color: var(--primary-30);
  }
  
  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .item-time {
      font-size: 14px;
      color: var(--text-secondary);
    }
    
    .item-scores {
      display: flex;
      gap: 16px;
      
      .score {
        font-size: 12px;
        padding: 4px 8px;
        border-radius: 12px;
        
        &.before {
          background: var(--gray-100);
          color: var(--gray-700);
        }
        
        &.after {
          background: var(--success-10);
          color: var(--success);
        }
      }
    }
  }
  
  .item-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 16px;
    
    @media (max-width: 767px) {
      grid-template-columns: 1fr;
    }
    
    .original-content,
    .optimized-content {
      h4 {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
      }
      
      p {
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.5;
      }
    }
    
    .optimized-content {
      border-left: 3px solid var(--success);
      padding-left: 16px;
    }
  }
  
  .item-actions {
    display: flex;
    gap: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
  }
}
</style>