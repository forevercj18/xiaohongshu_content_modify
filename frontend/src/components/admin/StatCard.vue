<template>
  <div class="stat-card" :class="color">
    <div class="stat-content">
      <div class="stat-info">
        <h3 class="stat-title">{{ title }}</h3>
        <div class="stat-value">{{ formattedValue }}</div>
      </div>
      <div class="stat-icon" :class="color">
        <component :is="iconComponent" :size="24" />
      </div>
    </div>
    
    <div v-if="trend" class="stat-trend" :class="trend.direction">
      <component :is="trend.direction === 'up' ? 'TrendingUp' : 'TrendingDown'" :size="16" />
      <span>{{ trend.value }}% vs 上周</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Search, 
  Wand2, 
  AlertTriangle, 
  Volume2,
  TrendingUp,
  TrendingDown 
} from 'lucide-vue-next'

interface Props {
  title: string
  value: number | string
  icon: string
  color: 'primary' | 'success' | 'warning' | 'info'
  trend?: {
    direction: 'up' | 'down'
    value: number
  }
}

const props = defineProps<Props>()

const iconComponents = {
  Search,
  Wand2,
  AlertTriangle,
  Volume2
}

const iconComponent = computed(() => {
  return iconComponents[props.icon as keyof typeof iconComponents] || Search
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    if (props.value >= 1000000) {
      return (props.value / 1000000).toFixed(1) + 'M'
    }
    if (props.value >= 1000) {
      return (props.value / 1000).toFixed(1) + 'K'
    }
    return props.value.toString()
  }
  return props.value
})
</script>

<style lang="scss" scoped>
.stat-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
  
  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
    
    .stat-info {
      flex: 1;
      
      .stat-title {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-secondary);
        margin: 0 0 8px 0;
      }
      
      .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
      }
    }
    
    .stat-icon {
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
  }
  
  .stat-trend {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 500;
    
    &.up {
      color: var(--success);
    }
    
    &.down {
      color: var(--danger);
    }
  }
}
</style>