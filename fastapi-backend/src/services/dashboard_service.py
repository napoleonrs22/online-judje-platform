
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..repository.problem_repository import ProblemRepository
from ..repository.top_students_repository import TopStudentsRepository
from ..models.user_models import User
from ..models.submission_models import Submission
from ..models.problem_models import Problem
from ..models.base import SubmissionStatus


class DashboardService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.problem_repository = ProblemRepository(db)
        self.top_students_repository = TopStudentsRepository(db)

    async def get_top_students(self, limit: int = 10) -> List[Dict]:
        return await self.top_students_repository.get_top_students(limit)

    async def get_available_problems(self, user_id: UUID, skip: int = 0, limit: int = 20) -> List[Dict]:
        problems = await self.problem_repository.list_available_problems(user_id, skip, limit)
        out = []
        for p in problems:
            stats = await self.problem_repository.get_problem_statistics(p.id)
            out.append(
                {
                    "id": str(p.id),
                    "title": p.title,
                    "slug": p.slug,
                    "difficulty": p.difficulty.value if hasattr(p.difficulty, "value") else str(p.difficulty),
                    "is_public": p.is_public,
                    "author": p.author.username if p.author else None,
                    "success_rate": round(stats.get("success_rate") or 0, 1),
                }
            )
        return out

    async def _compute_student_rank(self, user_id: UUID) -> Optional[int]:
        ac_subq = (
            select(
                Submission.user_id.label("uid"),
                func.count(func.distinct(Submission.problem_id)).label("solved_n"),
            )
            .where(Submission.status == SubmissionStatus.ACCEPTED)
            .group_by(Submission.user_id)
            .subquery()
        )
        solved_n = func.coalesce(ac_subq.c.solved_n, 0).label("solved_n")
        stmt = (
            select(User.id, solved_n, User.rating)
            .select_from(User)
            .outerjoin(ac_subq, User.id == ac_subq.c.uid)
            .where(User.role == "student")
            .order_by(desc(solved_n), desc(User.rating))
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        for idx, row in enumerate(rows, start=1):
            if row.id == user_id:
                return idx
        return None

    async def get_my_stats(self, user: User) -> dict:
        user_id = user.id
        role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
        rating = user.rating

        stmt_solved = (
            select(func.count(func.distinct(Submission.problem_id)))
            .where(
                Submission.user_id == user_id,
                Submission.status == SubmissionStatus.ACCEPTED,
            )
        )
        solved = (await self.db.execute(stmt_solved)).scalar() or 0

        week_ago = datetime.utcnow() - timedelta(days=7)
        stmt_week = (
            select(func.count())
            .select_from(Submission)
            .where(
                Submission.user_id == user_id,
                Submission.created_at >= week_ago,
            )
        )
        submissions_week = (await self.db.execute(stmt_week)).scalar() or 0

        rank: Optional[int] = None
        if role_val == "student":
            rank = await self._compute_student_rank(user_id)

        stmt_recent = (
            select(Submission, Problem.title)
            .join(Problem, Problem.id == Submission.problem_id)
            .where(Submission.user_id == user_id)
            .order_by(desc(Submission.created_at))
            .limit(12)
        )
        recent_rows = (await self.db.execute(stmt_recent)).all()
        recent_activity = []
        for sub, title in recent_rows:
            st = sub.status.value if hasattr(sub.status, "value") else str(sub.status)
            recent_activity.append(
                {
                    "problem_id": str(sub.problem_id),
                    "problem_title": title,
                    "status": st,
                    "created_at": sub.created_at.isoformat() if sub.created_at else None,
                }
            )

        est_minutes = submissions_week * 15
        est_hours_rounded = round(est_minutes / 60, 1)

        return {
            "rating": rating,
            "solved_count": int(solved),
            "rank": rank,
            "submissions_this_week": int(submissions_week),
            "estimated_hours_this_week": est_hours_rounded,
            "recent_activity": recent_activity,
        }
