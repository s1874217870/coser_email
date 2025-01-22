"""
用户模型模块
定义用户相关的数据库模型
"""
from sqlalchemy import Column, BigInteger, String, TIMESTAMP, text, Integer
from app.db.database import Base

class User(Base):
    """用户表模型"""
    __table_args__ = {'extend_existing': True}
    __tablename__ = "users"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    telegram_id = Column(String(32), unique=True, nullable=False)
    email = Column(String(128), unique=True)
    status = Column(BigInteger().with_variant(Integer, "sqlite"), default=1)
    points = Column(BigInteger().with_variant(Integer, "sqlite"), default=0)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

class PointRecord(Base):
    """积分记录表模型"""
    __tablename__ = "point_records"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False)
    points = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False)
    type = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False, comment='1:签到 2:活动 3:转移')
    description = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
