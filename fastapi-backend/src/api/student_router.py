# fastapi-backend/src/api/student_router.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.schemas import SubmissionCreate, SubmissionResponse,ProblemBase
from ..services.problem_service import submit_solution_to_go
from ..models.db_models import Problem 



student_router = APIRouter(prefix="/api/student", tags=["Функционал студента"])

@student_router.post("/submissions", status_code=status.HTTP_202_ACCEPTED, response_model=SubmissionResponse)
async def submit_solution(
    submission_data: SubmissionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Отправка решения студентом на проверку в Go-Executor."""
    
    response = await submit_solution_to_go(db, submission_data)
    
    return response

@student_router.get("/problems", response_model=List[ProblemBase])
async def list_problems(
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех опубликованных задач.
    """
    result = await db.execute(
        select(Problem).where(Problem.is_public == True)
    )
    
    problems = result.scalars().all()
    
    return problems