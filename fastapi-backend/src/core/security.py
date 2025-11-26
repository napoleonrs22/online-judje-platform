from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Union
from pydantic_settings import BaseSettings

from ..database import get_db
from ..repository.user_repository import UserRepository
from ..models.user_models import User




class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
security = HTTPBearer()




def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Создать JWT access token.

    Args:
        data: Данные для кодирования (например, {"sub": user_id})
        expires_delta: Время жизни токена

    Returns:
        JWT токен (строка)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "token_type": "access"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Создать JWT refresh token.

    Args:
        data: Данные для кодирования (например, {"sub": user_id})

    Returns:
        JWT токен (строка)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "token_type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Token decoded successfully. Payload: {payload}")
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id: str = payload.get("sub") or payload.get("user_id")
    token_type: str = payload.get("token_type")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id or sub"
        )

    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: not an access token"
        )

    try:
        user_id_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user_id is not a valid UUID"
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_id_uuid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user




def require_role(allowed_roles: Union[str, List[str]]):
    """
    Фабрика зависимостей для проверки ролей.

    Args:
        allowed_roles: Строка или список разрешённых ролей

    Примеры использования:
        @router.post("", dependencies=[Depends(require_role("admin"))])
        @router.post("", dependencies=[Depends(require_role(["teacher", "admin"]))])

    Returns:
        Async функция, которая проверяет роль пользователя
    """
    if isinstance(allowed_roles, str):
        normalized_roles = [allowed_roles.lower()]
    else:
        normalized_roles = [role.lower() for role in allowed_roles]

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """Проверяет, что пользователь имеет одну из разрешённых ролей."""
        user_role = current_user.role.lower()


        if user_role == "admin":
            return current_user


        if user_role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(normalized_roles)}"
            )

        return current_user

    return role_checker


async def get_current_admin_user(
        current_user: User = Depends(require_role("admin"))
) -> User:
    """
    Получить текущего пользователя с проверкой роли ADMIN.

    Альтернатива: использовать dependencies=[Depends(require_role("admin"))]
    """
    return current_user


async def get_current_teacher_user(
        current_user: User = Depends(require_role(["teacher", "admin"]))
) -> User:
    """
    Получить текущего пользователя с проверкой роли TEACHER или ADMIN.

    Альтернатива: использовать dependencies=[Depends(require_role(["teacher", "admin"]))]
    """
    return current_user


async def get_current_student_user(
        current_user: User = Depends(require_role("student"))
) -> User:
    """
    Получить текущего пользователя с проверкой роли STUDENT.
    """
    return current_user