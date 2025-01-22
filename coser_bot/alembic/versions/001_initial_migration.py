"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-03-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 创建users表
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.String(32), nullable=False),
        sa.Column('email', sa.String(128), nullable=True),
        sa.Column('status', sa.Integer(), server_default='1'),
        sa.Column('points', sa.BigInteger(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id'),
        sa.UniqueConstraint('email')
    )
    
    # 添加索引以提高查询性能
    op.create_index('idx_telegram_id', 'users', ['telegram_id'])
    op.create_index('idx_email', 'users', ['email'])
    
    # 创建point_records表
    op.create_table(
        'point_records',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False, comment='1:签到 2:活动 3:转移'),
        sa.Column('description', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 添加索引以提高查询性能
    op.create_index('idx_user_id', 'point_records', ['user_id'])
    op.create_index('idx_created_at', 'point_records', ['created_at'])
    
    # 添加外键约束
    op.create_foreign_key(
        'fk_point_records_user_id',
        'point_records', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    # 删除外键约束
    op.drop_constraint('fk_point_records_user_id', 'point_records', type_='foreignkey')
    
    # 删除索引
    op.drop_index('idx_created_at', 'point_records')
    op.drop_index('idx_user_id', 'point_records')
    op.drop_index('idx_email', 'users')
    op.drop_index('idx_telegram_id', 'users')
    
    # 删除表
    op.drop_table('point_records')
    op.drop_table('users')
