# fastapi-backend/src/api/student_router.py

from typing import List, Dict  # Импортируем Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid  # Нужен для user_id заглушки

from ..database import get_db
from ..schemas.schemas import SubmissionCreate, SubmissionResponse, ProblemBase
# Импортируем репозитории и сервисы
from ..repository.problem_repository import ProblemRepository
from ..repository.submission_repository import SubmissionRepository
from ..services.problem_service import ProblemService
from ..services.submission_service import SubmissionService

student_router = APIRouter(prefix="/api/student", tags=["Функционал студента"])


# 💡 НОВАЯ ЕДИНАЯ ЗАВИСИМОСТЬ: Возвращает словарь с обоими сервисами
async def get_services(db: AsyncSession = Depends(get_db)) -> Dict:
    problem_repo = ProblemRepository(db)
    submission_repo = SubmissionRepository(db)

    # 🔥 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем ИМЕНОВАННЫЕ АРГУМЕНТЫ для исключения путаницы!
    # Это гарантирует, что problem_repository в сервисе получит ProblemRepository.
    submission_service = SubmissionService(
        submission_repository=submission_repo,
        problem_repository=problem_repo
    )
    problem_service = ProblemService(problem_repo, submission_repo)  # ProblemService использует короткие имена

    return {
        "problem": problem_service,
        "submission": submission_service,
    }


@student_router.post("/submissions", status_code=status.HTTP_202_ACCEPTED, response_model=SubmissionResponse)
async def submit_solution(
        submission_data: SubmissionCreate,
        services: Dict = Depends(get_services)  # Запрашиваем словарь
):
    """Отправка решения студентом на проверку в Go-Executor."""

    # Имитация ID студента
    user_id = uuid.uuid4()

    # 💡 Вызываем SubmissionService из словаря
    response = await services["submission"].submit_solution(submission_data, user_id)

    return response


@student_router.get("/problems", response_model=List[ProblemBase])
async def list_problems(
        services: Dict = Depends(get_services)  # Запрашиваем словарь
):
    """Получение списка всех опубликованных задач."""
    # 💡 Вызываем ProblemService
    problems = await services["problem"].problem_repo.list_public_problems()

    return problems