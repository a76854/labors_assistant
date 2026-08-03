<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const props = defineProps<{
  content: string
}>()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  highlight(code: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch {
        /* ignore */
      }
    }
    return ''
  },
})

const rendered = computed(() => md.render(props.content || ''))
</script>

<template>
  <!-- eslint-disable-next-line vue/no-v-html -- markdown-it 已禁用原始 HTML(html: false),仅渲染受信任的 AI 回复文本 -->
  <div class="markdown-body" v-html="rendered"></div>
</template>

<style scoped>
.markdown-body {
  font-size: 14px;
  line-height: 1.75;
  word-break: break-word;
}
.markdown-body :deep(p) {
  margin: 6px 0;
}
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 12px 0 6px;
  font-weight: 600;
}
.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}
.markdown-body :deep(a) {
  color: var(--color-primary);
}
.markdown-body :deep(code) {
  background: rgba(128, 128, 128, 0.12);
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 12.5px;
}
.markdown-body :deep(pre) {
  background: rgba(128, 128, 128, 0.1);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}
.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
}
.markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
}
.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid var(--border-color);
  padding: 6px 10px;
}
.markdown-body :deep(blockquote) {
  border-left: 3px solid var(--color-primary);
  margin: 8px 0;
  padding: 4px 12px;
  color: var(--text-secondary);
  background: rgba(128, 128, 128, 0.06);
}
</style>
