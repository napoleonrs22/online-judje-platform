# fastapi-backend/src/api/teacher_router.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import  Dict
from ..database import get_db
from ..schemas.schemas import ProblemCreate, ProblemUpdate, ProblemId
from ..repository.problem_repository import ProblemRepository
from  ..repository.submission_repository import  SubmissionRepository
from ..services.problem_service import ProblemService
from  ..services.submission_service import SubmissionService
from  uuid import UUID


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


@teacher_router.post("/problems", status_code=status.HTTP_201_CREATED)
async def create_problem(
        problem_data: ProblemCreate,
        services: Dict = Depends(get_services)
):
    """Создание новой задачи преподавателем."""

    if not problem_data.test_cases:
        raise HTTPException(status_code=400, detail="Задача должна содержать хотя бы один тест-кейс")

    user_id = uuid.UUID('11111111-1111-1111-1111-111111111111')

    problem_service: ProblemService = services["problem"]

    db_problem = await problem_service.create_problem(problem_data, user_id)

    return {"message": "Задача успешно создана", "problem_id": db_problem.id, "slug": db_problem.slug}


@teacher_router.get("/problems/{id}", status_code=status.HTTP_200_OK)
async def get_problems_id(
        problem_id: uuid.UUID,
        services: Dict = Depends(get_services)
):
    problem_service = services["problem"]
    db_problem = await problem_service.get_problem_by_ids(problem_id)
    return {
        "id": db_problem.id,
        "title": db_problem.title,
        "slug": db_problem.slug,
        "difficulty": db_problem.difficulty,
        "is_public": db_problem.is_public
    }




@teacher_router.put("/problems/{id}", status_code=status.HTTP_200_OK)
async def update_problem_by_id(
        problem_id: UUID,
        problem_data: ProblemUpdate,
        services: Dict = Depends(get_services),
):
    problem_service = services["problem"]
    db_problem = await problem_service.update_problem(problem_id, problem_data)

    return {
        "message": "Задача успешно обновлена",
        "problem_id": str(db_problem.id),
        "slug": db_problem.slug
    }


# 💡 ДОБАВЬТЕ сюда другие роуты для обновления, удаления и т.д., используя services["problem"]