"""
认证模块
处理JWT令牌生成、验证和密码哈希
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Awaitable
from inspect import isawaitable
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.admin import AdminUser, AdminRole
from app.core.config import get_settings
from app.core.redis import redis_client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Auth:
    """认证服务类"""
    
    # OAuth2认证方案
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            print(f"\n=== 验证密码 ===")
            print(f"明文密码长度: {len(plain_password)}")
            print(f"哈希密码长度: {len(hashed_password)}")
            
            # 忽略bcrypt版本警告
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                result = pwd_context.verify(plain_password, hashed_password)
            
            print(f"验证结果: {result}")
            return result
        except Exception as e:
            print(f"密码验证错误: {e}")
            print(f"错误类型: {type(e)}")
            print(f"错误详情: {str(e)}")
            return False
        
    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)
        
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        
        参数:
            data: 令牌数据
            expires_delta: 过期时间
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
        
    @staticmethod
    async def get_current_admin(
        token: str = Depends(oauth2_scheme),  # type: ignore
        db: AsyncSession = Depends(get_db)
    ) -> AdminUser:
        """
        获取当前管理员
        
        参数:
            token: JWT令牌
            db: 数据库会话
        """
        print("\n=== 验证管理员令牌 ===")
        print(f"令牌: {token[:20]}...")
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # 检查令牌是否被注销
            if redis_client.exists(f"blacklist:{token}"):
                print("令牌在黑名单中")
                raise credentials_exception
                
            # 验证令牌
            print("开始验证令牌...")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            admin_id = payload.get("sub")
            print(f"解析的管理员ID: {admin_id}")
            
            if not isinstance(admin_id, str):
                print(f"无效的管理员ID类型: {type(admin_id)}")
                raise credentials_exception
                
            # 获取管理员信息
            print(f"查询管理员信息...")
            query = select(AdminUser).where(AdminUser.id == int(admin_id))
            result = await db.execute(query)
            admin = result.scalar_one_or_none()
            
            if admin is None:
                print(f"未找到管理员: ID={admin_id}")
                raise credentials_exception
                
            if not admin.is_active:
                print(f"管理员账号已禁用: ID={admin_id}")
                raise credentials_exception
                
            print(f"验证成功: {admin.username} (ID={admin.id})")
            return admin
            
        except (JWTError, ValueError) as e:
            print(f"认证错误: {e}")
            raise credentials_exception
            
    @staticmethod
    async def get_superadmin(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
        """
        验证超级管理员权限
        
        参数:
            admin: 当前管理员
        """
        admin = await admin if isawaitable(admin) else admin
        if admin.role != AdminRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要超级管理员权限"
            )
        return admin
        
    @staticmethod
    async def blacklist_token(token: str):
        """
        将令牌加入黑名单（用于注销）
        
        参数:
            token: JWT令牌
        """
        try:
            # 解析令牌获取过期时间
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            exp = payload.get("exp")
            if exp:
                # 计算剩余有效期
                ttl = exp - datetime.utcnow().timestamp()
                if ttl > 0:
                    # 将令牌加入黑名单，过期时间与令牌相同
                    redis_client.setex(f"blacklist:{token}", int(ttl), "1")
                    return True
        except JWTError:
            pass
        return False
