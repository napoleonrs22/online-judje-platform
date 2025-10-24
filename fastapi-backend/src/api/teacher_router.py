# fastapi-backend/src/api/teacher_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.schemas import ProblemCreate, ProblemUpdate, ProblemResponse
from ..services.auth_service import get_current_teacher
from ..services.teacher_service import TeacherService
from ..models.user_models import User

teacher_router = APIRouter(prefix="/api/teacher", tags=["Преподавательский функционал"])


async def get_teacher_service(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_teacher),
) -> TeacherService:
    """Создает TeacherService для преподавателя."""
    return TeacherService(db, current_user)


@teacher_router.post("/problems", status_code=status.HTTP_201_CREATED)
async def create_problem(
        problem_data: ProblemCreate,
        service: TeacherService = Depends(get_teacher_service)
):
    """Создать новую задачу (только преподаватели и администраторы)."""
    return await service.create_problem(problem_data)


@teacher_router.get("/problems", status_code=status.HTTP_200_OK)
async def list_my_problems(
        skip: int = 0,
        limit: int = 50,
        service: TeacherService = Depends(get_teacher_service)
):
    """Получить все свои задачи."""
    problems = await service.get_user_problems(skip=skip, limit=limit)
    return {
        "total": len(problems),
        "problems": problems
    }


@teacher_router.put("/problems/{problem_id}", status_code=status.HTTP_200_OK)
async def update_problem(
        problem_id: str,
        problem_data: ProblemUpdate,
        service: TeacherService = Depends(get_teacher_service)
):
    """Обновить задачу."""
    return await service.update_problem(problem_id, problem_data)


@teacher_router.delete("/problems/{problem_id}", status_code=status.HTTP_200_OK)
async def delete_problem(
        problem_id: str,
        service: TeacherService = Depends(get_teacher_service)
):
    """Удалить задачу."""
    return await service.delete_problem(problem_id)


@teacher_router.get("/problems/{problem_id}/statistics", status_code=status.HTTP_200_OK)
async def get_problem_statistics(
        problem_id: str,
        service: TeacherService = Depends(get_teacher_service)
):
    """Получить статистику по задаче."""
    return await service.get_problem_statistics(problem_id)


@teacher_router.get("/submissions", status_code=status.HTTP_200_OK)
async def list_problem_submissions(
        problem_id: str,
        skip: int = 0,
        limit: int = 50,
        service: TeacherService = Depends(get_teacher_service)
):
    """Получить все попытки решения своих задач."""
    return await service.get_problem_submissions(problem_id, skip=skip, limit=limit)