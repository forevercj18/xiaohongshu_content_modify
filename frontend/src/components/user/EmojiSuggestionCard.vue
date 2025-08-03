<template>
  <div class="emoji-suggestion-card">
    <div class="card-header">
      <div class="card-icon">
        <component :is="Smile" :size="18" />
      </div>
      <div class="card-info">
        <h4>🍠 小红薯表情建议</h4>
        <span v-if="suggestions.length > 0" class="ai-tag">
          {{ suggestions.length }} 个推荐
        </span>
        <span v-else class="card-status">
          暂无建议
        </span>
      </div>
    </div>
    
    <div class="card-content">
      <div v-if="suggestions.length > 0" class="emoji-list">
        <div 
          v-for="(suggestion, index) in suggestions.slice(0, 3)" 
          :key="index"
          class="emoji-item"
          @click="copyEmojiTip(suggestion)"
        >
          <div class="emoji-info">
            <div class="emoji-name">{{ suggestion.描述 }}</div>
            <div class="emoji-desc">{{ suggestion.建议 }}</div>
            <div class="emoji-reason">{{ suggestion.推荐理由 }}</div>
          </div>
          <div class="emoji-action">
            <el-button type="text" size="small" @click.stop="showEmojiTip(suggestion)">
              查看详情
            </el-button>
          </div>
        </div>
        
        <div v-if="suggestions.length > 3" class="more-suggestions">
          还有 {{ suggestions.length - 3 }} 个建议...
        </div>
        
        <div class="usage-tips">
          <div class="tip-title">💡 使用提示</div>
          <div class="tip-content">
            在小红书发布时选择对应的小红薯表情，让内容更生动有趣！
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">🍠</div>
        <div class="empty-text">
          使用智能优化功能后<br/>将为您推荐合适的小红薯表情
        </div>
      </div>
    </div>
    
    <!-- 表情详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="🍠 表情使用建议"
      width="400px"
      center
    >
      <div v-if="selectedEmoji" class="emoji-detail">
        <div class="detail-name">{{ selectedEmoji.描述 }}</div>
        <div class="detail-suggestion">{{ selectedEmoji.建议 }}</div>
        
        <div class="detail-section">
          <h5>适用场景：</h5>
          <div class="scene-tags">
            <el-tag 
              v-for="scene in selectedEmoji.场景" 
              :key="scene"
              size="small"
              type="info"
            >
              {{ scene }}
            </el-tag>
          </div>
        </div>
        
        <div class="detail-section">
          <h5>推荐理由：</h5>
          <p>{{ selectedEmoji.推荐理由 }}</p>
        </div>
        
        <div class="usage-guide">
          <el-alert
            title="在小红书发布时搜索并选择对应的小红薯表情即可"
            type="success"
            :closable="false"
            show-icon
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="dialogVisible = false">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Smile } from 'lucide-vue-next'

interface EmojiSuggestion {
  描述: string
  建议: string
  场景: string[]
  推荐理由: string
}

interface Props {
  suggestions: EmojiSuggestion[]
}

const props = defineProps<Props>()

const dialogVisible = ref(false)
const selectedEmoji = ref<EmojiSuggestion | null>(null)

const showEmojiTip = (suggestion: EmojiSuggestion) => {
  selectedEmoji.value = suggestion
  dialogVisible.value = true
}

const copyEmojiTip = (suggestion: EmojiSuggestion) => {
  const tipText = `${suggestion.描述} - ${suggestion.建议}`
  navigator.clipboard.writeText(tipText).then(() => {
    ElMessage.success('建议已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style lang="scss" scoped>
.emoji-suggestion-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--primary-30);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #ff6b9d 0%, #ffa726 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-info {
  flex: 1;
  
  h4 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
}

.ai-tag {
  background: linear-gradient(135deg, #ff6b9d 0%, #ffa726 100%);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.card-status {
  color: var(--text-muted);
  font-size: 12px;
}

.card-content {
  .emoji-list {
    .emoji-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px;
      background: var(--bg-secondary);
      border-radius: 8px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover {
        background: var(--hover-bg);
        transform: translateY(-1px);
      }
      
      .emoji-info {
        flex: 1;
        
        .emoji-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 4px;
        }
        
        .emoji-desc {
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 2px;
        }
        
        .emoji-reason {
          font-size: 11px;
          color: var(--text-muted);
        }
      }
      
      .emoji-action {
        .el-button {
          color: var(--primary);
          
          &:hover {
            color: var(--primary-hover);
          }
        }
      }
    }
    
    .more-suggestions {
      text-align: center;
      color: var(--text-muted);
      font-size: 12px;
      padding: 8px 0;
    }
    
    .usage-tips {
      margin-top: 16px;
      padding: 12px;
      background: var(--success-10);
      border-radius: 8px;
      border-left: 3px solid var(--success);
      
      .tip-title {
        font-size: 12px;
        font-weight: 500;
        color: var(--success);
        margin-bottom: 4px;
      }
      
      .tip-content {
        font-size: 11px;
        color: var(--text-secondary);
        line-height: 1.4;
      }
    }
  }
  
  .empty-state {
    text-align: center;
    padding: 24px 0;
    
    .empty-icon {
      font-size: 32px;
      margin-bottom: 8px;
    }
    
    .empty-text {
      color: var(--text-muted);
      font-size: 12px;
      line-height: 1.4;
    }
  }
}

.emoji-detail {
  .detail-name {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
    text-align: center;
  }
  
  .detail-suggestion {
    color: var(--text-secondary);
    text-align: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
  }
  
  .detail-section {
    margin-bottom: 16px;
    
    h5 {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 8px;
    }
    
    p {
      color: var(--text-secondary);
      font-size: 14px;
      margin: 0;
    }
    
    .scene-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
  }
  
  .usage-guide {
    margin-top: 20px;
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .emoji-suggestion-card {
    padding: 16px;
  }
  
  .card-header {
    margin-bottom: 12px;
  }
  
  .emoji-item {
    padding: 10px !important;
    
    .emoji-info {
      .emoji-name {
        font-size: 13px;
      }
      
      .emoji-desc {
        font-size: 11px;
      }
    }
  }
}
</style>