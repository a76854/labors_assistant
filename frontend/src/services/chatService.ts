/**
 * 聊天相关 API 服务
 * - 会话创建、获取
 * - 消息发送、历史查询
 */
import { del, get, post } from './request';
import { ApiError } from './request';
import type {
  SessionCreateRequest,
  SessionListResponse,
  SessionResponse,
  DocumentReadinessResponse,
  MessageCreateRequest,
  MessageResponse,
  ChatHistoryResponse,
} from '../types';

function getDefaultAgentBaseUrl(port: number): string {
  if (typeof window !== 'undefined' && window.location?.hostname) {
    return `${window.location.protocol}//${window.location.hostname}:${port}`;
  }
  return `http://127.0.0.1:${port}`;
}

const AGENT_BASE_URL: string =
  import.meta.env.VITE_AGENT_BASE_URL || getDefaultAgentBaseUrl(8001);
const AGENT_CHAT_PATH: string =
  import.meta.env.VITE_AGENT_CHAT_PATH || '/chat';

type StreamEventPayload = {
  type?: string;
  content?: string;
  tool_name?: string;
  message?: string;
};

type StreamChatHandlers = {
  onToken?: (token: string) => void;
  onToolStart?: (toolName: string) => void;
  onToolEnd?: (toolName: string) => void;
  onDone?: () => void;
  onError?: (message: string) => void;
};

function parseSseDataBlock(block: string): StreamEventPayload | null {
  if (!block) return null;
  const lines = block
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  const dataLines = lines
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trim());

  if (dataLines.length === 0) return null;

  const rawJson = dataLines.join('');
  if (!rawJson) return null;

  try {
    return JSON.parse(rawJson) as StreamEventPayload;
  } catch {
    return null;
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
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_input: userInput,
      thread_id: threadId,
    }),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new ApiError(response.status, detail || `请求失败，状态码：${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new ApiError(0, '流式响应不可用：response.body 为空');
  }

  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      const tail = decoder.decode();
      if (tail) {
        buffer += tail;
      }
      break;
    }

    if (!value) {
      continue;
    }

    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split('\n\n');
    buffer = blocks.pop() ?? '';

    for (const block of blocks) {
      const payload = parseSseDataBlock(block);
      if (!payload?.type) continue;

      if (payload.type === 'token' && payload.content) {
        handlers.onToken?.(payload.content);
      } else if (payload.type === 'tool_start') {
        handlers.onToolStart?.(payload.tool_name || 'unknown_tool');
      } else if (payload.type === 'tool_end') {
        handlers.onToolEnd?.(payload.tool_name || 'unknown_tool');
      } else if (payload.type === 'error') {
        handlers.onError?.(payload.message || '流式响应出错');
      } else if (payload.type === 'done') {
        handlers.onDone?.();
      }
    }
  }

  if (buffer.trim()) {
    const payload = parseSseDataBlock(buffer.trim());
    if (payload?.type === 'token' && payload.content) {
      handlers.onToken?.(payload.content);
    }
  }

  handlers.onDone?.();
}

/** 创建新会话 */
export async function createSession(data: SessionCreateRequest): Promise<SessionResponse> {
  return post<SessionResponse>('/api/v1/sessions', data);
}

/** 获取历史会话列表 */
export async function listSessions(
  limit?: number,
  offset?: number,
): Promise<SessionListResponse> {
  return get<SessionListResponse>('/api/v1/sessions', {
    params: { limit, offset },
  });
}

/** 删除会话 */
export async function deleteSession(sessionId: string): Promise<void> {
  return del<void>(`/api/v1/sessions/${sessionId}`);
}

/** 获取会话详情 */
export async function getSession(sessionId: string): Promise<SessionResponse> {
  return get<SessionResponse>(`/api/v1/sessions/${sessionId}`);
}

/** 在指定会话中发送消息 */
export async function sendMessage(
  sessionId: string,
  data: MessageCreateRequest
): Promise<MessageResponse> {
  return post<MessageResponse>(`/api/v1/sessions/${sessionId}/messages`, data);
}

/** 获取会话历史记录 */
export async function getMessages(
  sessionId: string,
  limit?: number,
  offset?: number
): Promise<ChatHistoryResponse> {
  return get<ChatHistoryResponse>(`/api/v1/sessions/${sessionId}/messages`, {
    params: { limit, offset },
  });
}

/** 获取会话文书生成就绪状态 */
export async function getDocumentReadiness(
  sessionId: string,
): Promise<DocumentReadinessResponse> {
  return get<DocumentReadinessResponse>(`/api/v1/sessions/${sessionId}/document-readiness`);
}

/** 将前端流式对话消息写回后端数据库 */
export async function syncMessages(
  sessionId: string,
  messages: Array<Pick<MessageResponse, 'role' | 'content'>>,
): Promise<void> {
  return post<void>(`/api/v1/sessions/${sessionId}/messages/sync`, { messages });
}
