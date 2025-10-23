# fastapi-backend/src/api/teacher_router.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import  Dict
from ..database import get_db
from ..schemas.schemas import ProblemCreate, ProblemUpdate
from ..core.security import get_current_teacher_user
from ..models.user_models import User
from ..repository.problem_repository import ProblemRepository
from  ..repository.submission_repository import  SubmissionRepository
from ..services.problem_service import ProblemService
from  ..services.submission_service import SubmissionService
from  uuid import UUID


teacher_router = APIRouter(prefix="/api/teacher", tags=["Преподавательский функционал"])


# async def get_services(db: AsyncSession = Depends(get_db)) -> Dict:
#     """Создает и инжектирует репозитории и сервисы."""
#     problem_repo = ProblemRepository(db)
#     submission_repo = SubmissionRepository(db)
#
#     problem_service = ProblemService(problem_repo, submission_repo)
#     submission_service = SubmissionService(problem_repo, submission_repo)
#
#     return {
#         "problem": problem_service,
#         "submission": submission_service,
#     }


async def get_teacher_services(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_teacher_user)
):
    """Создает сервисы для преподавателя."""
    problem_repo = ProblemRepository(db)
    submission_repo = SubmissionRepository(db)
    problem_service = ProblemService(problem_repo, submission_repo)

    return {
        "problem_service": problem_service,
        "problem_repo": problem_repo,
        "submission_repo": submission_repo,
        "current_user": current_user
    }


@teacher_router.post("/problems", status_code=status.HTTP_201_CREATED)
async def create_problem(
        problem_data: ProblemCreate,
        services: Dict = Depends(get_teacher_services)
):
    """Создать новую задачу."""
    if not problem_data.test_cases or len(problem_data.test_cases) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Задача должна содержать хотя бы один тест"
        )

    if not problem_data.examples or len(problem_data.examples) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Задача должна содержать хотя бы один пример"
        )

    problem_service = services["problem_service"]
    current_user = services["current_user"]

    try:
        db_problem = await problem_service.create_problem(problem_data, current_user.id)
        return {
            "message": "Задача создана успешно",
            "problem_id": str(db_problem.id),
            "slug": db_problem.slug,
            "title": db_problem.title
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@teacher_router.get("/problems", status_code=status.HTTP_200_OK)
async def list_my_problems(
        skip: int = 0,
        limit: int = 50,
        services: Dict = Depends(get_teacher_services)
):
    """Получить все свои задачи."""
    problem_repo = services["problem_repo"]
    current_user = services["current_user"]

    problems = await problem_repo.get_user_problems(current_user.id)

    return {
        "total": len(problems),
        "problems": [
            {
                "id": str(p.id),
                "title": p.title,
                "slug": p.slug,
                "difficulty": p.difficulty,
                "is_public": p.is_public,
                "created_at": p.created_at
            }
            for p in problems[skip:skip + limit]
        ]
    }


@teacher_router.put("/problems/{problem_id}", status_code=status.HTTP_200_OK)
async def update_problem(
        problem_id: UUID,
        problem_data: ProblemUpdate,
        services: Dict = Depends(get_teacher_services)
):
    """Обновить задачу."""
    problem_service = services["problem_service"]

    db_problem = await problem_service.update_problem(problem_id, problem_data)

    if not db_problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    return {
        "message": "Задача обновлена успешно",
        "problem_id": str(db_problem.id),
        "slug": db_problem.slug
    }

# 💡 ДОБАВЬТЕ сюда другие роуты для обновления, удаления и т.д., используя services["problem"]