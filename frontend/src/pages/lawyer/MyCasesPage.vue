<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NEmpty, NSkeleton, NTag, useMessage } from 'naive-ui'
import { listMyLeads } from '@/services/lawyerService'
import type { LeadListItem } from '@/services/lawyerService'
import { CASE_TYPE_MAP, COMPLEXITY_MAP } from '@/constants'

const router = useRouter()
const message = useMessage()

const leads = ref<LeadListItem[]>([])
const loading = ref(true)

onMounted(loadMyLeads)

async function loadMyLeads() {
  loading.value = true
  try {
    const data = await listMyLeads(100)
    leads.value = data.leads
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载失败')
  } finally {
    loading.value = false
  }
}

function formatTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getMonth() + 1}/${date.getDate()} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function openDetail(id: string) {
  router.push(`/lawyer/leads/${id}`)
}
</script>

<template>
  <div class="my-cases fade-in">
    <div class="my-cases-header">
      <div>
        <h2>📁 我的接单</h2>
        <p class="my-cases-sub">我接手的案件与跟进状态</p>
      </div>
      <n-button size="small" quaternary @click="loadMyLeads" :loading="loading">刷新</n-button>
    </div>

    <div v-if="loading" class="my-skeleton">
      <n-skeleton v-for="i in 2" :key="i" height="100px" :sharp="false" style="margin-bottom: 12px" />
    </div>

    <n-empty v-else-if="leads.length === 0" description="还没有接单">
      <template #extra>
        <n-button type="primary" size="small" @click="router.push('/lawyer/dashboard')">
          去系统推荐找案件
        </n-button>
      </template>
    </n-empty>

    <div v-else class="case-list">
      <div v-for="lead in leads" :key="lead.id" class="case-card glass-card" @click="openDetail(lead.id)">
        <div class="case-icon">{{ CASE_TYPE_MAP[lead.case_type]?.icon || '⚖️' }}</div>
        <div class="case-main">
          <div class="case-top">
            <span class="case-name">{{ CASE_TYPE_MAP[lead.case_type]?.name || lead.case_type }}</span>
            <n-tag v-if="lead.region" size="small" :bordered="false" type="info">📍 {{ lead.region }}</n-tag>
            <n-tag
              size="small"
              :bordered="false"
              :type="lead.status === 'claimed' ? 'success' : 'default'"
            >
              {{ lead.status === 'claimed' ? '跟进中' : '已完成' }}
            </n-tag>
            <n-tag
              size="small"
              :bordered="false"
              :type="(COMPLEXITY_MAP[lead.complexity || '']?.color as any) || 'default'"
            >
              {{ COMPLEXITY_MAP[lead.complexity || '']?.label || lead.complexity || '-' }}
            </n-tag>
          </div>
          <div class="case-summary">{{ lead.summary || '暂无摘要' }}</div>
          <div class="case-meta">
            <span class="case-time">接单时间 {{ formatTime(lead.updated_at) }}</span>
            <span v-if="lead.material_request_count > 0" class="case-material">
              📎 已发起 {{ lead.material_request_count }} 次补充材料
            </span>
          </div>
        </div>
        <div class="case-scores">
          <span class="score-chip">风险 {{ lead.risk_score ?? '-' }}</span>
          <span class="score-chip">证据 {{ lead.evidence_score ?? '-' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.my-cases-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}
.my-cases-header h2 {
  margin: 0;
  font-size: 18px;
}
.my-cases-sub {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--text-secondary);
}
.my-skeleton {
  padding: 4px;
}
.case-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.case-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  cursor: pointer;
  transition: all 0.2s;
}
.case-card:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.4);
}
.case-icon {
  font-size: 26px;
  flex-shrink: 0;
}
.case-main {
  flex: 1;
  min-width: 0;
}
.case-top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.case-name {
  font-size: 15px;
  font-weight: 700;
}
.case-summary {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.case-meta {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.case-time {
  font-size: 11px;
  color: var(--text-tertiary);
}
.case-material {
  font-size: 11px;
  color: #f59e0b;
}
.case-scores {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}
.score-chip {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(128, 128, 128, 0.1);
  text-align: center;
}
</style>
