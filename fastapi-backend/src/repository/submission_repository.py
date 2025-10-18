from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
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