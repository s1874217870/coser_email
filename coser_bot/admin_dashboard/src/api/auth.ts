/**
 * 认证相关API
 */
import apiClient from './client';
import type { AdminUser, ApiResponse, LoginResponse } from '@/types/api';

export interface LoginRequest {
  username: string;
  password: string;
}

export const authApi = {
  /**
   * 管理员登录
   * @throws {Error} 当登录失败时抛出错误
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    try {
      console.log('准备登录请求:', data);
      const formData = new URLSearchParams();
      formData.append('username', data.username);
      formData.append('password', data.password);
      formData.append('grant_type', 'password');
      
      console.log('请求URL:', apiClient.defaults.baseURL);
      console.log('请求数据:', formData.toString());
      
      const response = await apiClient.post<LoginResponse>('/admin/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        },
        transformRequest: [(data) => data], // 防止axios自动转换数据
        validateStatus: (status) => true, // 允许所有状态码以便调试
      });
      
      console.log('响应状态码:', response.status);
      console.log('响应头:', response.headers);
      console.log('响应数据:', response.data);
      
      if (response.status !== 200) {
        throw new Error(response.data?.message || '登录失败');
      }
      
      return response.data;
    } catch (error) {
      console.error('登录错误:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('登录失败，请稍后重试');
    }
  },

  /**
   * 管理员注销
   * @throws {Error} 当注销失败时抛出错误
   */
  logout: async (): Promise<void> => {
    try {
      const response = await apiClient.post<ApiResponse<void>>('/admin/logout');
      if (response.data.code !== 0) {
        throw new Error(response.data.message);
      }
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('注销失败，请稍后重试');
    }
  },

  /**
   * 获取当前管理员信息
   * @throws {Error} 当获取信息失败时抛出错误
   */
  getProfile: async (): Promise<AdminUser> => {
    try {
      const response = await apiClient.get<ApiResponse<AdminUser>>('/admin/me');
      if (response.data.code !== 0) {
        throw new Error(response.data.message);
      }
      return response.data.data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('获取用户信息失败，请稍后重试');
    }
  },
};
