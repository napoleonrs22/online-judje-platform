# fastapi-backend/src/services/problem_service.py

import re
import uuid
from typing import List, Optional

from ..schemas.schemas import ProblemCreate
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

    async def create_problem(self, problem_data: ProblemCreate, user_id: uuid.UUID) -> Problem:
        """Бизнес-логика создания задачи (генерация slug, сохранение через репозиторий)."""


        problem_dict = problem_data.dict(exclude={"examples", "test_cases"})


        problem_dict["user_id"] = user_id
        problem_dict["slug"] = generate_slug(problem_data.title)

        examples_data = [ex.dict() for ex in problem_data.examples]
        test_cases_data = [test.dict() for test in problem_data.test_cases]

        return await self.problem_repo.create_problem(problem_dict, examples_data, test_cases_data)

    async def list_public_problems(self) -> List[Problem]:
        """Получает список всех опубликованных задач."""
        return await self.problem_repo.list_public_problems()


    # async def get_problem_by_id(self, problem_id) -> Optional[Problem]: ...
    # async def update_problem(self, problem_id, data) -> Optional[Problem]: ...
    # async def get_problem_statistics(self, problem_id) -> dict:
    #   # Здесь можно использовать self.submission_repo для вызова статистики!
    #   return await self.problem_repo.get_problem_statistics(problem_id)