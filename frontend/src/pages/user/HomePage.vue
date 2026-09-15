<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSelect, useMessage } from 'naive-ui'
import { CASE_TYPES, DEFAULT_REGION } from '@/constants'
import { createSession } from '@/services/chatService'
import { listRegions } from '@/services/lawyerService'
import type { RegionInfo } from '@/services/lawyerService'
import CaseTypeIcon from '@/components/CaseTypeIcon.vue'
import { useAuthStore } from '@/stores/auth'
import { useHistoryStore } from '@/stores/history'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()
const historyStore = useHistoryStore()

const selectedType = ref<string>('')
const selectedRegion = ref<string>(DEFAULT_REGION)
const regions = ref<RegionInfo[]>([])
const creating = ref(false)

onMounted(async () => {
  if (auth.isLoggedIn) {
    historyStore.load()
  }
  try {
    const data = await listRegions()
    regions.value = data.regions
  } catch {
    /* 后端不可用时前端兜底 */
  }
})

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
</script>

<template>
  <div class="home-page page-container fade-in">
    <section class="main-panel">
      <div class="hero">
        <h1>劳动者维权 AI 助手</h1>
        <p class="hero-sub">
          多轮对话收集案情，智能生成法律文书；复杂案件自动分诊评分，推荐本地专业律师接单。
        </p>
      </div>

      <div class="stat-strip">
        <div class="stat-strip-item">
          <div class="stat-strip-icon"><AppIcon name="locate" :size="18" /></div>
          <div>
            <div class="stat-strip-value">3+</div>
            <div class="stat-strip-label">服务地区</div>
          </div>
        </div>
        <div class="stat-strip-item">
          <div class="stat-strip-icon"><AppIcon name="scale" :size="18" /></div>
          <div>
            <div class="stat-strip-value">10+</div>
            <div class="stat-strip-label">入驻律师</div>
          </div>
        </div>
        <div class="stat-strip-item">
          <div class="stat-strip-icon"><AppIcon name="list" :size="18" /></div>
          <div>
            <div class="stat-strip-value">4</div>
            <div class="stat-strip-label">案件类型</div>
          </div>
        </div>
        <div class="stat-strip-item">
          <div class="stat-strip-icon"><AppIcon name="shield" :size="18" /></div>
          <div>
            <div class="stat-strip-value">规则启发</div>
            <div class="stat-strip-label">分诊评分</div>
          </div>
        </div>
      </div>

      <div class="region-picker">
        <span class="region-label"><AppIcon name="locate" :size="14" />案件地区</span>
        <n-select
          v-model:value="selectedRegion"
          :options="regions.map((r) => ({ label: `${r.name} · ${r.institution}`, value: r.key }))"
          placeholder="选择地区（文书模板将按地区适配）"
          style="flex: 1; max-width: 480px"
        />
      </div>

      <div class="case-grid">
        <div
          v-for="item in CASE_TYPES"
          :key="item.key"
          class="case-card"
          :class="{ selected: selectedType === item.key }"
          @click="selectedType = item.key"
        >
          <div class="case-icon"><CaseTypeIcon :type="item.key" :size="22" /></div>
          <div class="case-name">{{ item.name }}</div>
          <div class="case-desc">{{ item.desc }}</div>
          <div v-if="selectedType === item.key" class="case-check">
            <AppIcon name="check" :size="11" />
          </div>
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
</template>

<style scoped>
.home-page {
  max-width: 1000px;
}
.main-panel {
  min-width: 0;
}
.hero {
  padding: 8px 0 4px;
}
.hero h1 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--text-primary);
}
.hero-sub {
  margin: 0;
  font-size: 13.5px;
  color: var(--text-secondary);
  max-width: 560px;
  line-height: 1.7;
}
.stat-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin: 18px 0 4px;
}
.stat-strip-item {
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  display: flex;
  align-items: center;
  gap: 8px;
}
.stat-strip-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  border-radius: var(--radius-sm);
}
.stat-strip-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}
.stat-strip-label {
  font-size: 11.5px;
  color: var(--text-tertiary);
  margin-top: 2px;
}
@media (max-width: 768px) {
  .stat-strip {
    grid-template-columns: repeat(2, 1fr);
  }
}
.region-picker {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 18px 0 14px;
  padding: 12px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
}
.region-label {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;
}
.case-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}
.case-card {
  position: relative;
  padding: 16px;
  text-align: left;
  cursor: pointer;
  background: var(--bg-surface);
  border: 1.5px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.case-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-sm);
}
.case-card.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
}
.case-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-soft);
  color: var(--color-primary);
  margin-bottom: 10px;
}
.case-card.selected .case-icon {
  background: var(--color-primary);
  color: var(--text-inverse);
}
.case-name {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}
.case-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.5;
}
.case-check {
  position: absolute;
  top: 10px;
  right: 10px;
  color: var(--color-primary);
  font-weight: 700;
  font-size: 12px;
  background: var(--bg-surface);
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1.5px solid var(--color-primary);
}
.start-area {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.start-button {
  min-width: 220px;
  height: 40px;
  font-weight: 500;
}
.login-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
