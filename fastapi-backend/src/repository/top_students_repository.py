from sqlalchemy.engine import row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_, or_, desc
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

class TopStudentsRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_top_students(self, limit: int = 10) -> List[Dict]:
        ac_subquery = (
            select(
                Submission.user_id,
                func.count().label("ac_count")
            )
            .where(Submission.status == SubmissionStatus.ACCEPTED)  # ← AC, не ACCEPTED!
            .group_by(Submission.user_id)
            .subquery()
        )

        # Основной запрос
        stmt = (
            select(
                User.id,
                User.username,
                User.full_name,
                User.email,
                User.university_id,
                User.rating,
                func.coalesce(ac_subquery.c.ac_count, 0).label("solved_count")
            )
            .join(ac_subquery, User.id == ac_subquery.c.user_id, isouter=True)
            .where(User.role == "student")
            .order_by(desc("solved_count"), desc(User.rating))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "username": row.username,
                "full_name": row.full_name,
                "email": row.email,
                "university_id": row.university_id,
                "rating": row.rating,
                "solved_count": row.solved_count,
            }
            for row in rows
        ]