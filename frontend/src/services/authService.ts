/**
 * 认证 API
 */
import { get, post } from './request'
import type { UserInfo } from '@/stores/auth'

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export interface RegisterPayload {
  username: string
  password: string
  role: 'user' | 'lawyer'
  name?: string
  phone?: string
}

export function register(data: RegisterPayload): Promise<TokenResponse> {
  return post<TokenResponse>('/api/v1/auth/register', data)
}

export function login(username: string, password: string): Promise<TokenResponse> {
  return post<TokenResponse>('/api/v1/auth/login', { username, password })
}

export function fetchMe(): Promise<UserInfo> {
  return get<UserInfo>('/api/v1/auth/me')
}
