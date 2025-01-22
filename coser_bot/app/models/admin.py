"""
管理员模型模块
定义管理员用户和日志相关的数据库模型
"""
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, text, Integer, ForeignKey, Enum
from app.db.database import Base
import enum

class AdminRole(enum.Enum):
    """管理员角色枚举"""
    SUPERADMIN = "superadmin"  # 超级管理员
    MODERATOR = "moderator"    # 版主
    VIEWER = "viewer"          # 查看者

class AdminUser(Base):
    """管理员用户表模型"""
    __tablename__ = "admin_users"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(AdminRole), nullable=False, default=AdminRole.VIEWER)
    is_active = Column(Boolean, default=True)
    last_login = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

class AdminLog(Base):
    """管理员操作日志表模型"""
    __tablename__ = "admin_logs"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('admin_users.id'), nullable=False)
    action = Column(String(50), nullable=False)  # 操作类型
    target_type = Column(String(50), nullable=False)  # 操作对象类型（用户/积分/群组等）
    target_id = Column(String(50), nullable=False)  # 操作对象ID
    details = Column(String(500))  # 操作详情
    ip_address = Column(String(50))  # 操作IP
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
