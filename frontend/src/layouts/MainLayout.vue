<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useHistoryStore } from '@/stores/history'
import AppIcon from '@/components/AppIcon.vue'
import SessionHistoryPanel from '@/components/SessionHistoryPanel.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const themeStore = useThemeStore()
const historyStore = useHistoryStore()

const isOnHome = computed(() => route.path === '/')

onMounted(() => {
  if (auth.isLoggedIn) {
    historyStore.load()
  }
  historyStore.setActive(route.params.sessionId as string | null)
})
</script>

<template>
  <div class="app-shell">
    <aside class="app-sidebar">
      <div class="sidebar-brand" @click="router.push('/')">
        <div class="brand-mark">
          <AppIcon name="scale" :size="18" />
        </div>
        <div class="brand-text">
          <div class="brand-name">劳动者维权</div>
          <div class="brand-sub">AI 法律助手</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div
          class="nav-item"
          :class="{ active: route.path === '/' }"
          @click="router.push('/')"
        >
          <AppIcon name="home" :size="14" />
          <span>首页</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: route.path.startsWith('/chat') || route.path.startsWith('/result') }"
          @click="auth.isLoggedIn ? router.push('/') : router.push('/login')"
        >
          <AppIcon name="chat" :size="14" />
          <span>咨询</span>
        </div>
        <div v-if="auth.isLawyer" class="nav-item" @click="router.push('/lawyer/dashboard')">
          <AppIcon name="scale" :size="14" />
          <span>律师工作台</span>
        </div>
        <div v-if="auth.isAdmin" class="nav-item" @click="router.push('/admin/overview')">
          <AppIcon name="shield" :size="14" />
          <span>管理后台</span>
        </div>
      </nav>

      <div class="sidebar-history">
        <div class="history-label">历史会话</div>
        <div class="history-list">
          <SessionHistoryPanel />
        </div>
      </div>

      <div class="sidebar-footer">
        <template v-if="auth.isLoggedIn">
          <div class="user-info">
            <div class="user-avatar">
              <AppIcon name="person" :size="14" />
            </div>
            <div class="user-meta">
              <div class="user-name">{{ auth.user?.username }}</div>
              <div class="user-role">{{ auth.isLawyer ? '律师' : auth.isAdmin ? '管理员' : '劳动者' }}</div>
            </div>
          </div>
          <button
            v-if="!isOnHome"
            class="footer-button"
            @click="router.push('/')"
          >
            <AppIcon name="home" :size="14" />
            <span>返回首页</span>
          </button>
          <button class="footer-button footer-button-danger" @click="auth.logout(); router.push('/login')">
            <AppIcon name="logout" :size="14" />
            <span>退出登录</span>
          </button>
        </template>
        <template v-else>
          <n-button type="primary" block size="small" @click="router.push('/login')">登录 / 注册</n-button>
        </template>
      </div>
    </aside>

    <main class="app-main">
      <header class="app-topbar">
        <div class="topbar-title">
          <span v-if="route.path === '/'">首页</span>
          <span v-else-if="route.path.startsWith('/chat')">咨询对话</span>
          <span v-else-if="route.path.startsWith('/result')">文书结果</span>
        </div>
        <div class="topbar-actions">
          <button
            class="topbar-icon-button"
            :title="themeStore.theme === 'dark' ? '切换浅色' : '切换深色'"
            @click="themeStore.toggle()"
          >
            <AppIcon :name="themeStore.theme === 'dark' ? 'sun' : 'moon'" :size="16" />
          </button>
        </div>
      </header>
      <div class="app-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 220px 1fr;
  min-height: 100vh;
  background: var(--bg-base);
}
@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: 1fr;
  }
}
.app-sidebar {
  background: var(--bg-surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}
@media (max-width: 900px) {
  .app-sidebar {
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
  padding: 14px 14px 12px;
  border-bottom: 1px solid var(--border-subtle);
  cursor: pointer;
  user-select: none;
}
.brand-mark {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: var(--text-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
  min-width: 0;
}
.brand-name {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
}
.brand-sub {
  font-size: 11px;
  color: var(--text-tertiary);
}
.sidebar-nav {
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 1px;
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
  transition: all var(--transition-fast);
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
.sidebar-history {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 4px 10px 8px;
  border-top: 1px solid var(--border-subtle);
  margin-top: 8px;
}
.history-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  letter-spacing: 0.3px;
  text-transform: uppercase;
  padding: 8px 6px 6px;
}
.history-list {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 4px;
}
.sidebar-footer {
  padding: 10px 10px 12px;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px 8px;
}
.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.user-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}
.user-name {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-role {
  font-size: 11px;
  color: var(--text-tertiary);
}
.footer-button {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 5px 10px;
  background: transparent;
  border: 0;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  font-size: 12.5px;
  text-align: left;
  transition: all var(--transition-fast);
}
.footer-button:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}
.footer-button-danger:hover {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}
.app-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 100vh;
}
.app-topbar {
  display: none;
  position: sticky;
  top: 0;
  z-index: 50;
  height: 48px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-color);
  padding: 0 16px;
  align-items: center;
  justify-content: space-between;
}
@media (max-width: 900px) {
  .app-topbar {
    display: flex;
  }
}
.topbar-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.topbar-icon-button {
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
.topbar-icon-button:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}
.app-content {
  flex: 1;
  min-width: 0;
}
</style>
