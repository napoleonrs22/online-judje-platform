from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc
from typing import Optional, List
from  uuid import UUID
import uuid

from ..models.submission_models import Submission
from ..models.base import SubmissionStatus




class SubmissionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_submission(self, submission: Submission):
        self.db.add(submission)
        await self.db.flush()
        return submission

    async def update_submission(self, submission: Submission):

        await self.db.commit()
        await self.db.refresh(submission)
        return submission

    async  def get_submission_by_id(self, submission_id: uuid.UUID) -> Optional[Submission]:
        stmt = (
            select(Submission).where(Submission.id == submission_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_submissions(self,user_id, skip=0, limit=50) -> List[Submission]:
        stmt = (
            select(Submission).where(Submission.user_id == user_id)
            .offset(skip)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_submissions(self, submissions_id: List[uuid.UUID]) -> int:

        stmt = (
            delete(Submission)
            .where(Submission.id.in_(submissions_id))
            .where(Submission.status == SubmissionStatus.PENDING)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        await self.db.close()
        return result.rowcount

    async def get_user_submissions(self, user_id, skip=0, limit=50) -> List[Submission]:

        stmt = (
            select(Submission).where(Submission.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Submission.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_problem_submissions(
            self,
            problem_id: UUID,
            skip: int = 0,
            limit: int = 50
    ) -> List[Submission]:
        """Получить все попытки решения конкретной задачи с пагинацией."""
        stmt = (
            select(Submission)
            .where(Submission.problem_id == problem_id)
            .order_by(desc(Submission.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

