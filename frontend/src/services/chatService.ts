/**
 * 会话 / 消息 API + Agent SSE 流式聊天
 */
import { del, get, post } from './request'

export interface SessionResponse {
  id: string
  case_type: string
  region?: string | null
  status: string
  description?: string | null
  created_at: string
  updated_at: string
}

export interface SessionListItem {
  id: string
  case_type: string
  region?: string | null
  status: string
  description?: string | null
  created_at: string
  updated_at: string
  message_count: number
  last_message_preview?: string | null
  last_message_role?: string | null
  last_message_at?: string | null
}

export interface SessionListResponse {
  sessions: SessionListItem[]
  total: number
}

export interface MessageResponse {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface ChatHistoryResponse {
  session_id: string
  messages: MessageResponse[]
  total: number
}

export interface DocumentReadinessResponse {
  ready: boolean
  missing_fields: string[]
  collected_fields: Record<string, string>
}

export function createSession(data: {
  case_type: string
  region?: string
  description?: string
}): Promise<SessionResponse> {
  return post<SessionResponse>('/api/v1/sessions', data)
}

export function listSessions(limit = 20, offset = 0): Promise<SessionListResponse> {
  return get<SessionListResponse>('/api/v1/sessions', { limit, offset })
}

export function deleteSession(sessionId: string): Promise<void> {
  return del<void>(`/api/v1/sessions/${sessionId}`)
}

export function getSession(sessionId: string): Promise<SessionResponse> {
  return get<SessionResponse>(`/api/v1/sessions/${sessionId}`)
}

export function getMessages(sessionId: string, limit = 100, offset = 0): Promise<ChatHistoryResponse> {
  return get<ChatHistoryResponse>(`/api/v1/sessions/${sessionId}/messages`, { limit, offset })
}

export function syncMessages(
  sessionId: string,
  messages: Array<Pick<MessageResponse, 'role' | 'content'>>,
): Promise<void> {
  return post<void>(`/api/v1/sessions/${sessionId}/messages/sync`, { messages })
}

export function getDocumentReadiness(sessionId: string): Promise<DocumentReadinessResponse> {
  return get<DocumentReadinessResponse>(`/api/v1/sessions/${sessionId}/document-readiness`)
}

// ============================================================================
// Agent SSE 流式聊天
// ============================================================================

function getAgentBaseUrl(): string {
  if (import.meta.env.VITE_AGENT_BASE_URL) {
    return import.meta.env.VITE_AGENT_BASE_URL as string
  }
  if (typeof window !== 'undefined' && window.location?.hostname) {
    return `${window.location.protocol}//${window.location.hostname}:8001`
  }
  return 'http://127.0.0.1:8001'
}

const AGENT_BASE_URL = getAgentBaseUrl()
const AGENT_CHAT_PATH = import.meta.env.VITE_AGENT_CHAT_PATH || '/chat'

interface StreamEventPayload {
  type?: string
  content?: string
  tool_name?: string
  message?: string
}

export interface StreamChatHandlers {
  onToken?: (token: string) => void
  onToolStart?: (toolName: string) => void
  onToolEnd?: (toolName: string) => void
  onDone?: () => void
  onError?: (message: string) => void
}

function parseSseDataBlock(block: string): StreamEventPayload | null {
  if (!block) return null
  const lines = block
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
  const dataLines = lines
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trim())
  if (dataLines.length === 0) return null
  try {
    return JSON.parse(dataLines.join('')) as StreamEventPayload
  } catch {
    return null
  }
}

export async function streamChat(
  threadId: string,
  userInput: string,
  handlers: StreamChatHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${AGENT_BASE_URL}${AGENT_CHAT_PATH}`, {
    method: 'POST',
    signal,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput, thread_id: threadId }),
  })

  if (!response.ok) {
    const detail = await response.text().catch(() => '')
    throw new Error(detail || `请求失败，状态码：${response.status}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('流式响应不可用：response.body 为空')
  }

  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    if (!value) continue

    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() ?? ''

    for (const block of blocks) {
      const payload = parseSseDataBlock(block)
      if (!payload?.type) continue
      if (payload.type === 'token' && payload.content) {
        handlers.onToken?.(payload.content)
      } else if (payload.type === 'tool_start') {
        handlers.onToolStart?.(payload.tool_name || 'unknown_tool')
      } else if (payload.type === 'tool_end') {
        handlers.onToolEnd?.(payload.tool_name || 'unknown_tool')
      } else if (payload.type === 'error') {
        handlers.onError?.(payload.message || '流式响应出错')
      } else if (payload.type === 'done') {
        handlers.onDone?.()
      }
    }
  }

  handlers.onDone?.()
}
