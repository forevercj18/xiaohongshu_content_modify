import api from './index'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user_info: {
    id: number
    username: string
    email?: string
    role: string
    permissions?: Record<string, any>
  }
}

export interface UserInfo {
  id: number
  username: string
  email?: string
  role: string
  permissions?: Record<string, any>
}

export const login = (data: LoginRequest): Promise<LoginResponse> => {
  return api.post('/auth/login', data)
}

export const getProfile = (): Promise<UserInfo> => {
  return api.get('/auth/profile')
}

export const logout = (): Promise<{ message: string }> => {
  return api.post('/auth/logout')
}