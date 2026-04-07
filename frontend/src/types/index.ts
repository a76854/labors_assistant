/**
 * 全局 TypeScript 类型定义
 */

export type CaseType = 'wage_arrears' | 'labor_contract' | 'work_injury';

export interface SessionCreateRequest {
  case_type: CaseType;
  description?: string;
}

export interface SessionResponse {
  id: string;
  case_type: string;
  status: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface MessageCreateRequest {
  content: string;
}

export interface MessageResponse {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: MessageResponse[];
  total: number;
}

export type DocumentStatus = 'pending' | 'generated' | 'exported' | 'failed';

export interface DocumentGenerateRequest {
  template_id: string;
  format: 'docx' | 'pdf';
}

export interface DocumentResponse {
  id: string;
  session_id: string;
  template_id: string;
  title: string;
  status: DocumentStatus;
  content: string;
  file_url?: string;
  file_size?: number;
  created_at: string;
  updated_at: string;
}

