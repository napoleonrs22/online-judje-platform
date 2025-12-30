# services/auth_service.py
"""
Сервис аутентификации.
Обрабатывает регистрацию, логин, обновление токенов.
"""

import logging
from typing import Optional
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models.user_models import User
from ..schemas.schemas import UserCreate
from ..core.security import (
    Role,
    PasswordService,
    TokenService,
    oauth2_scheme,
    get_current_user_id,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Сервис для аутентификации и управления пользователями."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._password_service = PasswordService()
        self._token_service = TokenService()

    # === Работа с паролями ===

    def hash_password(self, password: str) -> str:
        """Хэширует пароль."""
        return self._password_service.hash_password(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль."""
        return self._password_service.verify_password(plain_password, hashed_password)

    # === Работа с токенами ===

    def create_access_token(self, user: User) -> str:
        """Создаёт access токен для пользователя."""
        role = user.role.value if hasattr(user.role, 'value') else user.role
        return self._token_service.create_access_token(user.id, role)

    def create_refresh_token(self, user: User) -> str:
        """Создаёт refresh токен для пользователя."""
        role = user.role.value if hasattr(user.role, 'value') else user.role
        return self._token_service.create_refresh_token(user.id, role)

    def decode_token(self, token: str) -> Optional[dict]:
        """Декодирует токен."""
        return self._token_service.decode_token(token)

    def verify_refresh_token_string(self, token: str, hashed_token: str) -> bool:
        """
        Проверяет refresh токен против хэша в БД.
        ВАЖНО: Использует правильную схему SHA256 + bcrypt.
        """
        return self._password_service.verify_refresh_token(token, hashed_token)

    # === Работа с пользователями в БД ===

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получает пользователя по ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получает пользователя по email."""
        stmt = select(User).where(User.email == email.lower().strip())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Получает пользователя по username."""
        stmt = select(User).where(User.username == username.strip())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Регистрирует нового пользователя.

        Raises:
            HTTPException 409: Email или username уже заняты
            HTTPException 500: Ошибка сервера
        """
        # Нормализация данных
        email = user_data.email.lower().strip()
        username = user_data.username.strip()

        # Проверка существующих пользователей
        existing_email = await self.get_user_by_email(email)
        if existing_email:
            logger.info(f"Попытка регистрации с существующим email: {email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email уже зарегистрирован"
            )

        existing_username = await self.get_user_by_username(username)
        if existing_username:
            logger.info(f"Попытка регистрации с существующим username: {username}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Имя пользователя уже занято"
            )

        # Нормализация роли
        role = user_data.role
        if isinstance(role, str):
            role = role.strip().lower()
        elif hasattr(role, 'value'):
            role = role.value

        # Создание пользователя
        hashed_password = self.hash_password(user_data.password)

        db_user = User(
            id=uuid4(),
            email=email,
            username=username,
            hashed_password=hashed_password,
            role=role,
            full_name=user_data.full_name,
            rating=0
        )

        try:
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)

            logger.info(f"Создан новый пользователь: {username} ({email}), роль: {role}")
            return db_user

        except IntegrityError as e:
            await self.db.rollback()
            error_msg = str(e.orig).lower() if e.orig else str(e).lower()

            logger.error(f"IntegrityError при создании пользователя: {error_msg}")

            if "username" in error_msg or "ix_users_username" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Имя пользователя уже занято"
                )
            if "email" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email уже зарегистрирован"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании пользователя"
            )

    async def update_refresh_token(self, user: User, refresh_token: Optional[str]) -> None:
        if refresh_token:
            user.refresh_token_hash = self._password_service.hash_refresh_token(refresh_token)
        else:
            user.refresh_token_hash = None

        await self.db.commit()
        await self.db.refresh(user)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)

        if not user:
            logger.debug(f"Пользователь не найден: {email}")
            return None

        if not self.verify_password(password, user.hashed_password):
            logger.debug(f"Неверный пароль для: {email}")
            return None

        logger.info(f"Успешная аутентификация: {email}")
        return user


# === Зависимости (Dependencies) ===

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Создаёт экземпляр AuthService."""
    return AuthService(db)


async def get_current_user(
        user_id: UUID = Depends(get_current_user_id),
        auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Получает текущего пользователя из БД по ID из токена.

    Использование:
        @router.get("/me")
        async def get_me(user: User = Depends(get_current_user)):
            return user
    """
    user = await auth_service.get_user_by_id(user_id)

    if not user:
        logger.warning(f"Пользователь не найден в БД: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Проверяет, что пользователь активен."""
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    return user


# === Зависимости для ролей (используют get_current_user) ===

async def get_current_teacher(user: User = Depends(get_current_user)) -> User:
    """Требует роль teacher или admin."""
    role = user.role.value if hasattr(user.role, 'value') else str(user.role).lower()

    if role not in [Role.TEACHER.value, Role.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль преподавателя или администратора"
        )
    return user


async def get_current_student(user: User = Depends(get_current_user)) -> User:
    """Требует роль student."""
    role = user.role.value if hasattr(user.role, 'value') else str(user.role).lower()

    if role != Role.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль студента"
        )
    return user


async def get_current_student_or_teacher_or_admin(user: User = Depends(get_current_user)) -> User:
    """Разрешает любую роль (student, teacher, admin)."""
    role = user.role.value if hasattr(user.role, 'value') else str(user.role).lower()

    if role not in [Role.STUDENT.value, Role.TEACHER.value, Role.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа"
        )
    return user


# === Экспорт ===

__all__ = [
    "AuthService",
    "get_auth_service",
    "get_current_user",
    "get_current_active_user",
    "get_current_teacher",
    "get_current_student",
    "get_current_student_or_teacher_or_admin",
]