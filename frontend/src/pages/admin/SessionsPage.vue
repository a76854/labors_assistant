<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NEmpty, NSkeleton, NTag, useMessage } from 'naive-ui'
import { getAdminSessions } from '@/services/adminService'
import type { AdminSession } from '@/services/adminService'
import { CASE_TYPE_MAP, formatRegion } from '@/constants'

const message = useMessage()

const sessions = ref<AdminSession[]>([])
const total = ref(0)
const loading = ref(true)

onMounted(loadSessions)

async function loadSessions() {
  loading.value = true
  try {
    const data = await getAdminSessions(200, 0)
    sessions.value = data.sessions
    total.value = data.total
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载失败')
  } finally {
    loading.value = false
  }
}

function formatTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
</script>

<template>
  <div class="sessions-page fade-in">
    <div class="sessions-header">
      <div>
        <h2>💬 会话记录</h2>
        <p class="sessions-sub">全平台咨询会话（共 {{ total }} 条）</p>
      </div>
    </div>

    <div v-if="loading" class="sessions-skeleton">
      <n-skeleton v-for="i in 5" :key="i" height="48px" :sharp="false" style="margin-bottom: 8px" />
    </div>

    <n-empty v-else-if="sessions.length === 0" description="暂无会话" />

    <div v-else class="session-table glass-card">
      <div class="table-row table-head">
        <span>案件类型</span>
        <span>地区</span>
        <span>所属用户</span>
        <span>消息数</span>
        <span>状态</span>
        <span>更新时间</span>
      </div>
      <div v-for="session in sessions" :key="session.id" class="table-row">
        <span class="session-case">
          {{ CASE_TYPE_MAP[session.case_type]?.icon || '⚖️' }}
          {{ CASE_TYPE_MAP[session.case_type]?.name || session.case_type }}
        </span>
        <span>{{ formatRegion(session.region) }}</span>
        <span>{{ session.user_username || '-' }}</span>
        <span>{{ session.message_count }}</span>
        <span>
          <n-tag size="small" :bordered="false" :type="session.status === 'active' ? 'info' : 'default'">
            {{ session.status }}
          </n-tag>
        </span>
        <span class="session-time">{{ formatTime(session.updated_at) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sessions-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}
.sessions-header h2 {
  margin: 0;
  font-size: 18px;
}
.sessions-sub {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--text-secondary);
}
.sessions-skeleton {
  padding: 4px;
}
.session-table {
  overflow-x: auto;
}
.table-row {
  display: grid;
  grid-template-columns: 1.6fr 80px 130px 70px 90px 150px;
  gap: 10px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  min-width: 720px;
}
.table-row:last-child {
  border-bottom: none;
}
.table-head {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  background: rgba(128, 128, 128, 0.05);
}
.session-case {
  display: flex;
  align-items: center;
  gap: 6px;
}
.session-time {
  color: var(--text-tertiary);
  font-size: 12px;
}
</style>
