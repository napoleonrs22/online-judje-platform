import re
import uuid
from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user_models import User


from ..repository.user_repository import UserRepository
class AdminUSerService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user_as_admin(self, email: str, username: str, password: str,
                                   role: str, full_name: str = None) -> User:
        """Создать пользователя (только админ)."""

        existing_user = await self.user_repository.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email уже зарегистрирован")

        existing_user = await self.user_repository.get_user_by_username(username)
        if existing_user:
            raise ValueError("Username уже занят")

        # Хеширование пароля
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(password)

        user = await self.user_repository.create_user(
            email=email,
            username=username,
            hashed_password=hashed_password,
            role=role,
            full_name=full_name
        )

        return user


