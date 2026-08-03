<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NEmpty, NProgress, NSelect, NSkeleton, NTag, useMessage } from 'naive-ui'
import { listLawyerLeads } from '@/services/lawyerService'
import type { LeadListItem } from '@/services/lawyerService'
import { CASE_TYPE_MAP, COMPLEXITY_MAP, LEAD_STATUS_MAP } from '@/constants'

const router = useRouter()
const message = useMessage()

const leads = ref<LeadListItem[]>([])
const total = ref(0)
const loading = ref(true)
const statusFilter = ref<string | null>(null)

const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '待接单', value: 'open' },
  { label: '已接单', value: 'claimed' },
  { label: '已完成', value: 'completed' },
]

const filteredLeads = computed(() => {
  if (!statusFilter.value) return leads.value
  return leads.value.filter((lead) => lead.status === statusFilter.value)
})

onMounted(loadLeads)

async function loadLeads() {
  loading.value = true
  try {
    const data = await listLawyerLeads(undefined, 100, 0)
    leads.value = data.leads
    total.value = data.total
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载线索失败')
  } finally {
    loading.value = false
  }
}

function riskColor(score: number | null | undefined): 'error' | 'warning' | 'success' {
  if (score === null || score === undefined) return 'success'
  if (score >= 70) return 'error'
  if (score >= 45) return 'warning'
  return 'success'
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
  <div class="leads-page fade-in">
    <div class="leads-header">
      <div class="leads-title">
        <h2>📥 待接单线索</h2>
        <n-tag size="small" :bordered="false" type="info">共 {{ total }} 条</n-tag>
      </div>
      <n-select
        v-model:value="statusFilter"
        :options="statusOptions"
        size="small"
        style="width: 140px"
        placeholder="状态筛选"
      />
    </div>

    <div v-if="loading" class="leads-skeleton">
      <n-skeleton v-for="i in 4" :key="i" height="110px" :sharp="false" style="margin-bottom: 12px" />
    </div>

    <n-empty v-else-if="filteredLeads.length === 0" description="暂无线索">
      <template #extra>
        <span class="empty-tip">劳动者完成咨询分诊后，案件会自动出现在这里</span>
      </template>
    </n-empty>

    <div v-else class="lead-list">
      <div v-for="lead in filteredLeads" :key="lead.id" class="lead-card glass-card" @click="openDetail(lead.id)">
        <div class="lead-main">
          <div class="lead-case">
            <span class="lead-icon">{{ CASE_TYPE_MAP[lead.case_type]?.icon || '⚖️' }}</span>
            <span class="lead-case-name">{{ CASE_TYPE_MAP[lead.case_type]?.name || lead.case_type }}</span>
            <n-tag v-if="lead.region" size="small" :bordered="false" type="info">📍 {{ lead.region }}</n-tag>
            <n-tag
              size="small"
              :bordered="false"
              :type="(LEAD_STATUS_MAP[lead.status]?.type as any) || 'default'"
            >
              {{ LEAD_STATUS_MAP[lead.status]?.label }}
            </n-tag>
          </div>
          <div class="lead-summary">{{ lead.summary || '暂无摘要' }}</div>
          <div class="lead-meta">
            <span class="lead-time">{{ formatTime(lead.created_at) }}</span>
            <span v-if="lead.material_request_count > 0" class="lead-material-badge">
              📎 补充材料 {{ lead.material_request_count }} 次
            </span>
          </div>
        </div>
        <div class="lead-scores">
          <div class="score-col">
            <span class="score-label">风险</span>
            <n-progress
              type="circle"
              :percentage="lead.risk_score ?? 0"
              :status="riskColor(lead.risk_score)"
              :stroke-width="8"
              :rail-color="'rgba(128,128,128,0.15)'"
              :show-text="false"
              style="width: 48px"
            />
            <span class="score-value">{{ lead.risk_score ?? '-' }}</span>
          </div>
          <div class="score-col">
            <span class="score-label">证据</span>
            <n-progress
              type="circle"
              :percentage="lead.evidence_score ?? 0"
              :status="lead.evidence_score !== null && lead.evidence_score !== undefined && lead.evidence_score >= 70 ? 'success' : 'warning'"
              :stroke-width="8"
              :rail-color="'rgba(128,128,128,0.15)'"
              :show-text="false"
              style="width: 48px"
            />
            <span class="score-value">{{ lead.evidence_score ?? '-' }}</span>
          </div>
          <div class="complexity-tag">
            <n-tag
              size="small"
              :bordered="false"
              :type="(COMPLEXITY_MAP[lead.complexity || '']?.color as any) || 'default'"
            >
              {{ COMPLEXITY_MAP[lead.complexity || '']?.label || lead.complexity || '-' }}
            </n-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.leads-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.leads-title {
  display: flex;
  align-items: center;
  gap: 10px;
}
.leads-title h2 {
  margin: 0;
  font-size: 18px;
}
.leads-skeleton {
  padding: 4px;
}
.empty-tip {
  font-size: 12px;
  color: var(--text-tertiary);
}
.lead-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.lead-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  cursor: pointer;
  transition: all 0.2s;
}
.lead-card:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.4);
}
.lead-main {
  flex: 1;
  min-width: 0;
}
.lead-case {
  display: flex;
  align-items: center;
  gap: 8px;
}
.lead-icon {
  font-size: 18px;
}
.lead-case-name {
  font-size: 15px;
  font-weight: 700;
}
.lead-summary {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.lead-meta {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.lead-time {
  font-size: 11px;
  color: var(--text-tertiary);
}
.lead-material-badge {
  font-size: 11px;
  color: #f59e0b;
}
.lead-scores {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}
.score-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.score-label {
  font-size: 11px;
  color: var(--text-tertiary);
}
.score-value {
  font-size: 12px;
  font-weight: 700;
}
.complexity-tag {
  min-width: 70px;
  text-align: center;
}
@media (max-width: 768px) {
  .lead-card {
    flex-direction: column;
    align-items: flex-start;
  }
  .lead-scores {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
