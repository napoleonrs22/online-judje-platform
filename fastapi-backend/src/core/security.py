# ============== src/core/security.py ==============

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Union

from ..database import get_db
from ..repository.user_repository import UserRepository
from ..models.user_models import User

security = HTTPBearer()

# ⚠️ TODO: Переместить в .env файл!
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============== СОЗДАНИЕ ТОКЕНОВ ==============

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
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "token_type": "access"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "token_type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ============== ПРОВЕРКА ТОКЕНОВ ==============

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    ✅ Получить текущего пользователя из JWT access token.

    Используется как Depends() в защищённых роутах.

    Выбрасывает:
        - HTTPException(401): Если токен невалидный или истёкший
        - HTTPException(404): Если пользователь не найден
    """
    token = credentials.credentials

    # ============ 1. Проверка подписи токена ============
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # ============ 2. Проверка структуры payload ============
    user_id: str = payload.get("sub")
    token_type: str = payload.get("token_type")

    # ❌ ПРОБЛЕМА: Вы проверяете token_type == "access", но при создании не устанавливаете!
    # ✅ РЕШЕНИЕ: Добавить проверку или убрать, если не требуется
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id"
        )

    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: not an access token"
        )

    # ============ 3. Парсинг UUID ============
    try:
        user_id_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user_id is not a valid UUID"
        )

    # ============ 4. Получение пользователя из БД ============
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_id_uuid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ============== ПРОВЕРКА РОЛЕЙ ==============

def require_role(allowed_roles: Union[str, List[str]]):
    """
    🎯 Фабрика зависимостей для проверки ролей.

    Args:
        allowed_roles: Строка или список разрешённых ролей

    Примеры использования:
        @router.post("", dependencies=[Depends(require_role("ADMIN"))])
        @router.post("", dependencies=[Depends(require_role(["TEACHER", "ADMIN"]))])

    Returns:
        Async функция, которая проверяет роль пользователя
    """
    # ✅ Нормализуем входящие роли
    if isinstance(allowed_roles, str):
        normalized_roles = [allowed_roles.upper()]
    else:
        normalized_roles = [role.upper() for role in allowed_roles]

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """Проверяет, что пользователь имеет одну из разрешённых ролей."""
        user_role = current_user.role.upper()

        # ✅ Правило: ADMIN может делать всё, что может делать TEACHER
        if user_role == "ADMIN":
            return current_user

        # Проверяем, есть ли роль пользователя в списке разрешённых
        if user_role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(normalized_roles)}"
            )

        return current_user

    return role_checker


# ============== СПЕЦИАЛЬНЫЕ ЗАВИСИМОСТИ ==============

async def get_current_admin_user(
        current_user: User = Depends(require_role("ADMIN"))
) -> User:
    """
    Получить текущего пользователя с проверкой роли ADMIN.

    Альтернатива: использовать dependencies=[Depends(require_role("ADMIN"))]
    """
    return current_user


async def get_current_teacher_user(
        current_user: User = Depends(require_role(["TEACHER", "ADMIN"]))
) -> User:
    """
    Получить текущего пользователя с проверкой роли TEACHER или ADMIN.

    Альтернатива: использовать dependencies=[Depends(require_role(["TEACHER", "ADMIN"]))]
    """
    return current_user


async def get_current_student_user(
        current_user: User = Depends(require_role("STUDENT"))
) -> User:
    """
    Получить текущего пользователя с проверкой роли STUDENT.
    """
    return current_user