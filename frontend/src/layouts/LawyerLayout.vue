<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const themeStore = useThemeStore()
</script>

<template>
  <div class="lawyer-layout">
    <aside class="lawyer-sidebar glass-card">
      <div class="sidebar-brand">
        <span class="sidebar-logo">⚖️</span>
        <div>
          <div class="sidebar-title">律师工作台</div>
          <div class="sidebar-sub">{{ auth.user?.name || auth.user?.username }}</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/lawyer/leads') }"
          @click="router.push('/lawyer/leads')"
        >
          📥 待接单线索
        </div>
      </nav>
      <div class="sidebar-footer">
        <n-button size="small" quaternary block @click="router.push('/')">← 返回用户端</n-button>
        <n-button size="small" quaternary block @click="router.push('/login')">切换账号</n-button>
      </div>
    </aside>
    <main class="lawyer-main">
      <header class="lawyer-toolbar glass-card">
        <span>律师后台</span>
        <n-button quaternary circle @click="themeStore.toggle()">
          {{ themeStore.theme === 'dark' ? '☀️' : '🌙' }}
        </n-button>
      </header>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.lawyer-layout {
  display: grid;
  grid-template-columns: 230px 1fr;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px;
}
@media (max-width: 900px) {
  .lawyer-layout {
    grid-template-columns: 1fr;
  }
}
.lawyer-sidebar {
  padding: 18px 14px;
  align-self: start;
  position: sticky;
  top: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 120px);
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
}
.sidebar-logo {
  font-size: 28px;
}
.sidebar-title {
  font-weight: 700;
  font-size: 15px;
}
.sidebar-sub {
  font-size: 12px;
  color: var(--text-secondary);
}
.sidebar-nav {
  flex: 1;
}
.nav-item {
  padding: 11px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}
.nav-item:hover {
  background: rgba(128, 128, 128, 0.07);
}
.nav-item.active {
  background: rgba(59, 130, 246, 0.12);
  color: var(--color-primary);
  font-weight: 600;
}
.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.lawyer-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  margin-bottom: 16px;
  font-weight: 700;
  border-radius: 12px;
}
.lawyer-main {
  min-width: 0;
}
</style>
