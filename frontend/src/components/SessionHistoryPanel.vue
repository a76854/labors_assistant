<script setup lang="ts">
import { NButton, NEmpty, NPopconfirm, NSkeleton, NTag } from 'naive-ui'
import { inject, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import type { SessionListItem } from '@/services/chatService'
import CaseTypeIcon from '@/components/CaseTypeIcon.vue'
import { CASE_TYPE_MAP, formatRegion } from '@/constants'
import { useHistoryStore } from '@/stores/history'

const props = defineProps<{
  sessions?: SessionListItem[]
  loading?: boolean
  activeId?: string | null
  showNewEntry?: boolean
}>()

const router = useRouter()
const historyStore = inject('historyStore', null) as ReturnType<typeof useHistoryStore> | null
const store = historyStore ?? useHistoryStore()
const { sessions: storeSessions, loading: storeLoading, activeId: storeActiveId } = storeToRefs(store)

const sessions = ref<SessionListItem[]>(props.sessions ?? [])
const loading = ref(props.loading ?? false)
const activeId = ref<string | null>(props.activeId ?? null)

if (!props.sessions) {
  watch(
    storeSessions,
    (val) => {
      sessions.value = val
    },
    { immediate: true },
  )
}
if (props.loading === undefined) {
  watch(
    storeLoading,
    (val) => {
      loading.value = val
    },
    { immediate: true },
  )
}
if (props.activeId === undefined) {
  watch(
    storeActiveId,
    (val) => {
      activeId.value = val
    },
    { immediate: true },
  )
}

function handleSelect(id: string) {
  store.setActive(id)
  router.push(`/chat/${id}`)
}

function handleDelete(id: string) {
  store.remove(id)
}

function handleNew() {
  router.push('/')
}
</script>

<template>
  <div class="session-panel">
    <div v-if="props.showNewEntry !== false" class="new-entry" @click="handleNew">
      <span class="new-icon">＋</span>
      <span>开始新的案件咨询</span>
    </div>

    <div v-if="loading" class="skeleton-list">
      <n-skeleton v-for="i in 4" :key="i" height="48px" :sharp="false" style="margin-bottom: 8px" />
    </div>

    <n-empty v-else-if="sessions.length === 0" size="small" description="暂无历史会话" />

    <div v-else class="session-list">
      <div
        v-for="session in sessions"
        :key="session.id"
        class="session-item"
        :class="{ active: session.id === activeId }"
        @click="handleSelect(session.id)"
      >
        <div class="session-item-top">
          <CaseTypeIcon :type="session.case_type" :size="13" />
          <span class="session-title">{{ CASE_TYPE_MAP[session.case_type]?.name || session.case_type }}</span>
          <n-tag
            v-if="session.region"
            size="tiny"
            :bordered="false"
            type="info"
            class="session-region-tag"
          >
            {{ formatRegion(session.region) }}
          </n-tag>
        </div>
        <div v-if="session.last_message_preview" class="session-preview">
          {{ session.last_message_preview }}
        </div>
        <div class="session-item-bottom">
          <span class="session-time">{{ formatTime(session.updated_at) }}</span>
          <n-popconfirm @positive-click="handleDelete(session.id)">
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
  gap: 6px;
  padding: 0 4px;
}
.new-entry {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 10px;
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 12.5px;
  transition: all var(--transition-fast);
}
.new-entry:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-soft);
}
.new-icon {
  font-size: 14px;
  line-height: 1;
}
.session-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.session-item {
  padding: 8px 10px;
  border-radius: var(--radius-md);
  cursor: pointer;
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}
.session-item:hover {
  background: var(--bg-subtle);
}
.session-item.active {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
}
.session-item-top {
  display: flex;
  align-items: center;
  gap: 6px;
}
.session-title {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-primary);
}
.session-region-tag {
  margin-left: auto;
}
.session-preview {
  margin-top: 2px;
  font-size: 11.5px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}
.session-item-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}
.session-time {
  font-size: 10.5px;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}
</style>
