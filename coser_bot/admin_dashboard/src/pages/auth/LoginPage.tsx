/**
 * 登录页面
 */
import { LoginForm } from '@/components/auth/LoginForm';

export function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <div className="text-center">
          <h1 className="text-2xl font-bold">管理员登录</h1>
          <p className="text-gray-600">请登录以访问管理后台</p>
        </div>
        
        <LoginForm />
      </div>
    </div>
  );
}
