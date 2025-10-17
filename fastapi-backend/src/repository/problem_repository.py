# fastapi-backend/src/repository/problem_repo.py
from unittest import result

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
import uuid

from ..models.db_models import Problem, Submission, SubmissionStatus, TestCase, Example

class ProblemRepository:
    """Репозиторий для доступа к данным о Задачах и их Тестах."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_problem_by_id_with_tests(self, problem_id: uuid.UUID) -> Optional[Problem]:
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
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async  def delete_problem(self, problem_id:uuid.UUID) -> Optional[uuid.UUID]:

        stmt = delete(Problem).where(Problem.id  == problem_id).returning(Problem.id)

        result = await  self.db.execute(stmt)
        return result.scalars().first()

        if deleted_id:
            await self.db.close()
            return deleted_id

        return None



    async  def list_public_problems_with_filters(self, difficulty=None,skip=0, limit=50) -> List[Problem]:

        stmt = select(Problem).where(Problem.is_public == True)

        if difficulty:
            stmt = stmt.where(Problem.difficulty == difficulty)
        stmt = (
            stmt.order_by(Problem.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_user_problems(self, user_id:uuid.UUID) -> List[Problem]:

        stmt = (
            select(Problem).where(Problem.user_id == user_id)
            .order_by(Problem.created_at.desc())
            .limit(100)

        )

        result = await self.db.execute(stmt)
        return result.scalars().all()



    async def update_problem(self, problem_id:uuid.UUID, data: dict) -> Optional[Problem]:

        stmt = (
            select(Problem).where(Problem.id == problem_id)
        )

        result = await self.db.execute(stmt)

        db_problem = result.scalar_one_or_none()

        if db_problem is None:
            return None

        for key, value in data.items():
            if key not in ['id', 'created_at']:
                setattr(db_problem, key, value)

        await self.db.commit()

        await self.db.refresh(db_problem)
        return db_problem

    async def get_problem_statistics(self, problem_id:uuid.UUID) ->dict:


        total_submissions_stmt = (
            select(func.count(Submission.id))
            .where(Submission.problem_id == problem_id)
        )

        accepted_submissions_stmt = (
            select(func.count(Submission.id))
            .where(Submission.problem_id == problem_id)
            .where(Submission.status == SubmissionStatus.ACCEPTED)
        )

        avg_submissions_stmt = (
            select(
                func.avg(Submission.execution_time).label('avg_time'),
                func.avg(Submission.memory_used).label('avg_memory'),
            )
            .where(or_(
                Submission.status == SubmissionStatus.ACCEPTED,
                Submission.status == SubmissionStatus.WRONG_ANSWER,
            ))
        )

        total_submissions = (await self.db.execute(total_submissions_stmt)).scalar() or 0
        accepted_submissions = (await self.db.execute(accepted_submissions_stmt)).scalar() or 0
        avg_metrics_result = (await self.db.execute(avg_submissions_stmt)).one_or_none()


        avg_time = avg_metrics_result.avg_time if avg_metrics_result else None
        avg_memory = avg_metrics_result.avg_memory if avg_metrics_result else None

        if total_submissions > 0:
            success_rate = (accepted_submissions / total_submissions) * 100
        else:
            success_rate = 0

        return {
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'success_rate': round(success_rate, 2),
            'avg_time_ms': round(avg_time, 2) if avg_time else None,
            'avg_memory_mb': round(avg_memory, 2) if avg_memory else None,
        }

class SubmissionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_submission(self, submission: Submission):
        self.db.add(submission)
        await self.db.flush()
        return submission

    async def update_submission(self, submission: Submission):

        await self.db.commit()
        await self.db.refresh(submission)
        return submission