<script setup lang="ts">
import { computed } from 'vue'
import { NConfigProvider, NMessageProvider, NDialogProvider, darkTheme, zhCN } from 'naive-ui'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
themeStore.init()

const theme = computed(() => (themeStore.theme === 'dark' ? darkTheme : null))

const themeOverrides = computed(() => ({
  common: {
    primaryColor: themeStore.theme === 'dark' ? '#3b82f6' : '#1e40af',
    primaryColorHover: themeStore.theme === 'dark' ? '#60a5fa' : '#1d4ed8',
    primaryColorPressed: themeStore.theme === 'dark' ? '#2563eb' : '#1e3a8a',
    primaryColorSuppl: themeStore.theme === 'dark' ? '#3b82f6' : '#1e40af',
    borderRadius: '8px',
    borderRadiusSmall: '4px',
    fontFamily: 'var(--font-sans)',
    fontWeightStrong: '600',
    bodyColor: 'var(--bg-base)',
    cardColor: 'var(--bg-surface)',
    modalColor: 'var(--bg-surface)',
    popoverColor: 'var(--bg-surface)',
    dividerColor: 'var(--border-color)',
    textColorBase: 'var(--text-primary)',
    textColor1: 'var(--text-primary)',
    textColor2: 'var(--text-secondary)',
    textColor3: 'var(--text-tertiary)',
    borderColor: 'var(--border-color)',
    successColor: '#10b981',
    warningColor: '#f59e0b',
    errorColor: '#ef4444',
    infoColor: '#0ea5e9',
  },
}))
</script>

<template>
  <n-config-provider :theme="theme" :theme-overrides="themeOverrides" :locale="zhCN">
    <n-message-provider>
      <n-dialog-provider>
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>
