/**
 * 聊天相关 API 服务
 * - 会话创建、获取
 * - 消息发送、历史查询
 */
import { get, post } from './request';
import type {
  SessionCreateRequest,
  SessionResponse,
  MessageCreateRequest,
  MessageResponse,
  ChatHistoryResponse,
} from '../types';

/** 创建新会话 */
export async function createSession(data: SessionCreateRequest): Promise<SessionResponse> {
  return post<SessionResponse>('/api/v1/sessions', data);
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
