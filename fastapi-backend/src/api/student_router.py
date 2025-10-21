# fastapi-backend/src/api/student_router.py

from typing import List, Dict  # Импортируем Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid  # Нужен для user_id заглушки

from ..database import get_db
from ..schemas.schemas import SubmissionCreate, SubmissionResponse, ProblemBase
from ..repository.problem_repository import ProblemRepository
from ..repository.submission_repository import SubmissionRepository
from ..services.problem_service import ProblemService
from ..services.submission_service import SubmissionService
from ..services.auth_service import get_current_student
from ..models.user_models import User

student_router = APIRouter(prefix="/api/student", tags=["Функционал студента"])


async def get_services(db: AsyncSession = Depends(get_db)) -> Dict:
    problem_repo = ProblemRepository(db)
    submission_repo = SubmissionRepository(db)
    submission_service = SubmissionService(
        submission_repository=submission_repo,
        problem_repository=problem_repo
    )
    problem_service = ProblemService(problem_repo, submission_repo)  

    return {
        "problem": problem_service,
        "submission": submission_service,
    }


@student_router.post("/submissions", status_code=status.HTTP_202_ACCEPTED, response_model=SubmissionResponse)
async def submit_solution(
        submission_data: SubmissionCreate,
        services: Dict = Depends(get_services),
        current_user: User = Depends(get_current_student)  
):
    """Отправка решения студентом на проверку в Go-Executor."""


    response = await services["submission"].submit_solution(submission_data, user_id= current_user.id)

    return response


@student_router.get("/problems", response_model=List[ProblemBase])
async def list_problems(
        services: Dict = Depends(get_services)  
):
    """Получение списка всех опубликованных задач."""
    problems = await services["problem"].problem_repo.list_public_problems()

    return problems