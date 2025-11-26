
from typing import List, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from ..repository.problem_repository import ProblemRepository
from ..repository.top_students_repository import TopStudentsRepository
# from ..repository.contest_repository import ContestRepository
from datetime import datetime


class DashboardService:


    def __init__(self, db: AsyncSession):
        self.problem_repository = ProblemRepository(db)
        self.top_students_repository = TopStudentsRepository(db)

    async  def get_top_students(self, limit: int = 10) -> List[Dict]:
        return await self.top_students_repository.get_top_students(limit)


    async def get_available_problems(self, user_id : UUID, skip: int = 0, limit: int=20) -> List[Dict]:
        problems = await self.problem_repository.list_available_problems(user_id, skip, limit)

        return [
            {
                "id": str(p.id),
                "title": p.title,
                "slug": p.slug,
                "difficulty": p.difficulty.value,
                "is_public": p.is_public,
                "author": p.author.username if p.author else None
            }
            for p in problems
        ]
