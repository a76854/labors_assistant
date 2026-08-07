<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NEmpty, NSkeleton, NTag, useMessage } from 'naive-ui'
import { listLawyerLeads } from '@/services/lawyerService'
import type { LeadListItem } from '@/services/lawyerService'
import { CASE_TYPE_MAP, COMPLEXITY_MAP, formatRegion } from '@/constants'
import CaseTypeIcon from '@/components/CaseTypeIcon.vue'

const router = useRouter()
const message = useMessage()

const leads = ref<LeadListItem[]>([])
const total = ref(0)
const loading = ref(true)
const statusFilter = ref<string>('all')

const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '待接单', value: 'open' },
  { label: '已接单', value: 'claimed' },
  { label: '已完成', value: 'completed' },
]

const filteredLeads = computed(() => {
  if (statusFilter.value === 'all') return leads.value
  return leads.value.filter((lead) => lead.status === statusFilter.value)
})

const counts = computed(() => ({
  all: leads.value.length,
  open: leads.value.filter((l) => l.status === 'open').length,
  claimed: leads.value.filter((l) => l.status === 'claimed').length,
  completed: leads.value.filter((l) => l.status === 'completed').length,
}))

onMounted(loadLeads)

async function loadLeads() {
  loading.value = true
  try {
    const data = await listLawyerLeads(undefined, 200, 0)
    leads.value = data.leads
    total.value = data.total
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载失败')
  } finally {
    loading.value = false
  }
}

function riskClass(score: number | null | undefined) {
  if (score === null || score === undefined) return ''
  if (score >= 70) return 'risk-high'
  if (score >= 45) return 'risk-mid'
  return 'risk-low'
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
  <div class="market-page fade-in">
    <div class="page-header">
      <div>
        <h2>线索市场</h2>
        <p class="page-sub">全部待接单案件（共 {{ total }} 条）</p>
      </div>
    </div>

    <div class="filter-tabs">
      <div
        v-for="opt in statusOptions"
        :key="opt.value"
        class="filter-tab"
        :class="{ active: statusFilter === opt.value }"
        @click="statusFilter = opt.value"
      >
        {{ opt.label }}
        <span class="filter-count">{{ counts[opt.value as keyof typeof counts] }}</span>
      </div>
    </div>

    <div v-if="loading" class="skeleton-list">
      <n-skeleton v-for="i in 4" :key="i" height="56px" :sharp="false" style="margin-bottom: 8px" />
    </div>

    <n-empty v-else-if="filteredLeads.length === 0" description="暂无符合条件的线索">
      <template #extra>
        <span class="empty-tip">劳动者完成咨询分诊后，案件会自动进入线索市场</span>
      </template>
    </n-empty>

    <div v-else class="list surface-card">
      <div class="list-head">
        <span class="col col-case">案件</span>
        <span class="col col-region">地区</span>
        <span class="col col-risk">风险</span>
        <span class="col col-evidence">证据</span>
        <span class="col col-complexity">复杂度</span>
        <span class="col col-status">状态</span>
        <span class="col col-time">发布时间</span>
      </div>
      <div
        v-for="lead in filteredLeads"
        :key="lead.id"
        class="list-row"
        @click="openDetail(lead.id)"
      >
        <span class="col col-case">
          <CaseTypeIcon :type="lead.case_type" :size="16" />
          <span class="case-name">{{ CASE_TYPE_MAP[lead.case_type]?.name || lead.case_type }}</span>
        </span>
        <span class="col col-region">{{ formatRegion(lead.region) }}</span>
        <span class="col col-risk">
          <span class="risk-pill" :class="riskClass(lead.risk_score)">
            {{ lead.risk_score ?? '-' }}
          </span>
        </span>
        <span class="col col-evidence text-mono">{{ lead.evidence_score ?? '-' }}</span>
        <span class="col col-complexity">
          <n-tag
            size="small"
            :bordered="false"
            :type="(COMPLEXITY_MAP[lead.complexity || '']?.color as any) || 'default'"
          >
            {{ COMPLEXITY_MAP[lead.complexity || '']?.label || lead.complexity || '-' }}
          </n-tag>
        </span>
        <span class="col col-status">
          <n-tag
            size="small"
            :bordered="false"
            :type="lead.status === 'open' ? 'warning' : lead.status === 'claimed' ? 'success' : 'default'"
          >
            {{ lead.status === 'open' ? '待接单' : lead.status === 'claimed' ? '已接单' : '已完成' }}
          </n-tag>
        </span>
        <span class="col col-time text-tertiary">{{ formatTime(lead.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}
.page-sub {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--text-secondary);
}
.filter-tabs {
  display: flex;
  gap: 2px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}
.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  position: relative;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all var(--transition-fast);
}
.filter-tab:hover {
  color: var(--text-primary);
}
.filter-tab.active {
  color: var(--color-primary);
  font-weight: 600;
  border-bottom-color: var(--color-primary);
}
.filter-count {
  font-size: 11px;
  padding: 1px 7px;
  border-radius: var(--radius-full);
  background: var(--bg-subtle);
  color: var(--text-tertiary);
  line-height: 16px;
  font-variant-numeric: tabular-nums;
}
.filter-tab.active .filter-count {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}
.skeleton-list {
  padding: 4px;
}
.empty-tip {
  font-size: 12px;
  color: var(--text-tertiary);
}
.list {
  overflow: hidden;
  padding: 0;
}
.list-head,
.list-row {
  display: grid;
  grid-template-columns: 1.6fr 80px 80px 80px 100px 100px 120px;
  align-items: center;
  padding: 12px 18px;
  gap: 10px;
  font-size: 13px;
}
.list-head {
  background: var(--bg-subtle);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-tertiary);
  letter-spacing: 0.3px;
  border-bottom: 1px solid var(--border-color);
}
.list-row {
  cursor: pointer;
  border-bottom: 1px solid var(--border-subtle);
  transition: background var(--transition-fast);
}
.list-row:last-child {
  border-bottom: none;
}
.list-row:hover {
  background: var(--bg-subtle);
}
.col {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}
.col-case {
  display: flex;
  align-items: center;
  gap: 8px;
}
.case-name {
  font-weight: 600;
  color: var(--text-primary);
}
.risk-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  padding: 1px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 18px;
}
.risk-high {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}
.risk-mid {
  background: var(--color-warning-soft);
  color: var(--color-warning);
}
.risk-low {
  background: var(--color-success-soft);
  color: var(--color-success);
}
@media (max-width: 900px) {
  .list-head {
    display: none;
  }
  .list-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>
