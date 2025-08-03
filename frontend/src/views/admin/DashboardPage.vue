<template>
  <div class="dashboard-page">
    <AdminLayout>
      <template #header>
        <div class="dashboard-header">
          <h1>管理后台概览</h1>
          <p>欢迎回来，{{ authStore.user?.username }}</p>
        </div>
      </template>
      
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <StatCard
          title="总检测次数"
          :value="dashboardStats?.total_detections || 0"
          icon="Search"
          color="primary"
        />
        <StatCard
          title="总优化次数"
          :value="dashboardStats?.total_optimizations || 0"
          icon="Wand2"
          color="success"
        />
        <StatCard
          title="违禁词数量"
          :value="dashboardStats?.total_prohibited_words || 0"
          icon="AlertTriangle"
          color="warning"
        />
        <StatCard
          title="谐音词数量"
          :value="dashboardStats?.total_homophone_words || 0"
          icon="Volume2"
          color="info"
        />
      </div>
      
      <!-- 图表和活动 -->
      <div class="dashboard-content">
        <div class="charts-section">
          <div class="chart-card">
            <h3>使用趋势</h3>
            <UsageChart :data="usageStats" />
          </div>
        </div>
        
        <div class="activity-section">
          <div class="activity-card">
            <div class="activity-header">
              <h3>最近活动</h3>
              <div 
                v-if="hasMoreActivities" 
                class="scroll-indicator"
                title="向下滚动查看更多活动"
              >
                <div class="scroll-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
            <div class="activity-list" :class="{ 'has-scroll': hasMoreActivities }">
              <div
                v-for="(activity, index) in dashboardStats?.recent_activity || []"
                :key="index"
                class="activity-item"
              >
                <div class="activity-icon" :class="activity.type">
                  <component 
                    :is="activity.type === 'optimization' ? 'Wand2' : 'Search'" 
                    :size="16" 
                  />
                </div>
                <div class="activity-content">
                  <div class="activity-title">
                    {{ activity.type === 'optimization' ? '内容优化' : '内容检测' }}
                  </div>
                  <div class="activity-desc">
                    {{ activity.content_preview }}
                  </div>
                  <div class="activity-time">
                    {{ formatTime(activity.created_at) }}
                  </div>
                </div>
                <div v-if="activity.score_after" class="activity-score">
                  <span class="score-improvement">
                    +{{ activity.score_after - activity.score_before }}分
                  </span>
                </div>
              </div>
              
              <div v-if="!dashboardStats?.recent_activity?.length" class="empty-activity">
                <span>暂无最近活动</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 快捷操作 -->
      <div class="quick-actions">
        <h3>快捷操作</h3>
        <div class="actions-grid">
          <router-link to="/admin/prohibited-words" class="action-card">
            <div class="action-icon warning">
              <AlertTriangle :size="24" />
            </div>
            <div class="action-content">
              <h4>管理违禁词</h4>
              <p>添加、编辑或删除违禁词</p>
            </div>
          </router-link>
          
          <router-link to="/admin/homophone-words" class="action-card">
            <div class="action-icon info">
              <Volume2 :size="24" />
            </div>
            <div class="action-content">
              <h4>管理谐音词</h4>
              <p>维护谐音词替换库</p>
            </div>
          </router-link>
          
          <a href="/" target="_blank" class="action-card">
            <div class="action-icon primary">
              <ExternalLink :size="24" />
            </div>
            <div class="action-content">
              <h4>前往用户端</h4>
              <p>体验内容优化功能</p>
            </div>
          </a>
          
          <div class="action-card" @click="exportData">
            <div class="action-icon success">
              <Download :size="24" />
            </div>
            <div class="action-content">
              <h4>导出数据</h4>
              <p>导出统计数据和配置</p>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, 
  Wand2, 
  AlertTriangle, 
  Volume2, 
  ExternalLink, 
  Download 
} from 'lucide-vue-next'

import AdminLayout from '@/components/admin/AdminLayout.vue'
import StatCard from '@/components/admin/StatCard.vue'
import UsageChart from '@/components/admin/UsageChart.vue'
import { useAuthStore } from '@/stores/auth'
import { getDashboardStats, getUsageStats } from '@/api/stats'

const authStore = useAuthStore()

const dashboardStats = ref<any>(null)
const usageStats = ref<any[]>([])

// 计算是否有超过4条活动数据
const hasMoreActivities = computed(() => {
  return (dashboardStats.value?.recent_activity?.length || 0) > 4
})

onMounted(async () => {
  await loadDashboardData()
})

const loadDashboardData = async () => {
  try {
    // 加载仪表板统计
    dashboardStats.value = await getDashboardStats()
    
    // 加载使用统计（最近7天）
    usageStats.value = await getUsageStats({ days: 7 })
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  }
}

const formatTime = (timeString: string) => {
  const time = new Date(timeString)
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

const exportData = () => {
  ElMessage.info('数据导出功能正在开发中')
}
</script>

<style lang="scss" scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--bg-secondary);
}

.dashboard-header {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
  align-items: stretch; /* 确保左右两侧高度一致 */
  
  @media (max-width: 1023px) {
    grid-template-columns: 1fr;
  }
}

.chart-card,
.activity-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  min-height: 480px; /* 设置最小高度确保视觉平衡 */
  
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 20px;
  }
}

.charts-section,
.activity-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .chart-card {
    flex: 1;
    
    /* 确保图表组件填充可用空间 */
    :deep(.usage-chart) {
      height: 100%;
      min-height: 300px;
    }
  }
  
  .activity-card {
    flex: 1;
    min-height: 480px;
  }
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h3 {
    margin-bottom: 0;
  }
}

.scroll-indicator {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background: var(--gray-100);
  border-radius: 12px;
  cursor: help;
  
  .scroll-dots {
    display: flex;
    gap: 3px;
    
    span {
      width: 4px;
      height: 4px;
      background: var(--gray-400);
      border-radius: 50%;
      animation: scroll-pulse 1.5s ease-in-out infinite;
      
      &:nth-child(1) {
        animation-delay: 0s;
      }
      
      &:nth-child(2) {
        animation-delay: 0.2s;
      }
      
      &:nth-child(3) {
        animation-delay: 0.4s;
      }
    }
  }
}

@keyframes scroll-pulse {
  0%, 70%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  35% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.activity-list {
  flex: 1; /* 填充剩余空间 */
  max-height: 400px; /* 增加最大高度以适应新的布局 */
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--gray-400) transparent;
  
  /* 自定义滚动条样式 */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--gray-300);
    border-radius: 3px;
    transition: background-color 0.2s ease;
    
    &:hover {
      background: var(--gray-400);
    }
  }
  
  /* 滚动时显示渐变遮罩效果 */
  &.has-scroll::before {
    content: '';
    position: sticky;
    top: 0;
    left: 0;
    right: 0;
    height: 12px;
    background: linear-gradient(to bottom, var(--bg-primary) 0%, var(--bg-primary) 40%, transparent 100%);
    z-index: 2;
    pointer-events: none;
    margin-bottom: -12px;
  }
  
  &.has-scroll::after {
    content: '';
    position: sticky;
    bottom: 0;
    left: 0;
    right: 0;
    height: 12px;
    background: linear-gradient(to top, var(--bg-primary) 0%, var(--bg-primary) 40%, transparent 100%);
    z-index: 2;
    pointer-events: none;
    margin-top: -12px;
  }
  
  /* 滚动阴影效果 */
  &.has-scroll {
    border-radius: 8px;
    box-shadow: inset 0 10px 10px -10px rgba(0, 0, 0, 0.1), 
                inset 0 -10px 10px -10px rgba(0, 0, 0, 0.1);
  }
  
  .activity-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 8px 16px 0; /* 为滚动条留出空间 */
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.2s ease;
    
    &:last-child {
      border-bottom: none;
    }
    
    &:hover {
      background-color: var(--hover-bg);
      border-radius: 8px;
      margin: 0 -8px;
      padding-left: 8px;
    }
    
    .activity-icon {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      
      &.optimization {
        background: var(--success-10);
        color: var(--success);
      }
      
      &.detection {
        background: var(--info-10);
        color: var(--info);
      }
    }
    
    .activity-content {
      flex: 1;
      
      .activity-title {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 4px;
      }
      
      .activity-desc {
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 4px;
      }
      
      .activity-time {
        font-size: 11px;
        color: var(--text-muted);
      }
    }
    
    .activity-score {
      .score-improvement {
        font-size: 12px;
        color: var(--success);
        font-weight: 500;
        background: var(--success-10);
        padding: 2px 8px;
        border-radius: 12px;
      }
    }
  }
  
  .empty-activity {
    text-align: center;
    padding: 40px 0;
    color: var(--text-muted);
    font-size: 14px;
  }
}

.quick-actions {
  h3 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 20px;
  }
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
  cursor: pointer;
  
  &:hover {
    border-color: var(--primary-30);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
  
  .action-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.primary {
      background: var(--primary-10);
      color: var(--primary);
    }
    
    &.success {
      background: var(--success-10);
      color: var(--success);
    }
    
    &.warning {
      background: var(--warning-10);
      color: var(--warning);
    }
    
    &.info {
      background: var(--info-10);
      color: var(--info);
    }
  }
  
  .action-content {
    flex: 1;
    
    h4 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 4px;
    }
    
    p {
      font-size: 14px;
      color: var(--text-secondary);
      margin: 0;
    }
  }
}

/* 移动端响应式优化 */
@media (max-width: 768px) {
  .chart-card,
  .activity-card {
    min-height: 320px; /* 移动端降低最小高度 */
  }
  
  .activity-list {
    max-height: 250px; /* 移动端稍微降低高度 */
    
    .activity-item {
      padding: 12px 4px 12px 0;
      
      &:hover {
        margin: 0 -4px;
        padding-left: 4px;
      }
      
      .activity-icon {
        width: 36px;
        height: 36px;
      }
      
      .activity-content {
        .activity-title {
          font-size: 13px;
        }
        
        .activity-desc {
          font-size: 11px;
        }
      }
    }
  }
  
  .dashboard-content {
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .action-card {
    padding: 16px;
    
    .action-icon {
      width: 40px;
      height: 40px;
    }
    
    .action-content {
      h4 {
        font-size: 15px;
      }
      
      p {
        font-size: 13px;
      }
    }
  }
}

/* 平板端响应式优化 */
@media (min-width: 769px) and (max-width: 1023px) {
  .chart-card,
  .activity-card {
    min-height: 400px; /* 平板端中等高度 */
  }
  
  .activity-list {
    max-height: 320px;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>