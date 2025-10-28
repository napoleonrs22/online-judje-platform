import re
import uuid
from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user_models import User
from ..repository.user_repository import UserRepository
from  ..schemas.user_schemas import  UserResponse, CreateUserRequest, UpdateUserRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async  def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.user_repository.get_user_by_id(user_id)

    async def list_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[User]:
        users = await self.user_repository.list_users(skip, limit)
        if role:
            users = [u for u in users if u.role == role]
        return users




