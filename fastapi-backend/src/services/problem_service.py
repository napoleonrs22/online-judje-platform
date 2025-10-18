# fastapi-backend/src/services/problem_service.py

from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import re
import os
import uuid
from fastapi import HTTPException
from starlette import status
from typing import List

from ..schemas.schemas import SubmissionCreate, ExecutionResponseGo, SubmissionResponse, ExecutionTestInput, ProblemCreate
from ..models.db_models import Submission, SubmissionStatus, Problem
from ..repository.problem_repository import ProblemRepository
from  ..repository.submission_repository import SubmissionRepository

CODE_EXECUTION_URL = os.getenv("CODE_EXECUTION_URL", "http://code-executor:8001/execute")

def generate_slug(title: str) -> str:
    """Генерация URL-friendly slug из названия"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    
    if not slug:
        return 'problem-' + str(uuid.uuid4())[:8]
        
    return slug


class ProblemService:
    """Сервис, содержащий бизнес-логику для Задач и Отправок."""
    
    def __init__(self, problem_repo: ProblemRepository, submission_repo: SubmissionRepository):
        self.problem_repo = problem_repo
        self.submission_repo = submission_repo

    async def create_problem(self, problem_data: ProblemCreate) -> Problem:
        """Бизнес-логика создания задачи (генерация slug, сохранение через репозиторий)."""

        problem_dict = problem_data.dict(exclude={"examples", "test_cases"})

        # 🔥 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавление временного user_id
        # В реальном приложении здесь был бы user_id, полученный через Depends(current_user)
        problem_dict["user_id"] = uuid.uuid4()

        problem_dict["slug"] = generate_slug(problem_data.title)

        examples_data = [ex.dict() for ex in problem_data.examples]
        test_cases_data = [test.dict() for test in problem_data.test_cases]

        return await self.problem_repo.create_problem(problem_dict, examples_data, test_cases_data)

    async def submit_solution_to_go(self, submission_data: SubmissionCreate) -> SubmissionResponse:
        """Обрабатывает всю логику отправки решения на Go-Executor (Бизнес-логика)."""
        
        problem = await self.problem_repo.get_problem_by_id_with_tests(submission_data.problem_id)
        
        if not problem or not problem.is_public:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена или не опубликована")

        test_cases_data = [
            ExecutionTestInput(
                id=str(t.id), 
                input_data=t.input_data, 
                expected_output=t.output_data
            ).dict() 
            for t in problem.test_cases
        ]
        
        if not test_cases_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Задача не содержит тестовых данных для проверки.")

        db_submission = Submission(
            problem_id=submission_data.problem_id,
            language=submission_data.language,
            code=submission_data.code,
            status=SubmissionStatus.PENDING
        )
        db_submission = await self.submission_repo.create_submission(db_submission)

        go_payload = {
            "submission_id": str(db_submission.id),
            "language": submission_data.language,
            "code": submission_data.code,
            "time_limit": problem.time_limit,
            "memory_limit": problem.memory_limit,
            "test_cases": test_cases_data, 
            "checker_type": problem.checker_type.value,
            "custom_checker_code": None,
        }
        
        final_status = SubmissionStatus.PENDING
        message = "Решение принято в обработку."

        try:
            db_submission.status = SubmissionStatus.IN_PROGRESS
            await self.submission_repo.update_submission(db_submission) 
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(CODE_EXECUTION_URL, json=go_payload)
                response.raise_for_status()
                
                judge_result = ExecutionResponseGo.parse_obj(response.json())
                
                db_submission.status = SubmissionStatus(judge_result.final_status)
                db_submission.execution_time = judge_result.max_time_ms
                db_submission.memory_used = judge_result.max_memory_mb
                db_submission.test_results = [res.dict() for res in judge_result.test_results]
                db_submission.error_message = judge_result.error_message
                
                final_status = db_submission.status
                message = f"Вердикт: {final_status.value}."

        except httpx.ConnectError:
            final_status = SubmissionStatus.INTERNAL_ERROR
            message = f"Ошибка: Go-Executor недоступен по адресу {CODE_EXECUTION_URL}"
        except Exception as e:
            final_status = SubmissionStatus.INTERNAL_ERROR
            message = f"Ошибка при проверке: {str(e)}"
        
        if db_submission.status == SubmissionStatus.IN_PROGRESS:
            db_submission.status = final_status
            db_submission.error_message = message

        db_submission = await self.submission_repo.update_submission(db_submission)

        return SubmissionResponse(
            submission_id=db_submission.id, 
            status=db_submission.status.value,
            final_status=db_submission.status.value,
            message=message
        )