<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NEmpty, NProgress, NSkeleton, NTag, useMessage } from 'naive-ui'
import { getRecommendations } from '@/services/lawyerService'
import type { LeadRecommendation } from '@/services/lawyerService'
import { CASE_TYPE_MAP } from '@/constants'

const router = useRouter()
const message = useMessage()

const recommendations = ref<LeadRecommendation[]>([])
const loading = ref(true)
const claimingId = ref<string | null>(null)

const caseIconMap: Record<string, string> = {
  wage_arrears: '💰',
  labor_contract: '📄',
  work_injury: '🏥',
}

onMounted(loadRecommendations)

async function loadRecommendations() {
  loading.value = true
  try {
    const data = await getRecommendations(20)
    recommendations.value = data.recommendations
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载推荐失败')
  } finally {
    loading.value = false
  }
}

async function handleClaim(id: string) {
  claimingId.value = id
  try {
    const { claimLead } = await import('@/services/lawyerService')
    await claimLead(id)
    message.success('接单成功，已同步到我的接单')
    await loadRecommendations()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '接单失败')
  } finally {
    claimingId.value = null
  }
}

function matchColor(score: number): string {
  if (score >= 80) return '#16a34a'
  if (score >= 60) return '#d97706'
  return '#dc2626'
}

function openDetail(id: string) {
  router.push(`/lawyer/leads/${id}`)
}
</script>

<template>
  <div class="dashboard-page fade-in">
    <div class="dashboard-header">
      <div>
        <h2>🎯 系统推荐线索</h2>
        <p class="dashboard-sub">根据您的擅长领域与所在地区智能匹配，优先展示高匹配度案件</p>
      </div>
      <n-button size="small" quaternary @click="loadRecommendations" :loading="loading">刷新</n-button>
    </div>

    <div v-if="loading" class="rec-skeleton">
      <n-skeleton v-for="i in 3" :key="i" height="120px" :sharp="false" style="margin-bottom: 12px" />
    </div>

    <n-empty v-else-if="recommendations.length === 0" description="暂无推荐线索">
      <template #extra>
        <span class="empty-tip">有新的待接单案件时，系统将按您的专长自动推荐</span>
      </template>
    </n-empty>

    <div v-else class="rec-list">
      <div
        v-for="rec in recommendations"
        :key="rec.lead.id"
        class="rec-card glass-card"
        @click="openDetail(rec.lead.id)"
      >
        <div class="rec-score">
          <n-progress
            type="circle"
            :percentage="rec.match_score"
            :color="matchColor(rec.match_score)"
            :stroke-width="9"
            :rail-color="'rgba(128,128,128,0.15)'"
          >
            <div class="rec-score-value">{{ rec.match_score }}</div>
            <div class="rec-score-label">匹配度</div>
          </n-progress>
        </div>

        <div class="rec-main">
          <div class="rec-top">
            <span class="rec-icon">{{ caseIconMap[rec.lead.case_type] || '⚖️' }}</span>
            <span class="rec-case-name">{{ CASE_TYPE_MAP[rec.lead.case_type]?.name || rec.lead.case_type }}</span>
            <n-tag v-if="rec.lead.region" size="small" :bordered="false" type="info">
              📍 {{ rec.lead.region }}
            </n-tag>
            <n-tag size="small" :bordered="false" :type="rec.lead.risk_score && rec.lead.risk_score >= 70 ? 'error' : rec.lead.risk_score && rec.lead.risk_score >= 45 ? 'warning' : 'success'">
              风险 {{ rec.lead.risk_score ?? '-' }}
            </n-tag>
          </div>

          <div class="rec-reasons">
            <n-tag v-for="reason in rec.reasons" :key="reason" size="small" :bordered="false" type="success">
              ✓ {{ reason }}
            </n-tag>
          </div>

          <div class="rec-summary">{{ rec.lead.summary || '暂无摘要' }}</div>

          <div class="rec-footer">
            <span class="rec-time">{{ formatTime(rec.lead.created_at) }}</span>
            <span class="rec-evidence">证据完整度 {{ rec.lead.evidence_score ?? '-' }}/100</span>
          </div>
        </div>

        <div class="rec-actions">
          <n-button
            type="primary"
            size="small"
            :loading="claimingId === rec.lead.id"
            @click.stop="handleClaim(rec.lead.id)"
          >
            🤝 接单
          </n-button>
          <n-button size="small" quaternary @click.stop="openDetail(rec.lead.id)">详情</n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
function formatTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getMonth() + 1}/${date.getDate()} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
</script>

<style scoped>
.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}
.dashboard-header h2 {
  margin: 0;
  font-size: 18px;
}
.dashboard-sub {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--text-secondary);
}
.rec-skeleton {
  padding: 4px;
}
.empty-tip {
  font-size: 12px;
  color: var(--text-tertiary);
}
.rec-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.rec-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 16px 18px;
  cursor: pointer;
  transition: all 0.2s;
}
.rec-card:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.4);
}
.rec-score {
  flex-shrink: 0;
}
.rec-score-value {
  font-size: 16px;
  font-weight: 800;
}
.rec-score-label {
  font-size: 10px;
  color: var(--text-tertiary);
}
.rec-main {
  flex: 1;
  min-width: 0;
}
.rec-top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.rec-icon {
  font-size: 18px;
}
.rec-case-name {
  font-size: 15px;
  font-weight: 700;
}
.rec-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.rec-summary {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.rec-footer {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.rec-time {
  font-size: 11px;
  color: var(--text-tertiary);
}
.rec-evidence {
  font-size: 11px;
  color: var(--text-secondary);
}
.rec-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}
@media (max-width: 768px) {
  .rec-card {
    flex-direction: column;
    align-items: flex-start;
  }
  .rec-actions {
    flex-direction: row;
  }
}
</style>
