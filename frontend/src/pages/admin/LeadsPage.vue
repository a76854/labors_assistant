<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NEmpty, NSelect, NSkeleton, NTag, useMessage } from 'naive-ui'
import { getAdminLeads } from '@/services/adminService'
import type { AdminLead } from '@/services/adminService'
import CaseTypeIcon from '@/components/CaseTypeIcon.vue'
import { CASE_TYPE_MAP, COMPLEXITY_MAP, formatRegion } from '@/constants'

const message = useMessage()

const leads = ref<AdminLead[]>([])
const total = ref(0)
const loading = ref(true)
const statusFilter = ref<string | null>(null)

const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '待接单', value: 'open' },
  { label: '已接单', value: 'claimed' },
  { label: '已完成', value: 'completed' },
]

onMounted(loadLeads)

async function loadLeads() {
  loading.value = true
  try {
    const data = await getAdminLeads(statusFilter.value || undefined, 200, 0)
    leads.value = data.leads
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
  return `${date.getMonth() + 1}/${date.getDate()} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
</script>

<template>
  <div class="admin-leads fade-in">
    <div class="leads-header">
      <div>
        <h2><AppIcon name="file" :size="14" /> 线索管理</h2>
        <p class="leads-sub">全平台案件线索（共 {{ total }} 条）</p>
      </div>
      <n-select
        v-model:value="statusFilter"
        :options="statusOptions"
        size="small"
        style="width: 140px"
        @update:value="loadLeads"
      />
    </div>

    <div v-if="loading" class="leads-skeleton">
      <n-skeleton v-for="i in 5" :key="i" height="56px" :sharp="false" style="margin-bottom: 8px" />
    </div>

    <n-empty v-else-if="leads.length === 0" description="暂无线索" />

    <div v-else class="lead-table glass-card">
      <div class="table-row table-head">
        <span>案件</span>
        <span>状态</span>
        <span>发布者</span>
        <span>接单律师</span>
        <span>风险</span>
        <span>证据</span>
        <span>复杂度</span>
        <span>创建时间</span>
      </div>
      <div v-for="lead in leads" :key="lead.id" class="table-row">
        <span class="lead-case">
          <CaseTypeIcon :type="lead.case_type" :size="18" />
          {{ CASE_TYPE_MAP[lead.case_type]?.name || lead.case_type }}
          <n-tag v-if="lead.region" size="tiny" :bordered="false" type="info">{{ formatRegion(lead.region) }}</n-tag>
        </span>
        <span>
          <n-tag
            size="small"
            :bordered="false"
            :type="lead.status === 'open' ? 'warning' : lead.status === 'claimed' ? 'success' : 'default'"
          >
            {{ lead.status === 'open' ? '待接单' : lead.status === 'claimed' ? '已接单' : '已完成' }}
          </n-tag>
        </span>
        <span>{{ lead.user_username || '-' }}</span>
        <span>{{ lead.lawyer_username || '-' }}</span>
        <span class="risk-value" :class="(lead.risk_score ?? 0) >= 70 ? 'high' : (lead.risk_score ?? 0) >= 45 ? 'mid' : 'low'">
          {{ lead.risk_score ?? '-' }}
        </span>
        <span>{{ lead.evidence_score ?? '-' }}</span>
        <span>
          <n-tag size="small" :bordered="false" :type="(COMPLEXITY_MAP[lead.complexity || '']?.color as any) || 'default'">
            {{ COMPLEXITY_MAP[lead.complexity || '']?.label || lead.complexity || '-' }}
          </n-tag>
        </span>
        <span class="lead-time">{{ formatTime(lead.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.leads-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}
.leads-header h2 {
  margin: 0;
  font-size: 18px;
}
.leads-sub {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--text-secondary);
}
.leads-skeleton {
  padding: 4px;
}
.lead-table {
  overflow-x: auto;
}
.table-row {
  display: grid;
  grid-template-columns: 1.6fr 90px 110px 120px 60px 60px 90px 120px;
  gap: 10px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  min-width: 860px;
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
.lead-case {
  display: flex;
  align-items: center;
  gap: 6px;
}
.risk-value {
  font-weight: 700;
}
.risk-value.high {
  color: #ef4444;
}
.risk-value.mid {
  color: #f59e0b;
}
.risk-value.low {
  color: #16a34a;
}
.lead-time {
  color: var(--text-tertiary);
  font-size: 12px;
}
</style>
