"""
管理后台相关数据库模型
"""
from sqlalchemy import Column, BigInteger, Integer, String, TIMESTAMP, text, ForeignKey
from app.models.user import Base

class AdminLog(Base):
    """管理员操作日志"""
    __tablename__ = 'admin_logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(50), nullable=False)
    details = Column(String(500))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

class SecurityLog(Base):
    """安全日志"""
    __tablename__ = 'security_logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False)
    event_type = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    ip_address = Column(String(50))
    user_id = Column(BigInteger, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
