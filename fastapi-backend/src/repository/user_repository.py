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
        result = result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:

        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()
