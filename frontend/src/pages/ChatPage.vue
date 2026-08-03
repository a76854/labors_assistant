<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NEmpty,
  NProgress,
  NTag,
  NTooltip,
  useMessage,
} from 'naive-ui'
import {
  createSession,
  deleteSession,
  getMessages,
  getSession,
  listSessions,
  streamChat,
  syncMessages,
} from '@/services/chatService'
import { generateDocument } from '@/services/documentService'
import { getSessionLead, triageSession } from '@/services/lawyerService'
import type { TriageResponse, SessionLeadInfo } from '@/services/lawyerService'
import type { SessionListItem, SessionResponse } from '@/services/chatService'
import type { MessageResponse } from '@/services/chatService'
import SessionHistoryPanel from '@/components/SessionHistoryPanel.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import { CASE_TYPE_MAP, CASE_TYPES, TOOL_HINTS, COMPLEXITY_MAP, LEAD_STATUS_MAP, formatRegion } from '@/constants'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const DOCUMENT_READY_SIGNAL = '请点击右上角生成诉状'

const sessionId = computed(() => String(route.params.sessionId))
const caseType = computed(() => session.value?.case_type || '')

const session = ref<SessionResponse | null>(null)
const messages = ref<MessageResponse[]>([])
const historySessions = ref<SessionListItem[]>([])
const inputText = ref('')
const isInitializing = ref(true)
const isSending = ref(false)
const isTyping = ref(false)
const currentReply = ref('')
const toolHint = ref('')
const isGeneratingDoc = ref(false)
const deletingSessionId = ref<string | null>(null)
const notFound = ref(false)
const messagesEndRef = ref<HTMLElement | null>(null)

// 分诊
const triage = ref<TriageResponse | null>(null)
const triageLoading = ref(false)
const leadInfo = ref<SessionLeadInfo | null>(null)
const leadLoading = ref(false)

const activeToolMessage = ref<{ icon: string; label: string } | null>(null)

let abortController: AbortController | null = null

const isDocumentGenerationReady = computed(() => {
  return messages.value.some(
    (m) => m.role === 'assistant' && m.content.includes(DOCUMENT_READY_SIGNAL),
  )
})

const canGenerateDoc = computed(() => {
  return (
    !isInitializing.value &&
    !isSending.value &&
    !isGeneratingDoc.value &&
    isDocumentGenerationReady.value &&
    caseType.value !== 'other'
  )
})

const guidance = computed(() => {
  const found = CASE_TYPES.find((item) => item.key === caseType.value)
  if (!found) return []
  return [
    `我想咨询${found.name}，公司${caseType.value === 'work_injury' ? '在工作中受伤了' : '拖欠我工资'}`,
    '需要准备哪些材料？',
    '我的胜诉可能性有多大？',
  ]
})

const toolIconMap: Record<string, { icon: string; label: string }> = {
  search_public_laws_tool: { icon: '📚', label: '检索法律条文' },
  search_public_cases_tool: { icon: '📋', label: '检索相似判例' },
  search_private_knowledge_tool: { icon: '🗂️', label: '检索私域知识' },
  generate_legal_doc_tool: { icon: '📝', label: '生成法律文书' },
}

const riskColor = computed(() => {
  const score = triage.value?.risk_score ?? 0
  if (score >= 70) return 'error'
  if (score >= 45) return 'warning'
  return 'success'
})

onMounted(async () => {
  await Promise.all([loadHistory(), initSession()])
})

watch(messages, async () => {
  await scrollToBottom()
  if (!triage.value) {
    await loadLeadStatus()
  }
}, { deep: true })

async function scrollToBottom() {
  await nextTick()
  messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
}

async function loadHistory() {
  try {
    const data = await listSessions(20, 0)
    historySessions.value = data.sessions
  } catch {
    /* ignore */
  }
}

async function initSession() {
  isInitializing.value = true
  try {
    session.value = await getSession(sessionId.value)
    const history = await getMessages(sessionId.value, 100, 0)
    messages.value = history.messages
    await loadLeadStatus()
  } catch {
    notFound.value = true
  } finally {
    isInitializing.value = false
  }
}

async function loadLeadStatus() {
  leadLoading.value = true
  try {
    const data = await getSessionLead(sessionId.value)
    leadInfo.value = data.lead
  } catch {
    /* ignore */
  } finally {
    leadLoading.value = false
  }
}

function handleQuickQuestion(question: string) {
  inputText.value = question
  handleSend()
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || isSending.value) return
  inputText.value = ''
  isSending.value = true
  isTyping.value = true
  toolHint.value = ''
  currentReply.value = ''
  activeToolMessage.value = null

  messages.value = [
    ...messages.value,
    {
      id: `local-user-${Date.now()}`,
      session_id: sessionId.value,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    },
  ]
  await scrollToBottom()

  abortController = new AbortController()
  const streamedTokens: string[] = []

  try {
    await streamChat(
      sessionId.value,
      text,
      {
        onToken: (token) => {
          streamedTokens.push(token)
          currentReply.value += token
        },
        onToolStart: (toolName) => {
          const tool = toolIconMap[toolName] || { icon: '⚙️', label: TOOL_HINTS[toolName] || '执行工具' }
          activeToolMessage.value = tool
        },
        onToolEnd: () => {
          activeToolMessage.value = null
        },
        onError: (err) => {
          message.error(err)
        },
      },
      abortController.signal,
    )
  } catch (error) {
    if ((error as Error)?.name !== 'AbortError') {
      message.error(error instanceof Error ? error.message : '请求失败')
    }
  } finally {
    if (streamedTokens.length > 0 || currentReply.value.trim()) {
      const assistantContent = currentReply.value.trim() || streamedTokens.join('')
      if (assistantContent) {
        messages.value = [
          ...messages.value,
          {
            id: `local-assistant-${Date.now()}`,
            session_id: sessionId.value,
            role: 'assistant',
            content: assistantContent,
            timestamp: new Date().toISOString(),
          },
        ]
        try {
          await syncMessages(sessionId.value, [
            { role: 'user', content: text },
            { role: 'assistant', content: assistantContent },
          ])
        } catch {
          /* ignore */
        }
      }
    }
    isSending.value = false
    isTyping.value = false
    activeToolMessage.value = null
    await loadHistory()
  }
}

function handleStop() {
  abortController?.abort()
  isSending.value = false
  isTyping.value = false
}

async function handleGenerateDoc() {
  isGeneratingDoc.value = true
  try {
    const doc = await generateDocument(sessionId.value, {
      template_id: caseType.value,
      format: 'docx',
    })
    message.success('文书已生成')
    router.push(`/result/${doc.id}`)
  } catch (error) {
    message.error(error instanceof Error ? error.message : '文书生成失败')
  } finally {
    isGeneratingDoc.value = false
  }
}

async function handleTriage() {
  triageLoading.value = true
  try {
    triage.value = await triageSession(sessionId.value)
    await loadLeadStatus()
    message.success('案件分诊完成，已同步发布为律师线索')
  } catch (error) {
    message.error(error instanceof Error ? error.message : '分诊失败')
  } finally {
    triageLoading.value = false
  }
}

function handleDeleteSession(id: string) {
  deletingSessionId.value = id
  deleteSession(id)
    .then(async () => {
      message.success('会话已删除')
      await loadHistory()
    })
    .catch((error) => message.error(error instanceof Error ? error.message : '删除失败'))
    .finally(() => {
      deletingSessionId.value = null
    })
}

function handleSelectSession(id: string) {
  if (id === sessionId.value) return
  router.push(`/chat/${id}`)
}

async function handleNewSession() {
  try {
    const s = await createSession({ case_type: 'wage_arrears', region: 'beijing' })
    router.push(`/chat/${s.id}`)
  } catch (error) {
    message.error(error instanceof Error ? error.message : '创建失败')
  }
}
</script>

<template>
  <div class="chat-page page-container">
    <aside class="side-panel glass-card">
      <div class="panel-title">历史咨询</div>
      <SessionHistoryPanel
        :sessions="historySessions"
        :loading="isInitializing"
        :active-id="sessionId"
        :show-new-entry="true"
        @select="handleSelectSession"
        @delete="handleDeleteSession"
        @new-session="handleNewSession"
      />
    </aside>

    <main class="chat-container glass-card">
      <template v-if="notFound">
        <n-empty description="会话不存在或已删除" style="margin-top: 80px">
          <template #extra>
            <n-button type="primary" @click="router.push('/')">返回首页</n-button>
          </template>
        </n-empty>
      </template>

      <template v-else>
        <header class="chat-header">
          <div class="chat-title">
            <span class="chat-case-icon">{{ CASE_TYPE_MAP[caseType]?.icon || '⚖️' }}</span>
            <span>{{ CASE_TYPE_MAP[caseType]?.name || caseType }}</span>
            <n-tag v-if="session?.region" size="small" :bordered="false" type="info">
              📍 {{ formatRegion(session.region) }}
            </n-tag>
          </div>
          <n-tooltip :disabled="canGenerateDoc">
            <template #trigger>
              <n-button
                type="primary"
                :loading="isGeneratingDoc"
                :disabled="!canGenerateDoc"
                @click="handleGenerateDoc"
              >
                📄 生成诉状
              </n-button>
            </template>
            {{ isDocumentGenerationReady ? '' : '请先与 AI 完成案情信息收集（等待提示“请点击右上角生成诉状”）' }}
          </n-tooltip>
        </header>

        <!-- 分诊卡片 -->
        <div v-if="triage" class="triage-card fade-in">
          <div class="triage-header">
            <span class="triage-title">🔍 案件分诊结果</span>
            <div class="triage-actions">
              <n-button size="tiny" quaternary @click="handleTriage" :loading="triageLoading">
                重新分诊
              </n-button>
            </div>
          </div>
          <div class="triage-grid">
            <div class="triage-metric">
              <div class="metric-label">证据完整度</div>
              <n-progress
                type="circle"
                :percentage="triage.evidence_score"
                :color="triage.evidence_score >= 70 ? '#16a34a' : triage.evidence_score >= 40 ? '#d97706' : '#dc2626'"
                :stroke-width="8"
                :rail-color="'rgba(128,128,128,0.15)'"
              >
                <div class="metric-value">{{ triage.evidence_score }}</div>
              </n-progress>
            </div>
            <div class="triage-metric">
              <div class="metric-label">风险评分</div>
              <n-progress
                type="circle"
                :percentage="triage.risk_score"
                :status="riskColor"
                :stroke-width="8"
                :rail-color="'rgba(128,128,128,0.15)'"
              >
                <div class="metric-value">{{ triage.risk_score }}</div>
              </n-progress>
            </div>
            <div class="triage-detail">
              <div class="detail-row">
                <span>复杂度</span>
                <n-tag :bordered="false" :type="(COMPLEXITY_MAP[triage.complexity]?.color as any) || 'default'" size="small">
                  {{ COMPLEXITY_MAP[triage.complexity]?.label || triage.complexity }}
                </n-tag>
              </div>
              <div class="detail-row">
                <span>已覆盖证据</span>
                <span class="detail-tags">
                  <n-tag v-for="item in triage.evidence_covered" :key="item" size="small" :bordered="false" type="success">
                    {{ item }}
                  </n-tag>
                </span>
              </div>
              <div class="detail-row">
                <span>缺失证据</span>
                <span class="detail-tags">
                  <n-tag v-for="item in triage.missing_evidence" :key="item" size="small" :bordered="false" type="warning">
                    {{ item }}
                  </n-tag>
                </span>
              </div>
            </div>
          </div>

          <!-- 推荐律师 -->
          <div class="lawyer-section">
            <div class="lawyer-section-title">
              <span>👨‍⚖️ 推荐律师</span>
              <n-tag v-if="leadInfo" size="small" :bordered="false" :type="(LEAD_STATUS_MAP[leadInfo.status]?.type as any) || 'default'">
                线索已发布：{{ LEAD_STATUS_MAP[leadInfo.status]?.label }}
              </n-tag>
            </div>
            <div class="lawyer-grid">
              <div v-for="lawyer in triage.recommended_lawyers" :key="lawyer.id" class="lawyer-card">
                <div class="lawyer-name">
                  {{ lawyer.name }}
                  <span class="lawyer-rating">⭐ {{ lawyer.rating }}</span>
                </div>
                <div class="lawyer-meta">执业 {{ lawyer.years }} 年 · {{ lawyer.license_no }}</div>
                <div class="lawyer-desc">{{ lawyer.desc }}</div>
              </div>
            </div>
            <div v-if="leadInfo?.status === 'claimed'" class="lead-claimed-hint">
              🎉 已有律师接单，请注意补充材料提醒
            </div>
          </div>

          <!-- 补充材料提醒 -->
          <div
            v-for="request in leadInfo?.material_requests"
            :key="request.id"
            class="material-request-card"
          >
            <div class="mr-header">
              <span>📎 律师发起补充材料请求</span>
              <n-tag size="small" :bordered="false" :type="request.status === 'satisfied' ? 'success' : 'warning'">
                {{ request.status === 'satisfied' ? '已补充' : '待补充' }}
              </n-tag>
            </div>
            <div v-if="request.note" class="mr-note">备注：{{ request.note }}</div>
            <div v-for="item in request.items" :key="item.name" class="mr-item">
              <span class="mr-item-name">· {{ item.name }}</span>
              <span v-if="item.description" class="mr-item-desc">{{ item.description }}</span>
            </div>
          </div>
        </div>

        <!-- 未分诊时的提示条 -->
        <div v-else-if="messages.length >= 2 && !leadLoading" class="triage-hint">
          <span>💡 已获取初步案情，可进行案件分诊并发布给律师</span>
          <n-button size="small" type="primary" ghost :loading="triageLoading" @click="handleTriage">
            开始分诊
          </n-button>
        </div>

        <!-- 消息区 -->
        <div class="messages-area">
          <div v-if="messages.length === 0" class="empty-chat">
            <div class="empty-icon">🤖</div>
            <p>您好，我是您的维权助手</p>
            <p class="empty-sub">请描述您的劳动争议情况，我会帮您分析并生成法律文书</p>
            <div class="quick-questions">
              <n-button
                v-for="q in guidance"
                :key="q"
                size="small"
                secondary
                @click="handleQuickQuestion(q)"
              >
                {{ q }}
              </n-button>
            </div>
          </div>

          <div v-for="msg in messages" :key="msg.id" class="message-row" :class="msg.role">
            <div class="message-avatar">{{ msg.role === 'assistant' ? '⚖️' : '👤' }}</div>
            <div class="message-bubble">
              <MarkdownRenderer v-if="msg.role === 'assistant'" :content="msg.content" />
              <div v-else class="user-text">{{ msg.content }}</div>
            </div>
          </div>

          <!-- 打字中 -->
          <div v-if="isTyping" class="message-row assistant">
            <div class="message-avatar">⚖️</div>
            <div class="message-bubble">
              <div v-if="activeToolMessage" class="tool-hint">
                <span>{{ activeToolMessage.icon }}</span>
                <span>{{ activeToolMessage.label }}</span>
                <span class="typing-dots"><i></i><i></i><i></i></span>
              </div>
              <div v-else class="typing-indicator">
                <span class="typing-dots"><i></i><i></i><i></i></span>
                <span class="typing-cursor"></span>
              </div>
              <div v-if="currentReply" class="stream-reply">
                <MarkdownRenderer :content="currentReply" />
              </div>
            </div>
          </div>

          <div ref="messagesEndRef" />
        </div>

        <!-- 输入区 -->
        <footer class="chat-footer">
          <textarea
            v-model="inputText"
            class="chat-input"
            placeholder="描述您的案情…（Enter 发送，Shift+Enter 换行）"
            :disabled="isSending"
            @keydown.enter.exact.prevent="handleSend"
          />
          <div class="footer-actions">
            <n-button v-if="isSending" size="small" quaternary type="error" @click="handleStop">
              ⏹ 停止
            </n-button>
            <n-button type="primary" size="small" :disabled="!inputText.trim() || isSending" @click="handleSend">
              发送
            </n-button>
          </div>
        </footer>
      </template>
    </main>
  </div>
</template>

<style scoped>
.chat-page {
  max-width: 1200px;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
}
@media (max-width: 1024px) {
  .chat-page {
    grid-template-columns: 1fr;
  }
}
.side-panel {
  padding: 14px;
  align-self: start;
  position: sticky;
  top: calc(var(--navbar-height) + 24px);
  max-height: calc(100vh - var(--navbar-height) - 48px);
  overflow-y: auto;
}
@media (max-width: 1024px) {
  .side-panel {
    position: static;
    max-height: 280px;
  }
}
.panel-title {
  font-size: 14px;
  font-weight: 700;
  padding: 4px 8px 10px;
}
.chat-container {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - var(--navbar-height) - 80px);
  overflow: hidden;
}
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-color);
}
.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
}
.chat-case-icon {
  font-size: 18px;
}
.triage-card {
  margin: 14px 20px 0;
  padding: 16px;
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: var(--radius-md);
  background: rgba(59, 130, 246, 0.05);
}
.triage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.triage-title {
  font-weight: 700;
  font-size: 14px;
}
.triage-grid {
  display: grid;
  grid-template-columns: 110px 110px 1fr;
  gap: 16px;
  align-items: center;
}
@media (max-width: 768px) {
  .triage-grid {
    grid-template-columns: 1fr 1fr;
  }
}
.triage-metric {
  text-align: center;
}
.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}
.metric-value {
  font-size: 16px;
  font-weight: 800;
}
.triage-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
}
.detail-row > span:first-child {
  color: var(--text-secondary);
  white-space: nowrap;
  min-width: 60px;
}
.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.lawyer-section {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px dashed var(--border-color);
}
.lawyer-section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
}
.lawyer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}
.lawyer-card {
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
}
.lawyer-name {
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.lawyer-rating {
  font-size: 12px;
  color: #f59e0b;
}
.lawyer-meta {
  font-size: 11px;
  color: var(--text-tertiary);
  margin: 2px 0 6px;
}
.lawyer-desc {
  font-size: 12px;
  color: var(--text-secondary);
}
.lead-claimed-hint {
  margin-top: 10px;
  font-size: 13px;
  color: #34d399;
}
.material-request-card {
  margin-top: 12px;
  padding: 12px;
  border-radius: var(--radius-md);
  background: rgba(245, 158, 11, 0.07);
  border: 1px solid rgba(245, 158, 11, 0.25);
}
.mr-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 700;
}
.mr-note {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
}
.mr-item {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  font-size: 12.5px;
}
.mr-item-name {
  font-weight: 600;
}
.mr-item-desc {
  color: var(--text-secondary);
}
.triage-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 14px 20px 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(59, 130, 246, 0.06);
  border: 1px dashed rgba(59, 130, 246, 0.3);
  font-size: 13px;
}
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 300px;
  max-height: 60vh;
}
.empty-chat {
  text-align: center;
  margin: 60px auto;
  max-width: 460px;
}
.empty-icon {
  font-size: 48px;
}
.empty-chat p {
  margin: 6px 0;
  font-size: 15px;
  font-weight: 600;
}
.empty-sub {
  font-weight: 400 !important;
  font-size: 13px !important;
  color: var(--text-secondary);
}
.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 20px;
}
.message-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.message-row.user {
  flex-direction: row-reverse;
}
.message-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  flex-shrink: 0;
}
.message-bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
}
.message-row.user .message-bubble {
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.25);
}
.user-text {
  white-space: pre-wrap;
  word-break: break-word;
}
.tool-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: var(--text-secondary);
}
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}
.typing-dots {
  display: inline-flex;
  gap: 4px;
}
.typing-dots i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: dotPulse 1.2s infinite;
}
.typing-dots i:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-dots i:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes dotPulse {
  0%,
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}
.stream-reply {
  margin-top: 8px;
}
.chat-footer {
  border-top: 1px solid var(--border-color);
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.chat-input {
  width: 100%;
  min-height: 60px;
  max-height: 140px;
  resize: vertical;
  border: none;
  outline: none;
  background: transparent;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
}
.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
