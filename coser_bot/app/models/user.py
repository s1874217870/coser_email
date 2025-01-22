"""
用户相关数据库模型
"""
from sqlalchemy import Column, BigInteger, Integer, String, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(String(32), unique=True, nullable=False)
    email = Column(String(128), unique=True)
    status = Column(Integer, default=1)
    points = Column(BigInteger, default=0)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
        TIMESTAMP, 
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

class PointRecord(Base):
    """积分记录模型"""
    __tablename__ = 'point_records'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    points = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False, comment='1:签到 2:活动 3:转移')
    description = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
