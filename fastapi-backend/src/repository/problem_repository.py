# fastapi-backend/src/repository/problem_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
import uuid

from ..models.db_models import Problem, Submission, SubmissionStatus, TestCase, Example

class ProblemRepository:
    """Репозиторий для доступа к данным о Задачах и их Тестах."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_problem_by_id_with_tests(self, problem_id: uuid.UUID) -> Optional[Problem]:
        """Получает задачу по ID, включая связанные тест-кейсы (для выполнения)."""
        stmt = (
            select(Problem)
            .where(Problem.id == problem_id)
            .options(
                selectinload(Problem.test_cases),
                selectinload(Problem.examples)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def create_problem(self, problem_data: dict, examples_data: List[dict], test_cases_data: List[dict]) -> Problem:
        """Создает новую задачу, включая тесты и примеры."""
        
        db_problem = Problem(**problem_data)
        self.db.add(db_problem)
        await self.db.flush() 

        problem_id = db_problem.id
        
        db_examples = [Example(problem_id=problem_id, **ex_data) for ex_data in examples_data]
        db_tests = [
            TestCase(problem_id=problem_id, order_index=idx, **test_data) 
            for idx, test_data in enumerate(test_cases_data)
        ]
        
        self.db.add_all(db_examples)
        self.db.add_all(db_tests)
        
        await self.db.commit()
        await self.db.refresh(db_problem)
        return db_problem

    async def list_public_problems(self) -> List[Problem]:
        """Получает список всех опубликованных задач."""
        stmt = (
            select(Problem).where(Problem.is_public == True)
            .options(
                selectinload(Problem.test_cases),
                selectinload(Problem.examples)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_test_cases(self, problem_id:uuid.UUID) ->List[TestCase]:

        stmt = select(TestCase).where(TestCase.problem_id == problem_id).order_by(TestCase.order_index).limit(100)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_problem_by_id(self,problem_id:uuid.UUID) ->Optional[Problem]:

        stmt =(
            select(Problem).where(Problem.id == problem_id)
            .options(
                selectinload(Problem.test_cases),
            )
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    



        


class SubmissionRepository:
    """Репозиторий для доступа к данным об Отправках."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_submission(self, submission: Submission):
        """Создает новую запись об отправке (PENDING)."""
        self.db.add(submission)
        await self.db.flush()
        return submission

    async def update_submission(self, submission: Submission):
        """Обновляет статус и результаты отправки (COMMITTED)."""

        await self.db.commit()
        await self.db.refresh(submission)
        return submission