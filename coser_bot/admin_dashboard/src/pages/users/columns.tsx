/**
 * 用户列表列定义
 */
import * as React from 'react';
import { Button } from '@/components/ui/button';
import type { User } from '@/types/api';

interface ColumnProps {
  onBanUser?: (userId: number) => Promise<void>;
  onUnbanUser?: (userId: number) => Promise<void>;
  onResetPoints?: (userId: number) => Promise<void>;
}

export const createColumns = ({ onBanUser, onUnbanUser, onResetPoints }: ColumnProps) => [
  {
    id: 'id',
    header: 'ID',
    cell: (user: User) => user.id,
  },
  {
    id: 'telegram_id',
    header: 'Telegram ID',
    cell: (user: User) => user.telegram_id,
  },
  {
    id: 'email',
    header: '邮箱',
    cell: (user: User) => user.email || '-',
  },
  {
    id: 'points',
    header: '积分',
    cell: (user: User) => user.points,
  },
  {
    id: 'status',
    header: '状态',
    cell: (user: User) => user.status === 1 ? '正常' : '已封禁',
  },
  {
    id: 'actions',
    header: '操作',
    cell: (user: User) => (
      <div className="flex gap-2">
        <Button
          variant={user.status === 1 ? 'destructive' : 'default'}
          size="sm"
          onClick={() => user.status === 1 ? onBanUser?.(user.id) : onUnbanUser?.(user.id)}
        >
          {user.status === 1 ? '封禁' : '解封'}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onResetPoints?.(user.id)}
        >
          重置积分
        </Button>
      </div>
    ),
  },
];
