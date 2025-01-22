/**
 * 群组管理页面
 */
import * as React from 'react';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { adminApi } from '@/api/admin';
import { toast } from 'sonner';

interface GroupMember {
  user_id: number;
  username: string;
  status: string;
  joined_date: string;
  is_muted: boolean;
}

export function GroupsPage() {
  const [members, setMembers] = React.useState<GroupMember[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  const fetchMembers = React.useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await adminApi.getGroupMembers();
      setMembers(data);
    } catch (err) {
      toast.error('加载群组成员失败', {
        description: err instanceof Error ? err.message : '请稍后重试'
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchMembers();
  }, [fetchMembers]);

  const columns = [
    {
      id: 'user_id',
      header: '用户ID',
      cell: (member: GroupMember) => member.user_id,
    },
    {
      id: 'username',
      header: '用户名',
      cell: (member: GroupMember) => member.username,
    },
    {
      id: 'status',
      header: '状态',
      cell: (member: GroupMember) => member.status,
    },
    {
      id: 'joined_date',
      header: '加入时间',
      cell: (member: GroupMember) => new Date(member.joined_date).toLocaleString(),
    },
    {
      id: 'actions',
      header: '操作',
      cell: (member: GroupMember) => (
        <div className="flex gap-2">
          <Button
            variant={member.is_muted ? 'default' : 'destructive'}
            size="sm"
            onClick={async () => {
              try {
                if (member.is_muted) {
                  await adminApi.unmuteMember(member.user_id);
                  toast.success('操作成功', {
                    description: '已解除禁言'
                  });
                } else {
                  await adminApi.muteMember(member.user_id);
                  toast.success('操作成功', {
                    description: '已禁言用户'
                  });
                }
                fetchMembers();
              } catch (err) {
                toast.error('操作失败', {
                  description: err instanceof Error ? err.message : '请稍后重试'
                });
              }
            }}
          >
            {member.is_muted ? '解除禁言' : '禁言'}
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={async () => {
              try {
                await adminApi.kickMember(member.user_id);
                toast.success('操作成功', {
                  description: '已移出群组'
                });
                fetchMembers();
              } catch (err) {
                toast.error('操作失败', {
                  description: err instanceof Error ? err.message : '请稍后重试'
                });
              }
            }}
          >
            踢出群组
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">群组管理</h1>
      <DataTable 
        columns={columns} 
        data={members} 
        isLoading={isLoading}
      />
    </div>
  );
}
