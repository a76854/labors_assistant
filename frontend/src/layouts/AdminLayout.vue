<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const themeStore = useThemeStore()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="admin-layout">
    <aside class="admin-sidebar glass-card">
      <div class="sidebar-brand">
        <span class="sidebar-logo">🛡️</span>
        <div>
          <div class="sidebar-title">平台管理后台</div>
          <div class="sidebar-sub">超级管理员</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/admin/overview') }"
          @click="router.push('/admin/overview')"
        >
          📊 数据概览
        </div>
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/admin/users') }"
          @click="router.push('/admin/users')"
        >
          👥 用户管理
        </div>
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/admin/leads') }"
          @click="router.push('/admin/leads')"
        >
          📥 线索管理
        </div>
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/admin/sessions') }"
          @click="router.push('/admin/sessions')"
        >
          💬 会话记录
        </div>
      </nav>
      <div class="sidebar-footer">
        <n-button size="small" quaternary block @click="handleLogout">🚪 退出登录</n-button>
      </div>
    </aside>
    <main class="admin-main">
      <header class="admin-toolbar glass-card">
        <span>平台管理后台 · {{ auth.user?.name || auth.user?.username }}</span>
        <n-button quaternary circle @click="themeStore.toggle()">
          {{ themeStore.theme === 'dark' ? '☀️' : '🌙' }}
        </n-button>
      </header>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 230px 1fr;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px;
}
@media (max-width: 900px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }
}
.admin-sidebar {
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
  display: flex;
  flex-direction: column;
  gap: 4px;
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
.admin-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  margin-bottom: 16px;
  font-weight: 700;
  border-radius: 12px;
}
.admin-main {
  min-width: 0;
}
</style>
