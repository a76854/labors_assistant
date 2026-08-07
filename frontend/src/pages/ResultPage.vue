<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NDescriptions, NDescriptionsItem, NEmpty, NSpin, NTag, useMessage } from 'naive-ui'
import { exportDocument, getDocument } from '@/services/documentService'
import type { DocumentResponse } from '@/services/documentService'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const doc = ref<DocumentResponse | null>(null)
const loading = ref(true)
const exporting = ref(false)
const notFound = ref(false)

const docId = String(route.params.docId)

const statusMap: Record<string, { label: string; type: 'info' | 'success' | 'error' | 'warning' | 'default' }> = {
  pending: { label: '生成中', type: 'warning' },
  generated: { label: '已生成', type: 'success' },
  exported: { label: '已导出', type: 'info' },
  failed: { label: '生成失败', type: 'error' },
}

onMounted(async () => {
  await loadDoc()
})

async function loadDoc() {
  loading.value = true
  try {
    doc.value = await getDocument(docId)
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

function formatSize(size?: number | null): string {
  if (!size) return '-'
  if (size < 1024) return `${size} B`
  return `${(size / 1024).toFixed(1)} KB`
}

function formatTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

async function handleExport() {
  if (!doc.value) return
  exporting.value = true
  try {
    const data = await exportDocument(doc.value.id)
    const link = document.createElement('a')
    link.href = data.download_url
    link.download = data.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    message.success('开始下载')
    await loadDoc()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '导出失败')
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="result-page page-container">
    <n-spin :show="loading">
      <n-empty v-if="notFound" description="文档不存在" style="margin-top: 100px">
        <template #extra>
          <n-button type="primary" @click="router.push('/')">返回首页</n-button>
        </template>
      </n-empty>

      <div v-else-if="doc" class="result-card glass-card fade-in">
        <header class="result-header">
          <div class="result-title">
            <span class="doc-icon"><AppIcon name="document" :size="14" /></span>
            <div>
              <h2>{{ doc.title || '法律文书' }}</h2>
              <n-tag :bordered="false" :type="(statusMap[doc.status]?.type as any) || 'default'" size="small">
                {{ statusMap[doc.status]?.label || doc.status }}
              </n-tag>
            </div>
          </div>
          <n-button size="small" quaternary @click="router.push(`/chat/${doc.session_id}`)">
            ← 返回聊天
          </n-button>
        </header>

        <n-descriptions bordered size="small" :column="2" class="doc-meta">
          <n-descriptions-item label="文档 ID">{{ doc.id.slice(0, 8) }}…</n-descriptions-item>
          <n-descriptions-item label="模板">
            {{ doc.template_id }}
          </n-descriptions-item>
          <n-descriptions-item label="创建时间">{{ formatTime(doc.created_at) }}</n-descriptions-item>
          <n-descriptions-item label="文件大小">{{ formatSize(doc.file_size) }}</n-descriptions-item>
        </n-descriptions>

        <div class="doc-content">
          <div v-if="doc.status === 'pending'" class="doc-loading">
            <div class="mock-shimmer"></div>
            <div class="mock-shimmer short"></div>
            <div class="mock-shimmer"></div>
            <div class="mock-shimmer medium"></div>
          </div>
          <template v-else-if="doc.content">
            <MarkdownRenderer :content="doc.content" />
          </template>
          <n-empty v-else size="small" description="文档内容暂不可预览" />
        </div>

        <footer class="result-footer">
          <n-button
            type="primary"
            size="large"
            :loading="exporting"
            :disabled="doc.status === 'pending' || doc.status === 'failed'"
            @click="handleExport"
          >
            ⬇️ 下载诉状（Word）
          </n-button>
        </footer>
      </div>
    </n-spin>
  </div>
</template>

<style scoped>
.result-page {
  max-width: 860px;
}
.result-card {
  padding: 28px;
}
.result-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}
.result-title {
  display: flex;
  align-items: center;
  gap: 14px;
}
.doc-icon {
  font-size: 36px;
}
.result-title h2 {
  margin: 0 0 4px;
  font-size: 20px;
}
.doc-meta {
  margin-bottom: 20px;
}
.doc-content {
  min-height: 200px;
  padding: 20px;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
}
.doc-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.mock-shimmer {
  height: 16px;
  border-radius: 6px;
  background: linear-gradient(90deg, rgba(128, 128, 128, 0.1) 25%, rgba(128, 128, 128, 0.22) 50%, rgba(128, 128, 128, 0.1) 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}
.mock-shimmer.short {
  width: 60%;
}
.mock-shimmer.medium {
  width: 80%;
}
@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
.result-footer {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
@media print {
  .result-card {
    box-shadow: none;
    border: none;
  }
  .result-header,
  .result-footer,
  .doc-meta {
    display: none;
  }
}
</style>
