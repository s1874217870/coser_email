/**
 * 登录表单组件
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/lib/auth';

const loginSchema = z.object({
  username: z.string().min(1, '请输入用户名'),
  password: z.string().min(1, '请输入密码'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const navigate = useNavigate();
  const { login, isLoading, error: authError, clearError } = useAuth();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // 清除错误
  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      console.log('尝试登录:', data);
      console.log('请求前状态:', { isLoading, isSubmitting });
      
      // 确保请求格式正确
      const formData = {
        username: data.username.trim(),
        password: data.password,
        grant_type: 'password'
      };
      console.log('发送登录请求:', formData);
      
      await login(formData.username, formData.password);
      console.log('登录成功，准备跳转');
      navigate('/');
    } catch (err) {
      console.error('登录失败:', err);
      if (err instanceof Error) {
        console.error('错误详情:', {
          message: err.message,
          name: err.name,
          stack: err.stack
        });
      }
      // 错误已经在 auth store 中处理
    }
  };

  const handleFormSubmit = async (data: LoginFormData) => {
    console.log('表单提交:', data);
    try {
      await login(data.username.trim(), data.password);
      console.log('登录成功，准备跳转');
      navigate('/');
    } catch (err) {
      console.error('表单提交错误:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <div>
        <Input
          {...register('username')}
          placeholder="用户名"
          autoComplete="username"
          onChange={(e) => console.log('用户名输入:', e.target.value)}
        />
        {errors.username && (
          <p className="text-sm text-red-500">{errors.username.message}</p>
        )}
      </div>
      
      <div>
        <Input
          {...register('password')}
          type="password"
          placeholder="密码"
          autoComplete="current-password"
          onChange={(e) => console.log('密码输入:', e.target.value)}
        />
        {errors.password && (
          <p className="text-sm text-red-500">{errors.password.message}</p>
        )}
      </div>

      {authError && <p className="text-sm text-red-500">{authError}</p>}

      <Button
        type="submit"
        className="w-full"
        disabled={isSubmitting || isLoading}
        onClick={() => console.log('登录按钮点击')}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            登录中...
          </>
        ) : (
          '登录'
        )}
      </Button>
    </form>
  );
}
