from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc
from typing import Optional, List
from  uuid import UUID
from datetime import datetime

import uuid

from ..models.submission_models import Submission
from ..models.base import SubmissionStatus



class SubmissionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_submission(
        self,
        user_id: UUID,
        problem_id: UUID,
        language: str,
        code: str
    ) -> Submission:
        """Создать новую попытку решения."""
        submission = Submission(
            id=uuid.uuid4(),
            user_id=user_id,
            problem_id=problem_id,
            language=language,
            code=code,
            status=SubmissionStatus.PENDING,
            error_message=None,
            created_at=datetime.utcnow()
        )
        self.db.add(submission)
        await self.db.flush()
        await self.db.refresh(submission)  # Освежаем объект после flush
        return submission

    async def update_submission(self, submission: Submission) -> Submission:
        """Обновить попытку решения."""
        await self.db.merge(submission)
        await self.db.commit()
        await self.db.refresh(submission)
        return submission

    async def get_submission_by_id(self, submission_id: UUID) -> Optional[Submission]:
        """Получить попытку по ID."""
        stmt = select(Submission).where(Submission.id == submission_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_submissions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Submission]:
        """Получить все попытки пользователя."""
        stmt = (
            select(Submission)
            .where(Submission.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Submission.created_at))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_submissions(self, submissions_id: List[UUID]) -> int:
        """Удалить попытки (только PENDING статус)."""
        stmt = (
            delete(Submission)
            .where(Submission.id.in_(submissions_id))
            .where(Submission.status == SubmissionStatus.PENDING)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def get_user_submissions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Submission]:
        """Получить попытки пользователя с пагинацией."""
        stmt = (
            select(Submission)
            .where(Submission.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Submission.created_at))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_problem_submissions(
        self,
        problem_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Submission]:
        """Получить все попытки решения конкретной задачи."""
        stmt = (
            select(Submission)
            .where(Submission.problem_id == problem_id)
            .order_by(desc(Submission.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()