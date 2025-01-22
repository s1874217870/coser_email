/**
 * 用户数据Hook
 */
import { useState, useEffect } from 'react';
import { adminApi } from '@/api/admin';
import type { User } from '@/types/api';

export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await adminApi.getUsers();
        console.log('获取到的用户数据:', data);
        setUsers(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载用户列表失败');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const refetch = () => {
    fetchUsers();
  };

  return { users, isLoading, error, refetch };
}
