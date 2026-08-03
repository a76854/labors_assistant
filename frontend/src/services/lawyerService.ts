/**
 * 案件分诊 / 律师后台 API
 */
import { get, post } from './request'

export interface LawyerProfile {
  id: string
  name: string
  license_no: string
  specialties: string[]
  years: number
  rating: number
  desc: string
}

export interface TriageResponse {
  session_id: string
  case_type: string
  region?: string | null
  evidence_score: number
  evidence_covered: string[]
  missing_evidence: string[]
  risk_score: number
  complexity: 'high' | 'medium' | 'low'
  recommended_lawyers: LawyerProfile[]
}

export interface RegionInfo {
  key: string
  name: string
  institution: string
  note: string
}

export interface MaterialRequest {
  id: string
  items: Array<{ name: string; description?: string; status: string }>
  note?: string | null
  status: string
  created_at: string
}

export interface SessionLeadInfo {
  id: string
  session_id: string
  status: 'open' | 'claimed' | 'completed'
  evidence_score?: number | null
  risk_score?: number | null
  complexity?: string | null
  created_at: string
  lawyer_id?: string | null
  material_requests: MaterialRequest[]
}

export interface LeadListItem {
  id: string
  session_id: string
  status: 'open' | 'claimed' | 'completed'
  case_type: string
  region?: string | null
  evidence_score?: number | null
  risk_score?: number | null
  complexity?: string | null
  missing_evidence: string[]
  summary?: string | null
  created_at: string
  updated_at: string
  material_request_count: number
}

export interface LeadDetail extends LeadListItem {
  user_username?: string | null
  user_phone?: string | null
  messages: Array<{ role: string; content: string }>
  material_requests: MaterialRequest[]
}

export function triageSession(sessionId: string): Promise<TriageResponse> {
  return post<TriageResponse>(`/api/v1/sessions/${sessionId}/triage`, {})
}

export function getSessionLead(sessionId: string): Promise<{ lead: SessionLeadInfo | null }> {
  return get<{ lead: SessionLeadInfo | null }>(`/api/v1/sessions/${sessionId}/lead`)
}

export function listRegions(): Promise<{ regions: RegionInfo[] }> {
  return get<{ regions: RegionInfo[] }>('/api/v1/regions')
}

// ============================================================================
// 律师后台
// ============================================================================

export function listLawyerLeads(
  status?: string,
  limit = 50,
  offset = 0,
): Promise<{ leads: LeadListItem[]; total: number }> {
  return get<{ leads: LeadListItem[]; total: number }>('/api/v1/lawyer/leads', {
    status_filter: status,
    limit,
    offset,
  })
}

export function getLawyerLead(leadId: string): Promise<LeadDetail> {
  return get<LeadDetail>(`/api/v1/lawyer/leads/${leadId}`)
}

export function claimLead(leadId: string): Promise<{ id: string; status: string; message: string }> {
  return post<{ id: string; status: string; message: string }>(`/api/v1/lawyer/leads/${leadId}/claim`, {})
}

export function completeLead(leadId: string): Promise<{ id: string; status: string; message: string }> {
  return post<{ id: string; status: string; message: string }>(`/api/v1/lawyer/leads/${leadId}/complete`, {})
}

export function requestMaterials(
  leadId: string,
  data: { items: Array<{ name: string; description?: string }>; note?: string },
): Promise<MaterialRequest> {
  return post<MaterialRequest>(`/api/v1/lawyer/leads/${leadId}/request-materials`, data)
}
