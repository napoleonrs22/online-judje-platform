import re
import uuid
from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch

from ..models.user_models import User
from ..repository.user_repository import UserRepository
from  ..schemas.user_schemas import  UserResponse, CreateUserRequest, UpdateUserRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async  def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.user_repository.get_user_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return  await self.user_repository.get_user_by_email(email)

    async  def get_user_by_username(self, username: str) -> Optional[User]:
        return  await self.user_repository.get_user_by_username(username)

    async  def update_user(self, user_id: uuid.UUID, data: UpdateUserRequest) ->  Optional[User]:
        updated_user = data.dict(exclude_unset=True)
        return  await self.user_repository.update_user(user_id, updated_user)

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        return await self.user_repository.delete_user(user_id)


    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_username(username: str) -> bool:
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def validate_password(password: str) -> bool:
        return len(password) >= 8


    # это еще я буду переделать под группы пока это затычка
    async def list_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[User]:
        users = await self.user_repository.list_users(skip, limit)
        if role:
            users = [u for u in users if u.role == role]
        return users




