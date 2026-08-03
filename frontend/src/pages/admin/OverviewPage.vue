<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NSpin, useMessage } from 'naive-ui'
import { getAdminStats } from '@/services/adminService'
import type { AdminStats } from '@/services/adminService'

const router = useRouter()
const message = useMessage()

const stats = ref<AdminStats | null>(null)
const loading = ref(true)

onMounted(loadStats)

async function loadStats() {
  loading.value = true
  try {
    stats.value = await getAdminStats()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载失败')
  } finally {
    loading.value = false
  }
}

const cards = () => {
  if (!stats.value) return []
  const s = stats.value
  return [
    { label: '用户总数', value: s.total_users, sub: `${s.total_workers} 劳动者 / ${s.total_lawyers} 律师`, icon: '👥', to: '/admin/users' },
    { label: '咨询会话', value: s.total_sessions, sub: '全部会话', icon: '💬', to: '/admin/sessions' },
    { label: '案件线索', value: s.total_leads, sub: `${s.open_leads} 待接 / ${s.claimed_leads} 跟进中 / ${s.completed_leads} 已完成`, icon: '📥', to: '/admin/leads' },
    { label: '生成文书', value: s.generated_documents, sub: `共生成 ${s.total_documents} 份记录`, icon: '📄', to: '/' },
  ]
}
</script>

<template>
  <div class="overview-page fade-in">
    <n-spin :show="loading">
      <div class="stat-grid">
        <div
          v-for="card in cards()"
          :key="card.label"
          class="stat-card glass-card"
          @click="router.push(card.to)"
        >
          <div class="stat-icon">{{ card.icon }}</div>
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-sub">{{ card.sub }}</div>
        </div>
      </div>
    </n-spin>
  </div>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}
.stat-card {
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.4);
}
.stat-icon {
  font-size: 26px;
}
.stat-value {
  font-size: 30px;
  font-weight: 800;
  margin: 6px 0 2px;
}
.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}
.stat-sub {
  font-size: 11.5px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

</style>
