/**
 * 路由保护组件
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const navigate = useNavigate();
  const { isAuthenticated, checkAuth } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      checkAuth().catch(() => {
        navigate('/login');
      });
    }
  }, [isAuthenticated, checkAuth, navigate]);

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
