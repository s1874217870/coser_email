"""
创建管理员账号脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.models.admin import AdminUser, AdminRole, Base
from app.core.auth import Auth
from app.core.config import get_settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

settings = get_settings()

def get_value(session: Session, obj: AdminUser, attr: str) -> str:
    """从SQLAlchemy对象中安全地获取属性值"""
    value = getattr(obj, attr)
    if hasattr(value, '__call__'):
        return str(session.scalar(value))
    return str(value)

def create_admin():
    """创建管理员账号"""
    try:
        # 创建数据库连接
        db_path = os.path.join(project_root, 'test.db')
        engine = create_engine(f'sqlite:///{db_path}')
        
        # 创建数据库表
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # 检查数据库连接
            session.execute(text('SELECT 1'))
            print('数据库连接成功')

            # 创建管理员账号
            password_hash = Auth.get_password_hash('testpass123')
            admin = AdminUser(
                username='test_admin',
                password_hash=password_hash,
                role=AdminRole.SUPERADMIN,
                is_active=True
            )

            # 删除已存在的同名账号
            existing = session.query(AdminUser).filter_by(username='test_admin').first()
            if existing:
                print(f'删除已存在的管理员账号: {get_value(session, existing, "username")}')
                session.delete(existing)
                session.commit()

            # 添加新账号
            session.add(admin)
            session.commit()
            print('新管理员账号已创建')

            # 验证账号
            result = session.query(AdminUser).filter_by(username='test_admin').first()
            if result:
                print('\n管理员账号创建状态：')
                print(f'ID: {get_value(session, result, "id")}')
                print(f'用户名: {get_value(session, result, "username")}')
                print(f'角色: {result.role.name}')
                print(f'状态: {"激活" if bool(get_value(session, result, "is_active")) else "禁用"}')
                print('\n验证密码哈希...')
                valid = Auth.verify_password('testpass123', get_value(session, result, "password_hash"))
                print(f'密码验证: {"成功" if valid else "失败"}')
            else:
                print('错误：账号创建失败')

        except SQLAlchemyError as e:
            print(f'数据库操作错误: {e}')
            session.rollback()
        finally:
            session.close()

    except Exception as e:
        print(f'发生错误: {e}')
        sys.exit(1)

if __name__ == '__main__':
    create_admin()
