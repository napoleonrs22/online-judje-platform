# fastapi-backend/src/services/teacher_service.py

from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..models.user_models import User
from ..schemas.schemas import ProblemCreate, ProblemUpdate, ProblemResponse
# from ..schemas.schemas_teacher import ProblemResponse
from ..repository.problem_repository import ProblemRepository
from ..repository.submission_repository import SubmissionRepository


class TeacherService:
    """Сервис для работы преподавателя с задачами и попытками студентов."""

    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
        self.problem_repo = ProblemRepository(db)
        self.submission_repo = SubmissionRepository(db)

    async def create_problem(self, problem_data: ProblemCreate) -> dict:
        """Создать новую задачу."""
        # Валидация
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

        slug_exists = await self.problem_repo.check_slug_exists(problem_data.slug)
        if slug_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Задача с таким slug уже существует"
            )

        try:
            problem_dict = problem_data.dict(exclude={"test_cases", "examples"})
            problem_dict["user_id"] = self.current_user.id

            examples_data = [ex.dict() for ex in problem_data.examples]
            test_cases_data = [tc.dict() for tc in problem_data.test_cases]

            db_problem = await self.problem_repo.create_problem(
                problem_dict,
                examples_data,
                test_cases_data
            )

            return {
                "message": "Задача создана успешно",
                "problem_id": str(db_problem.id),
                "slug": db_problem.slug,
                "title": db_problem.title
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка при создании задачи: {str(e)}"
            )

    async def get_user_problems(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[dict]:
        """Получить все свои задачи."""
        problems = await self.problem_repo.get_user_problems(self.current_user.id)

        return [
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

    async def update_problem(self, problem_id: str, problem_data: ProblemUpdate) -> dict:
        """Обновить задачу."""
        try:
            problem_uuid = UUID(problem_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный ID задачи"
            )

        # Проверка прав доступа
        db_problem = await self.problem_repo.get_problem_by_id(problem_uuid)
        if not db_problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        if db_problem.user_id != self.current_user.id and self.current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете редактировать чужие задачи"
            )

        # Обновление
        update_data = problem_data.dict(exclude_unset=True)
        updated_problem = await self.problem_repo.update_problem(problem_uuid, update_data)

        return {
            "message": "Задача обновлена успешно",
            "problem_id": str(updated_problem.id),
            "slug": updated_problem.slug,
            "title": updated_problem.title
        }

    async def delete_problem(self, problem_id: str) -> dict:
        """Удалить задачу."""
        try:
            problem_uuid = UUID(problem_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный ID задачи"
            )


        db_problem = await self.problem_repo.get_problem_by_id(problem_uuid)
        if not db_problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        if db_problem.user_id != self.current_user.id and self.current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете удалять чужие задачи"
            )


        deleted_id = await self.problem_repo.delete_problem(problem_uuid)

        if deleted_id:
            return {
                "message": "Задача удалена успешно",
                "problem_id": str(deleted_id)
            }

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении задачи"
        )

    async def get_problem_statistics(self, problem_id: str) -> dict:
        """Получить статистику по задаче."""
        try:
            problem_uuid = UUID(problem_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный ID задачи"
            )

        # Проверка прав доступа
        db_problem = await self.problem_repo.get_problem_by_id(problem_uuid)
        if not db_problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        if db_problem.user_id != self.current_user.id and self.current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете просматривать статистику чужих задач"
            )

        stats = await self.problem_repo.get_problem_statistics(problem_uuid)
        return stats

    async def get_problem_submissions(
        self,
        problem_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> dict:
        """Получить все попытки решения задачи."""
        try:
            problem_uuid = UUID(problem_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный ID задачи"
            )


        db_problem = await self.problem_repo.get_problem_by_id(problem_uuid)
        if not db_problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        if db_problem.user_id != self.current_user.id and self.current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете просматривать попытки чужих задач"
            )

        submissions = await self.submission_repo.get_problem_submissions(problem_uuid, skip, limit)

        return {
            "total": len(submissions),
            "submissions": submissions
        }