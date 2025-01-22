/**
 * API客户端配置
 */
import axios, { AxiosError, AxiosResponse } from 'axios';
import type { ApiResponse } from '@/types/api';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(import.meta.env.VITE_JWT_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 打印响应数据用于调试
    console.log('API响应:', response.data);
    return response;
  },
  (error: AxiosError) => {
    // 打印错误信息
    console.error('API错误:', error.response?.data || error.message);
    
    if (error.response?.status === 401) {
      // 清除token并跳转到登录页
      localStorage.removeItem(import.meta.env.VITE_JWT_KEY);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
