<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NDropdown, NIcon } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const auth = useAuthStore()
const themeStore = useThemeStore()

const userOptions = computed(() => {
  const options: Array<{ label: string; key: string }> = [{ label: '退出登录', key: 'logout' }]
  if (auth.isLawyer) {
    options.unshift({ label: '⚖️ 律师工作台', key: 'lawyer' })
  }
  if (auth.isAdmin) {
    options.unshift({ label: '🛡️ 管理后台', key: 'admin' })
  }
  return options
})

function handleUserAction(key: string) {
  if (key === 'logout') {
    auth.logout()
    router.push('/login')
  } else if (key === 'lawyer') {
    router.push('/lawyer/dashboard')
  } else if (key === 'admin') {
    router.push('/admin/overview')
  }
}

function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="main-layout">
    <header class="navbar glass-card">
      <div class="navbar-inner">
        <div class="brand" @click="goHome">
          <span class="brand-icon">⚖️</span>
          <span class="brand-name">劳动维权平台</span>
        </div>
        <div class="navbar-actions">
          <n-button
            quaternary
            circle
            :title="themeStore.theme === 'dark' ? '切换浅色主题' : '切换深色主题'"
            @click="themeStore.toggle()"
          >
            {{ themeStore.theme === 'dark' ? '☀️' : '🌙' }}
          </n-button>
          <template v-if="auth.isLoggedIn">
            <n-dropdown :options="userOptions" trigger="hover" @select="handleUserAction">
              <n-button quaternary size="small" class="user-chip">
                <n-icon>
                  <span>👤</span>
                </n-icon>
                <span class="user-name">{{ auth.user?.username }}</span>
                <span class="user-role-tag" :class="auth.isLawyer ? 'lawyer' : auth.isAdmin ? 'admin' : 'worker'">
                  {{ auth.isLawyer ? '律师' : auth.isAdmin ? '管理员' : '劳动者' }}
                </span>
              </n-button>
            </n-dropdown>
          </template>
          <template v-else>
            <n-button quaternary size="small" @click="router.push('/login')">登录</n-button>
          </template>
        </div>
      </div>
    </header>
    <main class="layout-main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.main-layout {
  min-height: 100vh;
}
.navbar {
  position: sticky;
  top: 12px;
  z-index: 100;
  margin: 12px auto 0;
  width: calc(100% - 32px);
  max-width: 1200px;
  border-radius: 14px;
  padding: 0 18px;
  height: var(--navbar-height);
  display: flex;
  align-items: center;
}
.navbar-inner {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}
.brand-icon {
  font-size: 22px;
}
.brand-name {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.navbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.user-chip {
  display: flex;
  align-items: center;
  gap: 6px;
}
.user-name {
  font-size: 13px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-role-tag {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 999px;
  line-height: 18px;
}
.user-role-tag.lawyer {
  background: rgba(59, 130, 246, 0.18);
  color: #60a5fa;
}
.user-role-tag.admin {
  background: rgba(239, 68, 68, 0.16);
  color: #f87171;
}
.user-role-tag.worker {
  background: rgba(16, 185, 129, 0.16);
  color: #34d399;
}
.layout-main {
  padding-bottom: 40px;
}
</style>
