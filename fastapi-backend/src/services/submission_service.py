import httpx
import os
import uuid
from fastapi import HTTPException
from starlette import status
from typing import List, Optional

from ..schemas.schemas import SubmissionCreate, ExecutionResponseGo, SubmissionResponse, ExecutionTestInput
from ..models.submission_models import Submission
from ..models.problem_models import Problem, TestCase
from ..models.base import SubmissionStatus
from ..repository.problem_repository import ProblemRepository
from ..repository.submission_repository import SubmissionRepository


CODE_EXECUTION_URL = os.getenv("CODE_EXECUTION_URL", "http://code-executor:8001/execute")


class SubmissionService:

    def __init__(self, submission_repository: SubmissionRepository, problem_repository: ProblemRepository):
        self.submission_repository = submission_repository
        self.problem_repository = problem_repository

    async def submit_solution(self, submission_data: SubmissionCreate, user_id: uuid.UUID) -> SubmissionResponse:

        problem_with_tests: Optional[Problem] = await self.problem_repository.get_problem_by_id_with_tests(submission_data.problem_id)

        if not problem_with_tests or not problem_with_tests.is_public:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Задача не найдена или не опубликована")


        db_submission = Submission(
            user_id=user_id,
            problem_id=submission_data.problem_id,
            language=submission_data.language,
            code=submission_data.code,
            status=SubmissionStatus.PENDING,
        )

        db_submission = await self.submission_repository.create_submission(db_submission)

        test_case_inputs = [
            ExecutionTestInput(
                id=str(test.id),
                input_data=test.input_data,
                expected_output=test.output_data
            )
            for test in problem_with_tests.test_cases
        ]

        go_payload = SubmissionStatus.IN_PROGRESS
        message = ""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Отправляем задачу на проверку
                response = await client.post(CODE_EXECUTION_URL, json=go_payload)
                response.raise_for_status()  # Выбросит исключение для 4xx/5xx ошибок

                # Парсинг ответа
                judge_result = ExecutionResponseGo.parse_obj(response.json())

                # 5. Обработка результатов Go (Бизнес-логика)
                db_submission.status = SubmissionStatus(judge_result.final_status)
                db_submission.execution_time = judge_result.max_time_ms
                db_submission.memory_used = judge_result.max_memory_mb
                db_submission.test_results = [res.dict() for res in judge_result.test_results]  # Pydantic в dict
                db_submission.error_message = judge_result.error_message

                final_status = db_submission.status
                message = f"Вердикт: {final_status.value}."

        except httpx.ConnectError:
            final_status = SubmissionStatus.INTERNAL_ERROR
            message = f"Ошибка: Go-Executor недоступен по адресу {CODE_EXECUTION_URL}"
        except Exception as e:
            final_status = SubmissionStatus.INTERNAL_ERROR
            message = f"Критическая ошибка при проверке: {type(e).__name__}: {str(e)}"

        if db_submission.status == SubmissionStatus.PENDING or db_submission.status == SubmissionStatus.IN_PROGRESS:
            db_submission.status = final_status
            db_submission.error_message = message

        db_submission = await self.submission_repository.update_submission(db_submission)


        return SubmissionResponse(
            submission_id=db_submission.id,
            status=db_submission.status.value,
            final_status=db_submission.final_status.value,
            message=message,
        )
