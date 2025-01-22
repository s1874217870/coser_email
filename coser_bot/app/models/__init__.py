"""
模型包初始化文件
导出所有数据库模型
"""
from .user import User, PointRecord
from .admin import AdminUser, AdminLog, AdminRole

# 导出所有模型
User = User
PointRecord = PointRecord
AdminUser = AdminUser
AdminLog = AdminLog
AdminRole = AdminRole

__all__ = [
    'User',
    'PointRecord',
    'AdminUser',
    'AdminLog',
    'AdminRole'
]
