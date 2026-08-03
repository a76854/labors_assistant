<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NCheckbox,
  NDescriptions,
  NDescriptionsItem,
  NEmpty,
  NInput,
  NPopconfirm,
  NProgress,
  NSpin,
  NTag,
  useMessage,
} from 'naive-ui'
import { claimLead, completeLead, getLawyerLead, requestMaterials } from '@/services/lawyerService'
import type { LeadDetail } from '@/services/lawyerService'
import { CASE_TYPE_MAP, COMPLEXITY_MAP, LEAD_STATUS_MAP } from '@/constants'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const leadId = String(route.params.leadId)
const lead = ref<LeadDetail | null>(null)
const loading = ref(true)
const notFound = ref(false)
const acting = ref(false)
const requesting = ref(false)

const materialItems = ref([
  { name: '劳动合同原件', description: '需提供完整劳动合同或聘用协议扫描件', checked: true },
  { name: '工资流水/工资条', description: '近 6 个月银行流水或工资条', checked: true },
  { name: '考勤记录', description: '打卡记录、考勤表等', checked: false },
  { name: '沟通记录', description: '与公司沟通工资/工伤事宜的聊天记录、邮件', checked: false },
  { name: '工作身份证明', description: '工牌、社保缴纳记录、名片等', checked: false },
  { name: '工伤认定材料', description: '工伤认定书、诊断证明、医疗费票据', checked: false },
  { name: '解除/辞退通知', description: '辞退通知、解除劳动合同通知书', checked: false },
])
const noteText = ref('')

onMounted(loadDetail)

async function loadDetail() {
  loading.value = true
  try {
    lead.value = await getLawyerLead(leadId)
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

function riskStatus(score: number | null | undefined): 'error' | 'warning' | 'success' {
  if (score === null || score === undefined) return 'success'
  if (score >= 70) return 'error'
  if (score >= 45) return 'warning'
  return 'success'
}

function formatTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

async function handleClaim() {
  acting.value = true
  try {
    await claimLead(leadId)
    message.success('接单成功')
    await loadDetail()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '接单失败')
  } finally {
    acting.value = false
  }
}

async function handleComplete() {
  acting.value = true
  try {
    await completeLead(leadId)
    message.success('案件已标记完成')
    await loadDetail()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '操作失败')
  } finally {
    acting.value = false
  }
}

async function handleRequestMaterials() {
  const selected = materialItems.value.filter((item) => item.checked)
  if (selected.length === 0) {
    message.warning('请至少选择一项材料')
    return
  }
  requesting.value = true
  try {
    await requestMaterials(leadId, {
      items: selected.map((item) => ({ name: item.name, description: item.description })),
      note: noteText.value || undefined,
    })
    message.success('补充材料请求已发送给劳动者')
    await loadDetail()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '发送失败')
  } finally {
    requesting.value = false
  }
}

const materialRequests = computed(() => lead.value?.material_requests || [])
</script>

<template>
  <div class="lead-detail fade-in">
    <div class="detail-nav">
      <n-button size="small" quaternary @click="router.back()">← 返回线索列表</n-button>
    </div>

    <n-spin :show="loading">
      <n-empty v-if="notFound" description="线索不存在">
        <template #extra>
          <n-button type="primary" @click="router.back()">返回列表</n-button>
        </template>
      </n-empty>

      <template v-else-if="lead">
        <!-- 案件概览 -->
        <div class="detail-card glass-card">
          <div class="card-header">
            <div class="case-head">
              <span class="case-icon">{{ CASE_TYPE_MAP[lead.case_type]?.icon || '⚖️' }}</span>
              <h2>{{ CASE_TYPE_MAP[lead.case_type]?.name || lead.case_type }}</h2>
              <n-tag :bordered="false" :type="(LEAD_STATUS_MAP[lead.status]?.type as any) || 'default'">
                {{ LEAD_STATUS_MAP[lead.status]?.label }}
              </n-tag>
            </div>
            <div class="case-actions">
              <n-popconfirm v-if="lead.status === 'claimed'" @positive-click="handleComplete">
                <template #trigger>
                  <n-button size="small" :loading="acting">✅ 标记完成</n-button>
                </template>
                确认案件已完成？
              </n-popconfirm>
              <n-button
                v-else-if="lead.status === 'open'"
                type="primary"
                size="small"
                :loading="acting"
                @click="handleClaim"
              >
                🤝 接单
              </n-button>
            </div>
          </div>

          <n-descriptions bordered size="small" :column="2" class="case-meta">
            <n-descriptions-item label="线索 ID">{{ lead.id.slice(0, 8) }}…</n-descriptions-item>
            <n-descriptions-item label="发布时间">{{ formatTime(lead.created_at) }}</n-descriptions-item>
            <n-descriptions-item label="发布者">
              {{ lead.user_username || '-' }}
              <span v-if="lead.user_phone" class="phone-mask">({{ lead.user_phone }})</span>
            </n-descriptions-item>
            <n-descriptions-item label="地区">📍 {{ lead.region || '-' }}</n-descriptions-item>
          </n-descriptions>

          <div class="score-row">
            <div class="score-box">
              <span class="score-box-label">风险评分</span>
              <n-progress
                type="circle"
                :percentage="lead.risk_score ?? 0"
                :status="riskStatus(lead.risk_score)"
                :stroke-width="9"
                :rail-color="'rgba(128,128,128,0.15)'"
              >
                <div class="score-box-value">{{ lead.risk_score ?? '-' }}</div>
              </n-progress>
            </div>
            <div class="score-box">
              <span class="score-box-label">证据完整度</span>
              <n-progress
                type="circle"
                :percentage="lead.evidence_score ?? 0"
                :status="(lead.evidence_score ?? 0) >= 70 ? 'success' : 'warning'"
                :stroke-width="9"
                :rail-color="'rgba(128,128,128,0.15)'"
              >
                <div class="score-box-value">{{ lead.evidence_score ?? '-' }}</div>
              </n-progress>
            </div>
            <div class="score-box">
              <span class="score-box-label">复杂度</span>
              <div class="complexity-display">
                <n-tag
                  size="large"
                  :bordered="false"
                  :type="(COMPLEXITY_MAP[lead.complexity || '']?.color as any) || 'default'"
                >
                  {{ COMPLEXITY_MAP[lead.complexity || '']?.label || lead.complexity || '-' }}
                </n-tag>
              </div>
            </div>
            <div class="missing-box">
              <span class="score-box-label">缺失证据</span>
              <div class="missing-tags">
                <n-tag v-for="item in lead.missing_evidence" :key="item" size="small" :bordered="false" type="warning">
                  {{ item }}
                </n-tag>
                <span v-if="lead.missing_evidence.length === 0" class="no-missing">✓ 证据覆盖良好</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 对话摘要 -->
        <div class="detail-card glass-card">
          <h3 class="card-subtitle">💬 案情对话摘要</h3>
          <div class="msg-summary">
            <div v-for="(msg, index) in lead.messages" :key="index" class="msg-line" :class="msg.role">
              <span class="msg-role">{{ msg.role === 'user' ? '劳动者' : 'AI助手' }}</span>
              <span class="msg-content">{{ msg.content }}</span>
            </div>
          </div>
        </div>

        <!-- 补充材料请求 -->
        <div class="detail-card glass-card">
          <h3 class="card-subtitle">📎 补充材料请求</h3>

          <div v-if="lead.status !== 'open'" class="request-form">
            <div class="material-grid">
              <label v-for="item in materialItems" :key="item.name" class="material-option">
                <n-checkbox v-model:checked="item.checked">
                  <span class="material-name">{{ item.name }}</span>
                  <span class="material-desc">{{ item.description }}</span>
                </n-checkbox>
              </label>
            </div>
            <n-input v-model:value="noteText" type="textarea" placeholder="备注（选填）：说明材料用途与提交要求…" :rows="2" />
            <n-button
              type="primary"
              :loading="requesting"
              :disabled="lead.status !== 'claimed'"
              @click="handleRequestMaterials"
            >
              🚀 一键发起补充材料请求
            </n-button>
            <span v-if="lead.status !== 'claimed'" class="form-hint">
              接单后即可向劳动者发起补充材料请求
            </span>
          </div>
          <div v-else class="request-placeholder">接单后可向劳动者发起补充材料请求</div>

          <div v-if="materialRequests.length > 0" class="request-history">
            <div v-for="request in materialRequests" :key="request.id" class="request-item">
              <div class="request-head">
                <span class="request-time">{{ formatTime(request.created_at) }}</span>
                <n-tag size="small" :bordered="false" :type="request.status === 'satisfied' ? 'success' : 'warning'">
                  {{ request.status === 'satisfied' ? '已补充' : '待补充' }}
                </n-tag>
              </div>
              <div v-if="request.note" class="request-note">备注：{{ request.note }}</div>
              <div v-for="item in request.items" :key="item.name" class="request-item-row">
                <span>· {{ item.name }}</span>
                <span v-if="item.description" class="request-item-desc">{{ item.description }}</span>
                <n-tag
                  v-if="item.status === 'satisfied'"
                  size="tiny"
                  :bordered="false"
                  type="success"
                  style="margin-left: 8px"
                >
                  已补充
                </n-tag>
              </div>
            </div>
          </div>
        </div>
      </template>
    </n-spin>
  </div>
</template>

<style scoped>
.detail-nav {
  margin-bottom: 12px;
}
.detail-card {
  padding: 20px;
  margin-bottom: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.case-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.case-icon {
  font-size: 24px;
}
.case-head h2 {
  margin: 0;
  font-size: 18px;
}
.case-actions {
  display: flex;
  gap: 8px;
}
.case-meta {
  margin-bottom: 18px;
}
.phone-mask {
  color: var(--text-tertiary);
  font-size: 12px;
}
.score-row {
  display: grid;
  grid-template-columns: 130px 130px 130px 1fr;
  gap: 16px;
  align-items: start;
}
@media (max-width: 900px) {
  .score-row {
    grid-template-columns: 1fr 1fr;
  }
}
.score-box {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.score-box-label {
  font-size: 12px;
  color: var(--text-secondary);
}
.score-box-value {
  font-size: 15px;
  font-weight: 800;
}
.complexity-display {
  padding-top: 14px;
}
.missing-box {
  padding: 4px 0 0 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.missing-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.no-missing {
  font-size: 13px;
  color: #16a34a;
}
.card-subtitle {
  margin: 0 0 14px;
  font-size: 15px;
}
.msg-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 320px;
  overflow-y: auto;
}
.msg-line {
  display: flex;
  gap: 10px;
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(128, 128, 128, 0.05);
}
.msg-line.user {
  border-left: 3px solid rgba(59, 130, 246, 0.6);
}
.msg-role {
  flex-shrink: 0;
  font-weight: 700;
  color: var(--color-primary);
  min-width: 44px;
}
.msg-content {
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
}
.material-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}
.material-option {
  display: flex;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
}
.material-option:hover {
  border-color: rgba(59, 130, 246, 0.4);
}
.material-name {
  font-size: 13px;
  font-weight: 600;
  display: block;
}
.material-desc {
  font-size: 11px;
  color: var(--text-tertiary);
}
.request-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.form-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}
.request-placeholder {
  padding: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--text-tertiary);
  border: 1px dashed var(--border-color);
  border-radius: 8px;
}
.request-history {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.request-item {
  padding: 12px 14px;
  border-radius: 8px;
  background: rgba(128, 128, 128, 0.05);
  border: 1px solid var(--border-color);
}
.request-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.request-time {
  font-size: 12px;
  color: var(--text-tertiary);
}
.request-note {
  font-size: 12.5px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.request-item-row {
  font-size: 13px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}
.request-item-desc {
  color: var(--text-tertiary);
  font-size: 12px;
  margin-left: 8px;
}
</style>
