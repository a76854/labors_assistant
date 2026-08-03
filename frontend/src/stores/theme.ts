import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const stored = localStorage.getItem('app-theme')
  const theme = ref<'dark' | 'light'>(stored === 'light' ? 'light' : 'dark')

  const appliedTheme = computed(() => (theme.value === 'dark' ? 'dark' : 'light'))

  function init() {
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    document.documentElement.setAttribute('data-theme', theme.value)
    localStorage.setItem('app-theme', theme.value)
  }

  return { theme, appliedTheme, init, toggle }
})
