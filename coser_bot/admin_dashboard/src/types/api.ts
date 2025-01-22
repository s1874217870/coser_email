/**
 * API响应类型定义
 */

/** API通用响应格式 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

/** 管理员角色类型 */
export type AdminRole = 'superadmin' | 'moderator' | 'viewer';

/** 管理员用户信息 */
export interface AdminUser {
  id: number;
  username: string;
  role: AdminRole;
  is_active: boolean;
}

/** 登录响应 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/** 用户信息 */
export interface User {
  id: number;
  telegram_id: string;
  email: string | null;
  status: number;
  points: number;
  created_at: string;
  updated_at: string;
}

/** 分页响应 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}
