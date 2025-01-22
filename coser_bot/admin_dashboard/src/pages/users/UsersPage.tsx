/**
 * 用户管理页面
 */
import React, { useState } from 'react';
import { DataTable } from '@/components/ui/data-table';
import { useUsers } from '@/hooks/useUsers';
import { createColumns } from './columns';
import { adminApi } from '@/api/admin';
import { useToast } from '@/components/ui/use-toast';

export function UsersPage() {
  const { users, isLoading, error, refetch } = useUsers();
  const { toast } = useToast();
  const [actionLoading, setActionLoading] = useState(false);

  const handleBanUser = async (userId: number) => {
    try {
      console.log('尝试封禁用户:', userId);
      setActionLoading(true);
      await adminApi.banUser(userId);
      console.log('封禁成功');
      toast({
        title: "操作成功",
        description: "用户已被封禁",
      });
      await refetch();  // 等待刷新完成
      console.log('列表已刷新');
    } catch (err) {
      console.error('封禁失败:', err);
      toast({
        title: "操作失败",
        description: err instanceof Error ? err.message : "封禁用户失败",
        variant: "destructive",
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleUnbanUser = async (userId: number) => {
    try {
      setActionLoading(true);
      await adminApi.unbanUser(userId);
      toast({
        title: "操作成功",
        description: "用户已被解封",
      });
      refetch();
    } catch (err) {
      toast({
        title: "操作失败",
        description: err instanceof Error ? err.message : "解封用户失败",
        variant: "destructive",
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleResetPoints = async (userId: number) => {
    try {
      setActionLoading(true);
      await adminApi.adjustPoints(userId, 0, "管理员重置积分");
      toast({
        title: "操作成功",
        description: "用户积分已重置",
      });
      refetch();
    } catch (err) {
      toast({
        title: "操作失败",
        description: err instanceof Error ? err.message : "重置积分失败",
        variant: "destructive",
      });
    } finally {
      setActionLoading(false);
    }
  };

  if (error) {
    return <div className="p-4 text-red-500">加载失败: {error}</div>;
  }

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">用户管理</h1>
      <DataTable 
        columns={createColumns({
          onBanUser: handleBanUser,
          onUnbanUser: handleUnbanUser,
          onResetPoints: handleResetPoints
        })} 
        data={users || []} 
        isLoading={isLoading || actionLoading}
      />
    </div>
  );
}
