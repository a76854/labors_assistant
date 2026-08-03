/**
 * 文档 API
 */
import { get, post } from './request'

export interface DocumentResponse {
  id: string
  session_id: string
  template_id: string
  title?: string | null
  status: 'pending' | 'generated' | 'exported' | 'failed'
  content?: string | null
  file_url?: string | null
  file_size?: number | null
  created_at: string
  updated_at: string
}

export function generateDocument(
  sessionId: string,
  data: { template_id: string; format?: string },
): Promise<DocumentResponse> {
  return post<DocumentResponse>(`/api/v1/sessions/${sessionId}/generate-document`, data)
}

export function getDocument(docId: string): Promise<DocumentResponse> {
  return get<DocumentResponse>(`/api/v1/documents/${docId}`)
}

export async function exportDocument(docId: string): Promise<{ download_url: string; filename: string }> {
  return get<{ download_url: string; filename: string }>(`/api/v1/documents/${docId}/export`)
}
