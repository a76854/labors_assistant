<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSelect, useMessage } from 'naive-ui'
import { CASE_TYPES, DEFAULT_REGION } from '@/constants'
import { createSession, deleteSession, listSessions } from '@/services/chatService'
import { listRegions } from '@/services/lawyerService'
import type { RegionInfo } from '@/services/lawyerService'
import type { SessionListItem } from '@/services/chatService'
import SessionHistoryPanel from '@/components/SessionHistoryPanel.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const selectedType = ref<string>('')
const selectedRegion = ref<string>(DEFAULT_REGION)
const regions = ref<RegionInfo[]>([])
const historySessions = ref<SessionListItem[]>([])
const historyTotal = ref(0)
const loadingSessions = ref(false)
const creating = ref(false)
const deletingId = ref<string | null>(null)

onMounted(async () => {
  await loadHistory()
  try {
    const data = await listRegions()
    regions.value = data.regions
  } catch {
    /* 后端不可用时前端兜底 */
  }
})

async function loadHistory() {
  loadingSessions.value = true
  try {
    const data = await listSessions(20, 0)
    historySessions.value = data.sessions
    historyTotal.value = data.total
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载历史会话失败')
  } finally {
    loadingSessions.value = false
  }
}

async function handleStart() {
  if (!selectedType.value) {
    message.warning('请先选择案件类型')
    return
  }
  creating.value = true
  try {
    const session = await createSession({
      case_type: selectedType.value,
      region: selectedRegion.value,
    })
    router.push({ path: `/chat/${session.id}`, query: { entry: 'new' } })
  } catch (error) {
    message.error(error instanceof Error ? error.message : '创建会话失败')
  } finally {
    creating.value = false
  }
}

async function handleDelete(id: string) {
  deletingId.value = id
  try {
    await deleteSession(id)
    message.success('会话已删除')
    await loadHistory()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '删除失败')
  } finally {
    deletingId.value = null
  }
}

function handleSelect(id: string) {
  router.push(`/chat/${id}`)
}

function handleNewSession() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
  selectedType.value = ''
}
</script>

<template>
  <div class="home-page page-container">
    <div class="home-grid">
      <aside class="side-panel glass-card fade-in">
        <div class="panel-title">历史咨询</div>
        <SessionHistoryPanel
          :sessions="historySessions"
          :loading="loadingSessions"
          :show-new-entry="true"
          @select="handleSelect"
          @delete="handleDelete"
          @new-session="handleNewSession"
        />
        <div v-if="historyTotal > 0" class="panel-footer">
          <span>共 {{ historyTotal }} 个会话</span>
        </div>
      </aside>

      <section class="main-panel fade-in">
        <div class="hero">
          <div class="hero-icon">⚖️</div>
          <h1>用 AI 维护劳动者的合法权益</h1>
          <p class="hero-sub">
            多轮对话收集案情，智能生成规范法律文书；复杂案件自动分诊，推荐专业律师接单
          </p>
        </div>

        <div class="region-picker">
          <span class="region-label">📍 案件地区</span>
          <n-select
            v-model:value="selectedRegion"
            :options="regions.map((r) => ({ label: `${r.name} · ${r.institution}`, value: r.key }))"
            placeholder="选择地区（文书模板将按地区适配）"
            style="max-width: 420px"
          />
        </div>

        <div class="case-grid">
          <div
            v-for="item in CASE_TYPES"
            :key="item.key"
            class="case-card glass-card"
            :class="{ selected: selectedType === item.key }"
            @click="selectedType = item.key"
          >
            <div class="case-icon">{{ item.icon }}</div>
            <div class="case-name">{{ item.name }}</div>
            <div class="case-desc">{{ item.desc }}</div>
            <div v-if="selectedType === item.key" class="case-check">✓</div>
          </div>
        </div>

        <div class="start-area">
          <n-button
            type="primary"
            size="large"
            class="start-button"
            :loading="creating"
            :disabled="!selectedType"
            @click="handleStart"
          >
            {{ selectedType ? '开始咨询' : '请选择案件类型' }}
          </n-button>
          <span v-if="!auth.isLoggedIn" class="login-hint">
            <n-button text type="primary" @click="router.push('/login')">登录</n-button>
            后历史记录将绑定到您的账号
          </span>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1200px;
}
.home-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
}
@media (max-width: 1024px) {
  .home-grid {
    grid-template-columns: 1fr;
  }
  .side-panel {
    max-height: 300px;
    overflow-y: auto;
  }
}
.side-panel {
  padding: 14px;
  align-self: start;
  position: sticky;
  top: calc(var(--navbar-height) + 24px);
}
@media (max-width: 1024px) {
  .side-panel {
    position: static;
  }
}
.panel-title {
  font-size: 14px;
  font-weight: 700;
  padding: 4px 8px 10px;
}
.panel-footer {
  padding: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
  text-align: center;
}
.main-panel {
  min-width: 0;
}
.hero {
  text-align: center;
  padding: 32px 0 20px;
}
.hero-icon {
  font-size: 52px;
}
.hero h1 {
  margin: 10px 0 6px;
  font-size: 28px;
  font-weight: 800;
}
.hero-sub {
  margin: 0 auto;
  font-size: 14px;
  color: var(--text-secondary);
  max-width: 520px;
}
.region-picker {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  margin: 20px 0 24px;
}
.region-label {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}
.case-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}
.case-card {
  position: relative;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 1.5px solid transparent;
}
.case-card:hover {
  transform: translateY(-2px);
}
.case-card.selected {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.08);
}
.case-icon {
  font-size: 30px;
}
.case-name {
  margin-top: 8px;
  font-size: 15px;
  font-weight: 700;
}
.case-desc {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}
.case-check {
  position: absolute;
  top: 10px;
  right: 12px;
  color: var(--color-primary);
  font-size: 18px;
  font-weight: 700;
}
.start-area {
  margin-top: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.start-button {
  min-width: 220px;
  border-radius: 999px;
}
.login-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
