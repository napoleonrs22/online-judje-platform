from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid as uuid_lib
import re
from slugify import slugify

from ..models.base import SubmissionStatus, DifficultyLevel
from ..models.problem_models import Problem, Example, TestCase
from ..models.submission_models import Submission
from ..models.user_models import User

class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db



    async def create_user(self, email: str, username: str,hashed_password:str,role:str,full_name: str = None) -> User:

        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            rating=1500
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


    async def get_user_by_id(self, user_id: uuid_lib.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:

        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_user(self, user_id:uuid_lib.UUID, data: Dict[str, Any]) -> Optional[User]:

        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()

        if not user:
            return None

        for key, value in data.items():
            if key not in ['id', 'created_at'] and hasattr(user, key):
                setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_rating(self,user_id:uuid_lib.UUID, rating_delta:int) -> Optional[User]:


        user = await  self.get_user_by_id(user_id)

        if not user:
            return None

        user.rating = max(0, user.rating, rating_delta)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id:uuid_lib.UUID) -> bool:

        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0


    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:

        stmt = select(User).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_top_students(self, limit: int = 10) -> List[User]:
        stmt = (
            select(User)
            .where(User.role == "student")
            .order_by(User.rating.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()