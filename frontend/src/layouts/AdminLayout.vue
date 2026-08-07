<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import AppIcon from '@/components/AppIcon.vue'

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
    <aside class="admin-sidebar">
      <div class="sidebar-brand">
        <div class="brand-mark">
          <AppIcon name="shield" :size="20" />
        </div>
        <div class="brand-text">
          <div class="brand-title">平台管理后台</div>
          <div class="brand-sub">超级管理员</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/admin/overview') }"
          @click="router.push('/admin/overview')"
        >
          <AppIcon name="stats" :size="14" />
          <span>数据概览</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/admin/users') }"
          @click="router.push('/admin/users')"
        >
          <AppIcon name="person-circle" :size="14" />
          <span>用户管理</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/admin/leads') }"
          @click="router.push('/admin/leads')"
        >
          <AppIcon name="file" :size="14" />
          <span>线索管理</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/admin/sessions') }"
          @click="router.push('/admin/sessions')"
        >
          <AppIcon name="chat" :size="14" />
          <span>会话记录</span>
        </div>
      </nav>

      <div class="sidebar-footer">
        <button class="logout-btn" @click="handleLogout">
          <AppIcon name="logout" :size="12" />
          <span>退出登录</span>
        </button>
      </div>
    </aside>

    <main class="admin-main">
      <header class="admin-toolbar">
        <span class="toolbar-title">平台管理 · {{ auth.user?.name || auth.user?.username }}</span>
        <button class="icon-button" :title="themeStore.theme === 'dark' ? '切换浅色' : '切换深色'" @click="themeStore.toggle()">
          <AppIcon :name="themeStore.theme === 'dark' ? 'sun' : 'moon'" :size="18" />
        </button>
      </header>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
  background: var(--bg-base);
}
@media (max-width: 900px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }
}
.admin-sidebar {
  background: var(--bg-surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}
@media (max-width: 900px) {
  .admin-sidebar {
    position: static;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--border-color);
  }
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px 16px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 12px;
}
.brand-mark {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--color-danger);
  color: var(--text-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
  min-width: 0;
}
.brand-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}
.brand-sub {
  font-size: 11.5px;
  color: var(--text-tertiary);
}
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  position: relative;
  transition: all var(--transition-fast);
  user-select: none;
}
.nav-item:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}
.nav-item.active {
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: 600;
}
.nav-item.active::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 6px;
  bottom: 6px;
  width: 3px;
  background: var(--color-primary);
  border-radius: 0 3px 3px 0;
}
.sidebar-footer {
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
}
.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: 0;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  font-size: 13px;
  transition: all var(--transition-fast);
}
.logout-btn:hover {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}
.admin-main {
  min-width: 0;
  padding: 20px 28px 40px;
  max-width: calc(1200px - var(--sidebar-width));
}
.admin-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px 18px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
}
.toolbar-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.3px;
}
.icon-button {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 0;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}
.icon-button:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}
</style>
