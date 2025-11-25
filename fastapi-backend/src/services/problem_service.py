# fastapi-backend/src/services/problem_service.py

import re
import uuid
from typing import List, Optional

from ..schemas.schemas import ProblemCreate, ProblemUpdate
from ..models.problem_models import Problem
from ..models.base import DifficultyLevel
from ..repository.problem_repository import ProblemRepository
from ..repository.submission_repository import SubmissionRepository


def generate_slug(title: str) -> str:
    """Генерация URL-friendly slug из названия"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')

    if not slug:
        return 'problem-' + str(uuid.uuid4())[:8]

    return slug


class ProblemService:

    def __init__(self, problem_repo: ProblemRepository, submission_repo: SubmissionRepository):

        self.problem_repo = problem_repo
        self.submission_repo = submission_repo

    async def _generate_unique_slug(self, title: str) -> str:
        """
        Генерирует уникальный slug, проверяя его наличие в БД через репозиторий.
        При необходимости добавляет числовой постфикс (-1, -2 и т.д.).
        """
        base_slug = generate_slug(title)
        final_slug = base_slug
        counter = 0

        while await self.problem_repo.check_slug_exists(final_slug):
            counter += 1
            final_slug = f"{base_slug}-{counter}"

            if counter > 1000:
                # Меры предосторожности от бесконечного цикла, если что-то пошло не так
                raise Exception("Ошибка генерации slug: превышено 1000 попыток.")

        return final_slug

    async def create_problem(self, problem_data: ProblemCreate, user_id: uuid.UUID) -> Problem:
        """Бизнес-логика создания задачи (генерация slug, сохранение через репозиторий)."""

        unique_slug = await self._generate_unique_slug(problem_data.title)
        problem_dict = problem_data.dict(exclude={"examples", "test_cases"})


        problem_dict["user_id"] = user_id
        problem_dict["slug"] = unique_slug


        examples_data = [ex.dict() for ex in problem_data.examples]
        test_cases_data = [test.dict() for test in problem_data.test_cases]

        return await self.problem_repo.create_problem(problem_dict, examples_data, test_cases_data)

    async def list_public_problems(self) -> List[Problem]:
        """Получает список всех опубликованных задач."""
        return await self.problem_repo.list_public_problems()


    async  def get_problem_by_ids(self, problem_id: uuid.UUID) -> Optional[Problem]:

        return await self.problem_repo.get_problem_by_id(problem_id)

    async def update_problem(self, problem_id: uuid.UUID, problem_data: ProblemUpdate) -> Optional[Problem]:
        data = problem_data.dict(exclude_unset=True)
        return await self.problem_repo.update_problem(problem_id, data)


    # async def get_problem_by_id(self, problem_id) -> Optional[Problem]: ...
    # async def update_problem(self, problem_id, data) -> Optional[Problem]: ...
    # async def get_problem_statistics(self, problem_id) -> dict:
    #   # Здесь можно использовать self.submission_repo для вызова статистики!
    #   return await self.problem_repo.get_problem_statistics(problem_id)