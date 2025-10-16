# fastapi-backend/src/api/student_router.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.schemas import SubmissionCreate, SubmissionResponse, ProblemBase
from ..models.db_models import Problem 
from ..repository.problem_repository import ProblemRepository, SubmissionRepository 
from ..services.problem_service import ProblemService


student_router = APIRouter(prefix="/api/student", tags=["Функционал студента"])

async def get_problem_service(db: AsyncSession = Depends(get_db)) -> ProblemService:
    problem_repo = ProblemRepository(db)
    submission_repo = SubmissionRepository(db)
    return ProblemService(problem_repo, submission_repo)


@student_router.post("/submissions", status_code=status.HTTP_202_ACCEPTED, response_model=SubmissionResponse)
async def submit_solution(
    submission_data: SubmissionCreate,
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Отправка решения студентом на проверку в Go-Executor."""
    
    response = await problem_service.submit_solution_to_go(submission_data)
    
    return response

@student_router.get("/problems", response_model=List[ProblemBase])
async def list_problems(
    problem_service: ProblemService = Depends(get_problem_service) 
):
    """
    Получение списка всех опубликованных задач.
    """
    problems = await problem_service.problem_repo.list_public_problems() 
    
    return problems