# fastapi-backend/src/api/teacher_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas.schemas import ProblemCreate 
from ..models.db_models import Problem, Example, TestCase
from ..repository.problem_repository import ProblemRepository,SubmissionRepository
from ..services.problem_service import ProblemService # <-- ИМПОРТ СЕРВИСА

teacher_router = APIRouter(prefix="/api/teacher", tags=["Преподавательский функционал"])

async def get_problem_service(db: AsyncSession = Depends(get_db)) -> ProblemService:
    problem_repo = ProblemRepository(db)
    submission_repo = SubmissionRepository(db)
    return ProblemService(problem_repo, submission_repo)

@teacher_router.post("/problems", status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemCreate,
    problem_service: ProblemService = Depends(get_problem_service) 
):
    """Создание новой задачи преподавателем."""
    
    if not problem_data.test_cases:
        raise HTTPException(status_code=400, detail="Задача должна содержать хотя бы один тест-кейс")

    db_problem = await problem_service.create_problem(problem_data) 
    
    return {"message": "Задача успешно создана", "problem_id": db_problem.id, "slug": db_problem.slug}