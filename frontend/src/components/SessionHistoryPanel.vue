<script setup lang="ts">
import { NButton, NEmpty, NPopconfirm, NSkeleton, NTag } from 'naive-ui'
import type { SessionListItem } from '@/services/chatService'
import { CASE_TYPE_MAP } from '@/constants'

const props = defineProps<{
  sessions: SessionListItem[]
  loading?: boolean
  activeId?: string | null
  showNewEntry?: boolean
}>()

const emit = defineEmits<{
  select: [id: string]
  delete: [id: string]
  newSession: []
}>()
</script>

<template>
  <div class="session-panel">
    <div v-if="props.showNewEntry" class="new-entry" @click="emit('newSession')">
      <span class="new-icon">＋</span>
      <span>开始新的案件咨询</span>
    </div>

    <div v-if="props.loading" class="skeleton-list">
      <n-skeleton v-for="i in 4" :key="i" height="52px" :sharp="false" style="margin-bottom: 10px" />
    </div>

    <n-empty v-else-if="props.sessions.length === 0" size="small" description="暂无历史会话">
      <template #extra>
        <span class="empty-hint">选择上方案件类型开始咨询</span>
      </template>
    </n-empty>

    <div v-else class="session-list">
      <div
        v-for="session in props.sessions"
        :key="session.id"
        class="session-item"
        :class="{ active: session.id === props.activeId }"
        @click="emit('select', session.id)"
      >
        <div class="session-item-top">
          <span class="session-icon">{{ CASE_TYPE_MAP[session.case_type]?.icon || '⚖️' }}</span>
          <span class="session-title">{{ CASE_TYPE_MAP[session.case_type]?.name || session.case_type }}</span>
          <n-tag
            size="tiny"
            :bordered="false"
            type="info"
            v-if="session.region"
            style="margin-left: auto"
          >
            {{ session.region }}
          </n-tag>
        </div>
        <div v-if="session.last_message_preview" class="session-preview">
          {{ session.last_message_preview }}
        </div>
        <div class="session-item-bottom">
          <span class="session-time">{{ formatTime(session.updated_at) }}</span>
          <n-popconfirm @positive-click="emit('delete', session.id)">
            <template #trigger>
              <n-button text size="tiny" type="error" @click.stop>删除</n-button>
            </template>
            确认删除该会话？
          </n-popconfirm>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
function formatTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()
  const pad = (n: number) => String(n).padStart(2, '0')
  const time = `${pad(date.getHours())}:${pad(date.getMinutes())}`
  if (isToday) return time
  return `${date.getMonth() + 1}/${date.getDate()} ${time}`
}
</script>

<style scoped>
.session-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 8px;
}
.new-entry {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: 1.5px dashed var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 13px;
  transition: all 0.2s;
}
.new-entry:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.new-icon {
  font-size: 16px;
}
.session-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.session-item {
  padding: 10px 12px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  background: rgba(128, 128, 128, 0.05);
  transition: all 0.2s;
}
.session-item:hover {
  border-color: var(--border-color);
}
.session-item.active {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.08);
}
.session-item-top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.session-icon {
  font-size: 15px;
}
.session-title {
  font-size: 13px;
  font-weight: 600;
}
.session-preview {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.session-item-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}
.session-time {
  font-size: 11px;
  color: var(--text-tertiary);
}
.empty-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
