#admin_service.py
import re
import uuid
from typing import List, Optional

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from ..models.user_models import User
from ..repository.user_repository import UserRepository
from  ..schemas.user_schemas import  UserResponse, CreateUserRequest, UpdateUserRequest
from ..services.user_service import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




class AdminUserService(UserService):



    async def create_user_as_admin(self, data: CreateUserRequest) -> User:
        """Создать пользователя (только админ)."""

        existing_user = await self.user_repository.get_user_by_email(data.email)
        if existing_user:
            raise ValueError("Email уже зарегистрирован")

        existing_user = await self.user_repository.get_user_by_username(data.username)
        if existing_user:
            raise ValueError("Username уже занят")

        # Хеширование пароля
        hashed_password = pwd_context.hash(data.password)

        user = await self.user_repository.create_user(
            email=data.email,
            username=data.username,
            hashed_password=hashed_password,
            role=data.role,
            full_name=data.full_name,
        )

        return user

    async def update_user_as_admin(self, user_id: uuid.UUID, data: UpdateUserRequest) -> Optional[User]:
        updated_data = data.dict(exclude_unset=True)

        if "username" in updated_data:
            existing = await self.user_repository.get_user_by_username(updated_data["username"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail="Username already exists")

        if "email" in updated_data:
            existing = await self.user_repository.get_user_by_email(updated_data["email"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail="Email already exists")

        return await self.user_repository.update_user(user_id,updated_data)

    async def delete_user_as_admin(self, user_id: uuid.UUID) -> bool:
        return await self.user_repository.delete_user(user_id)

    async def  change_user_role(self, user_id: uuid.UUID, new_role: str) -> Optional[User]:
        if new_role not in ["STUDENT", "ADMIN", "TEACHER"]:
            raise ValueError("Неверная роль")
        return await self.user_repository.update_user(user_id,{"role":new_role})
