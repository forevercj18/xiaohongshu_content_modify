<template>
  <div class="usage-chart">
    <div v-if="!chartData.length" class="chart-empty">
      <span>暂无数据</span>
    </div>
    
    <div v-else class="chart-container">
      <!-- 简化版图表，使用CSS绘制 -->
      <div class="chart-bars">
        <div
          v-for="(item, index) in chartData"
          :key="index"
          class="chart-bar"
        >
          <div class="bar-container">
            <div
              class="bar detection"
              :style="{ height: getBarHeight(item.detections, maxDetections) + '%' }"
              :title="`检测: ${item.detections}`"
            ></div>
            <div
              class="bar optimization"
              :style="{ height: getBarHeight(item.optimizations, maxOptimizations) + '%' }"
              :title="`优化: ${item.optimizations}`"
            ></div>
          </div>
          <div class="bar-label">
            {{ formatDate(item.date) }}
          </div>
        </div>
      </div>
      
      <div class="chart-legend">
        <div class="legend-item">
          <div class="legend-color detection"></div>
          <span>检测次数</span>
        </div>
        <div class="legend-item">
          <div class="legend-color optimization"></div>
          <span>优化次数</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface UsageData {
  date: string
  detections: number
  optimizations: number
  avg_processing_time: number
}

interface Props {
  data: UsageData[]
}

const props = defineProps<Props>()

const chartData = computed(() => props.data || [])

const maxDetections = computed(() => {
  return Math.max(...chartData.value.map(item => item.detections), 1)
})

const maxOptimizations = computed(() => {
  return Math.max(...chartData.value.map(item => item.optimizations), 1)
})

const getBarHeight = (value: number, max: number) => {
  return Math.max((value / max) * 100, 2) // 最小2%高度
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<style lang="scss" scoped>
.usage-chart {
  height: 300px;
  
  .chart-empty {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    font-size: 14px;
  }
  
  .chart-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .chart-bars {
    flex: 1;
    display: flex;
    align-items: flex-end;
    gap: 12px;
    padding: 20px 0;
    
    .chart-bar {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      
      .bar-container {
        height: 200px;
        display: flex;
        align-items: flex-end;
        gap: 4px;
        width: 100%;
        justify-content: center;
        
        .bar {
          width: 16px;
          border-radius: 4px 4px 0 0;
          transition: all 0.3s ease;
          cursor: pointer;
          
          &.detection {
            background: var(--primary);
            
            &:hover {
              background: var(--primary-hover);
            }
          }
          
          &.optimization {
            background: var(--success);
            
            &:hover {
              background: var(--success);
              filter: brightness(0.9);
            }
          }
        }
      }
      
      .bar-label {
        font-size: 11px;
        color: var(--text-secondary);
        text-align: center;
      }
    }
  }
  
  .chart-legend {
    display: flex;
    justify-content: center;
    gap: 24px;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
    
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: var(--text-secondary);
      
      .legend-color {
        width: 12px;
        height: 12px;
        border-radius: 2px;
        
        &.detection {
          background: var(--primary);
        }
        
        &.optimization {
          background: var(--success);
        }
      }
    }
  }
}
</style>