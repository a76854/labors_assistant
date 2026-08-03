<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NEmpty, NSelect, NSkeleton, NTag, useMessage } from 'naive-ui'
import { getAdminUsers } from '@/services/adminService'
import type { AdminUser } from '@/services/adminService'

const message = useMessage()

const users = ref<AdminUser[]>([])
const total = ref(0)
const loading = ref(true)
const roleFilter = ref<string | null>(null)

const roleOptions = [
  { label: '全部角色', value: '' },
  { label: '劳动者', value: 'user' },
  { label: '律师', value: 'lawyer' },
  { label: '管理员', value: 'admin' },
]

const roleTag: Record<string, { label: string; type: 'info' | 'success' | 'error' | 'default' }> = {
  user: { label: '劳动者', type: 'info' },
  lawyer: { label: '律师', type: 'success' },
  admin: { label: '管理员', type: 'error' },
}

onMounted(loadUsers)

async function loadUsers() {
  loading.value = true
  try {
    const data = await getAdminUsers(roleFilter.value || undefined, 200, 0)
    users.value = data.users
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
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}
</script>

<template>
  <div class="users-page fade-in">
    <div class="users-header">
      <div>
        <h2>👥 用户管理</h2>
        <p class="users-sub">全平台用户（共 {{ total }} 人）</p>
      </div>
      <n-select
        v-model:value="roleFilter"
        :options="roleOptions"
        size="small"
        style="width: 140px"
        @update:value="loadUsers"
      />
    </div>

    <div v-if="loading" class="users-skeleton">
      <n-skeleton v-for="i in 5" :key="i" height="52px" :sharp="false" style="margin-bottom: 8px" />
    </div>

    <n-empty v-else-if="users.length === 0" description="暂无用户" />

    <div v-else class="user-table glass-card">
      <div class="table-row table-head">
        <span>用户名</span>
        <span>角色</span>
        <span>姓名</span>
        <span>地区</span>
        <span>擅长领域</span>
        <span>会话</span>
        <span>线索</span>
        <span>注册时间</span>
      </div>
      <div v-for="user in users" :key="user.id" class="table-row">
        <span class="user-username">{{ user.username }}</span>
        <span>
          <n-tag size="small" :bordered="false" :type="(roleTag[user.role]?.type as any) || 'default'">
            {{ roleTag[user.role]?.label || user.role }}
          </n-tag>
        </span>
        <span>{{ user.name || '-' }}</span>
        <span>{{ user.region || '-' }}</span>
        <span class="specialty-cell">
          <template v-if="user.specialty && user.specialty.length">
            <n-tag v-for="s in user.specialty" :key="s" size="tiny" :bordered="false" type="info">
              {{ s }}
            </n-tag>
          </template>
          <span v-else>-</span>
        </span>
        <span>{{ user.session_count }}</span>
        <span>{{ user.lead_count }}</span>
        <span class="user-time">{{ formatTime(user.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.users-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}
.users-header h2 {
  margin: 0;
  font-size: 18px;
}
.users-sub {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--text-secondary);
}
.users-skeleton {
  padding: 4px;
}
.user-table {
  overflow-x: auto;
}
.table-row {
  display: grid;
  grid-template-columns: 130px 80px 110px 80px 1.4fr 60px 60px 110px;
  gap: 10px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  min-width: 820px;
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
.user-username {
  font-weight: 600;
}
.specialty-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.user-time {
  color: var(--text-tertiary);
  font-size: 12px;
}
</style>
