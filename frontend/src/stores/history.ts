import { defineStore } from 'pinia'
import { ref } from 'vue'
import { deleteSession as apiDeleteSession, listSessions } from '@/services/chatService'
import type { SessionListItem } from '@/services/chatService'

export const useHistoryStore = defineStore('history', () => {
  const sessions = ref<SessionListItem[]>([])
  const total = ref(0)
  const loading = ref(false)
  const activeId = ref<string | null>(null)

  async function load() {
    loading.value = true
    try {
      const data = await listSessions(50, 0)
      sessions.value = data.sessions
      total.value = data.total
    } catch {
      /* ignore */
    } finally {
      loading.value = false
    }
  }

  async function remove(id: string) {
    await apiDeleteSession(id)
    sessions.value = sessions.value.filter((s) => s.id !== id)
    total.value = Math.max(0, total.value - 1)
  }

  function setActive(id: string | null) {
    activeId.value = id
  }

  return { sessions, total, loading, activeId, load, remove, setActive }
})
