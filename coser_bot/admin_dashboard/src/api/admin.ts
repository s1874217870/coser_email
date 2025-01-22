/**
 * 管理后台API
 */
import apiClient from './client';
import type { ApiResponse, User, PaginatedResponse } from '@/types/api';

export const adminApi = {
  /**
   * 获取用户列表
   */
  getUsers: async (): Promise<User[]> => {
    try {
      const response = await apiClient.get<ApiResponse<User[]>>('/admin/users');
      console.log('用户列表响应:', response.data);
      if (!Array.isArray(response.data)) {
        throw new Error('无效的响应格式');
      }
      return response.data;
    } catch (error) {
      console.error('获取用户列表失败:', error);
      throw error;
    }
  },

  /**
   * 封禁用户
   */
  banUser: async (userId: number): Promise<void> => {
    try {
      console.log('发送封禁请求:', userId);
      const response = await apiClient.put<ApiResponse<void>>(`/admin/users/${userId}/ban`);
      console.log('封禁响应:', response.data);
      if (response.status !== 200) {
        throw new Error(response.data?.message || '封禁失败');
      }
    } catch (error) {
      console.error('封禁用户失败:', error);
      throw error;
    }
  },

  /**
   * 解封用户
   */
  unbanUser: async (userId: number): Promise<void> => {
    const response = await apiClient.put<ApiResponse<void>>(`/admin/users/${userId}/unban`);
    if (response.data.code !== 0) {
      throw new Error(response.data.message);
    }
  },

  /**
   * 调整用户积分
   */
  adjustPoints: async (userId: number, points: number, reason: string): Promise<void> => {
    const response = await apiClient.put<ApiResponse<void>>(`/admin/users/${userId}/points`, {
      points,
      reason
    });
    if (response.data.code !== 0) {
      throw new Error(response.data.message);
    }
  },

  /**
   * 获取用户增长趋势
   */
  getUserGrowth: async () => {
    const response = await apiClient.get<ApiResponse<any>>('/admin/stats/user-growth');
    return response.data.data;
  },

  /**
   * 获取积分分布
   */
  getPointsDistribution: async () => {
    const response = await apiClient.get<ApiResponse<any>>('/admin/stats/points-distribution');
    return response.data.data;
  },

  /**
   * 获取验证成功率
   */
  getVerificationRate: async () => {
    const response = await apiClient.get<ApiResponse<any>>('/admin/stats/verification-rate');
    return response.data.data;
  },

  /**
   * 获取群组成员列表
   */
  getGroupMembers: async () => {
    const response = await apiClient.get<ApiResponse<any>>('/admin/groups/members');
    return response.data.data;
  },

  /**
   * 禁言群组成员
   */
  muteMember: async (userId: number, duration?: number, reason?: string) => {
    await apiClient.post<ApiResponse<void>>(`/admin/groups/members/${userId}/mute`, {
      duration,
      reason
    });
  },

  /**
   * 解除群组成员禁言
   */
  unmuteMember: async (userId: number, reason?: string) => {
    await apiClient.post<ApiResponse<void>>(`/admin/groups/members/${userId}/unmute`, {
      reason
    });
  },

  /**
   * 踢出群组成员
   */
  kickMember: async (userId: number, reason?: string) => {
    await apiClient.post<ApiResponse<void>>(`/admin/groups/members/${userId}/kick`, {
      reason
    });
  },

  /**
   * 封禁用户
   */
  banUser: async (userId: number, reason: string): Promise<void> => {
    await apiClient.post<ApiResponse<void>>(`/admin/users/${userId}/ban`, { reason });
  },

  /**
   * 解封用户
   */
  unbanUser: async (userId: number, reason: string): Promise<void> => {
    await apiClient.post<ApiResponse<void>>(`/admin/users/${userId}/unban`, { reason });
  },

  /**
   * 重置用户积分
   */
  resetPoints: async (userId: number, reason: string): Promise<void> => {
    await apiClient.post<ApiResponse<void>>(`/admin/users/${userId}/reset-points`, { reason });
  },
};
