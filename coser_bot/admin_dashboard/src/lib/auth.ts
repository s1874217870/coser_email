/**
 * 认证工具库
 */
import { create } from 'zustand';
import type { AdminUser } from '@/types/api';
import { authApi } from '@/api/auth';

interface AuthState {
  user: AdminUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuth = create<AuthStore>((set) => ({
  // 状态
  user: null,
  token: localStorage.getItem(import.meta.env.VITE_JWT_KEY),
  isAuthenticated: !!localStorage.getItem(import.meta.env.VITE_JWT_KEY),
  isLoading: false,
  error: null,

  // 操作
  login: async (username: string, password: string) => {
    try {
      set({ isLoading: true, error: null });
      const response = await authApi.login({ username, password });
      localStorage.setItem(import.meta.env.VITE_JWT_KEY, response.access_token);
      const user = await authApi.getProfile();
      set({ 
        user, 
        token: response.access_token, 
        isAuthenticated: true,
        isLoading: false 
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : '登录失败，请稍后重试';
      set({ 
        user: null, 
        token: null, 
        isAuthenticated: false, 
        error: message,
        isLoading: false 
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      set({ isLoading: true, error: null });
      await authApi.logout();
      localStorage.removeItem(import.meta.env.VITE_JWT_KEY);
      set({ 
        user: null, 
        token: null, 
        isAuthenticated: false,
        isLoading: false 
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : '注销失败，请稍后重试';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  checkAuth: async () => {
    try {
      set({ isLoading: true, error: null });
      const user = await authApi.getProfile();
      set({ 
        user, 
        isAuthenticated: true,
        isLoading: false 
      });
    } catch {
      localStorage.removeItem(import.meta.env.VITE_JWT_KEY);
      set({ 
        user: null, 
        token: null, 
        isAuthenticated: false,
        isLoading: false 
      });
      throw new Error('会话已过期，请重新登录');
    }
  },

  clearError: () => set({ error: null }),
}));
