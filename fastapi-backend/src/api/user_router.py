
# fastapi-backend/src/api/teacher_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import  Dict
from ..database import get_db
from ..schemas.schemas import ProblemCreate, ProblemUpdate
from ..repository.problem_repository import ProblemRepository
from  ..repository.submission_repository import  SubmissionRepository
from ..services.problem_service import ProblemService
from  ..services.submission_service import SubmissionService


import uuid


teacher_router = APIRouter(prefix="/api/teacher", tags=["Преподавательский функционал"])


async def get_services(db: AsyncSession = Depends(get_db)) -> Dict:
    """Создает и инжектирует репозитории и сервисы."""
    problem_repo = ProblemRepository(db)
    submission_repo = SubmissionRepository(db)

    problem_service = ProblemService(problem_repo, submission_repo)
    submission_service = SubmissionService(problem_repo, submission_repo)

    return {
        "problem": problem_service,
        "submission": submission_service,
    }


