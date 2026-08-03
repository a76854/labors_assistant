/**
 * 超级管理员 API
 */
import { get } from './request'

export interface AdminStats {
  total_users: number
  total_lawyers: number
  total_workers: number
  total_sessions: number
  total_leads: number
  open_leads: number
  claimed_leads: number
  completed_leads: number
  total_documents: number
  generated_documents: number
}

export interface AdminUser {
  id: string
  username: string
  role: string
  name?: string | null
  phone?: string | null
  specialty?: string[] | null
  region?: string | null
  created_at: string
  session_count: number
  lead_count: number
}

export interface AdminLead {
  id: string
  session_id: string
  status: string
  case_type: string
  region?: string | null
  evidence_score?: number | null
  risk_score?: number | null
  complexity?: string | null
  missing_evidence: string[]
  summary?: string | null
  created_at: string
  updated_at: string
  user_username?: string | null
  lawyer_username?: string | null
}

export interface AdminSession {
  id: string
  case_type: string
  region?: string | null
  status: string
  user_username?: string | null
  message_count: number
  created_at: string
  updated_at: string
}

export function getAdminStats(): Promise<AdminStats> {
  return get<AdminStats>('/api/v1/admin/stats')
}

export function getAdminUsers(role?: string, limit = 100, offset = 0): Promise<{ users: AdminUser[]; total: number }> {
  return get<{ users: AdminUser[]; total: number }>('/api/v1/admin/users', { role, limit, offset })
}

export function getAdminLeads(status?: string, limit = 100, offset = 0): Promise<{ leads: AdminLead[]; total: number }> {
  return get<{ leads: AdminLead[]; total: number }>('/api/v1/admin/leads', { status_filter: status, limit, offset })
}

export function getAdminSessions(limit = 100, offset = 0): Promise<{ sessions: AdminSession[]; total: number }> {
  return get<{ sessions: AdminSession[]; total: number }>('/api/v1/admin/sessions', { limit, offset })
}
