# core/security.py
"""
Единый модуль безопасности и авторизации.
Содержит все функции для работы с JWT токенами и проверки ролей.
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, List
from enum import Enum
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings

# Настройка логирования
logger = logging.getLogger(__name__)

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 схема для Swagger UI
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login-form",
    scheme_name="JWT",
    auto_error=True
)


class Role(str, Enum):
    """Роли пользователей в системе."""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

    @classmethod
    def from_string(cls, value: str) -> "Role":
        """Преобразует строку в Role с нормализацией."""
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError:
            raise ValueError(f"Недопустимая роль: {value}. Допустимые: {[r.value for r in cls]}")


class PasswordService:
    """Сервис для работы с паролями."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Хэширует пароль с использованием bcrypt.
        bcrypt имеет ограничение в 72 байта.
        """
        password_bytes = password.encode("utf-8")[:72]
        return pwd_context.hash(password_bytes.decode("utf-8", errors="ignore"))

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль против хэша."""
        if not hashed_password:
            return False
        plain_bytes = plain_password.encode("utf-8")[:72]
        try:
            return pwd_context.verify(plain_bytes, hashed_password)
        except Exception as e:
            logger.warning(f"Ошибка верификации пароля: {e}")
            return False

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        """
        Создаёт безопасный хэш для refresh токена.
        Используем SHA256 + bcrypt для дополнительной безопасности.
        """
        sha256_hash = hashlib.sha256(token.encode()).hexdigest()
        return pwd_context.hash(sha256_hash)

    @staticmethod
    def verify_refresh_token(token: str, hashed_token: str) -> bool:
        """Проверяет refresh токен против хэша."""
        if not hashed_token:
            return False
        sha256_hash = hashlib.sha256(token.encode()).hexdigest()
        try:
            return pwd_context.verify(sha256_hash, hashed_token)
        except Exception as e:
            logger.warning(f"Ошибка верификации refresh токена: {e}")
            return False


class TokenService:
    """Сервис для работы с JWT токенами."""

    @staticmethod
    def create_access_token(
            user_id: UUID,
            role: Union[Role, str],
            additional_claims: Optional[dict] = None
    ) -> str:
        """
        Создаёт access токен.

        Args:
            user_id: UUID пользователя
            role: Роль пользователя
            additional_claims: Дополнительные данные для токена

        Returns:
            JWT access токен
        """
        role_value = role.value if isinstance(role, Role) else str(role).lower()

        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "user_id": str(user_id),  # Для обратной совместимости
            "role": role_value,
            "token_type": "access",
            "jti": secrets.token_hex(16),  # Уникальный ID токена
            "iat": now,
            "exp": expire,
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: UUID, role: Union[Role, str]) -> str:
        """
        Создаёт refresh токен.

        Args:
            user_id: UUID пользователя
            role: Роль пользователя

        Returns:
            JWT refresh токен
        """
        role_value = role.value if isinstance(role, Role) else str(role).lower()

        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "sub": str(user_id),
            "user_id": str(user_id),
            "role": role_value,
            "token_type": "refresh",
            "jti": secrets.token_hex(16),
            "iat": now,
            "exp": expire,
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Декодирует JWT токен.

        Args:
            token: JWT токен

        Returns:
            Payload токена или None при ошибке
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.debug(f"JWT decode error: {e}")
            return None

    @staticmethod
    def verify_access_token(token: str) -> Optional[dict]:
        """
        Верифицирует access токен.

        Returns:
            Payload если токен валиден и является access токеном, иначе None
        """
        payload = TokenService.decode_token(token)
        if payload and payload.get("token_type") == "access":
            return payload
        return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[dict]:
        """
        Верифицирует refresh токен.

        Returns:
            Payload если токен валиден и является refresh токеном, иначе None
        """
        payload = TokenService.decode_token(token)
        if payload and payload.get("token_type") == "refresh":
            return payload
        return None


# === ЗАВИСИМОСТИ (Dependencies) ===

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
    """
    Извлекает ID пользователя из access токена.
    Используется как базовая зависимость.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный токен авторизации",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = TokenService.verify_access_token(token)

    if not payload:
        logger.warning("Попытка доступа с невалидным access токеном")
        raise credentials_exception

    user_id_str = payload.get("sub") or payload.get("user_id")
    if not user_id_str:
        raise credentials_exception

    try:
        return UUID(user_id_str)
    except ValueError:
        raise credentials_exception


def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Возвращает полный payload токена.
    Полезно когда нужен доступ к роли без запроса в БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный токен авторизации",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = TokenService.verify_access_token(token)
    if not payload:
        raise credentials_exception

    return payload


def require_roles(*allowed_roles: Union[Role, str]):
    """
    Фабрика зависимостей для проверки ролей.

    Использование:
        @router.get("/admin", dependencies=[Depends(require_roles(Role.ADMIN))])
        @router.get("/teachers", dependencies=[Depends(require_roles(Role.TEACHER, Role.ADMIN))])
        @router.get("/any", dependencies=[Depends(require_roles("student", "teacher"))])

    Args:
        allowed_roles: Разрешённые роли (Role enum или строки)

    Returns:
        Зависимость FastAPI для проверки роли
    """
    # Нормализуем роли к lowercase строкам
    normalized_roles = set()
    for role in allowed_roles:
        if isinstance(role, Role):
            normalized_roles.add(role.value)
        else:
            normalized_roles.add(str(role).strip().lower())

    async def role_checker(payload: dict = Depends(get_token_payload)) -> dict:
        """Проверяет роль пользователя из токена."""
        user_role = payload.get("role", "").lower()

        # Админ имеет доступ везде
        if user_role == Role.ADMIN.value:
            return payload

        if user_role not in normalized_roles:
            logger.warning(
                f"Отказ в доступе: роль '{user_role}' не в списке разрешённых {normalized_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется: {', '.join(normalized_roles)}"
            )

        return payload

    return role_checker


# === Готовые зависимости для ролей ===

require_admin = require_roles(Role.ADMIN)
require_teacher = require_roles(Role.TEACHER, Role.ADMIN)
require_student = require_roles(Role.STUDENT)
require_any_authenticated = require_roles(Role.STUDENT, Role.TEACHER, Role.ADMIN)

# === Экспорт для удобства ===

__all__ = [
    "Role",
    "PasswordService",
    "TokenService",
    "oauth2_scheme",
    "get_current_user_id",
    "get_token_payload",
    "require_roles",
    "require_admin",
    "require_teacher",
    "require_student",
    "require_any_authenticated",
]