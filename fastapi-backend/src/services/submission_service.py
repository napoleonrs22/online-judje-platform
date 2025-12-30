import httpx
import os
import uuid
from fastapi import HTTPException
from starlette import status
from typing import Optional, List

from ..schemas.schemas import (
    SubmissionCreate,
    ExecutionResponseGo,
    SubmissionResponse,
    ExecutionTestInput,

)
from ..models.problem_models import Problem
from ..models.base import SubmissionStatus
from ..repository.problem_repository import ProblemRepository
from ..repository.submission_repository import SubmissionRepository

CODE_EXECUTION_URL = os.getenv("CODE_EXECUTION_URL", "http://code-executor:8001/execute")


class SubmissionService:
    def __init__(
            self,
            submission_repository: SubmissionRepository,
            problem_repository: ProblemRepository,
    ):
        self.submission_repository = submission_repository
        self.problem_repository = problem_repository

    async def submit_solution(
            self, submission_data: SubmissionCreate, user_id: uuid.UUID
    ) -> SubmissionResponse:
        """Отправить решение на проверку."""

        # Получаем задачу с тестами
        problem_with_tests: Optional[Problem] = (
            await self.problem_repository.get_problem_by_id_with_tests(
                submission_data.problem_id
            )
        )

        if not problem_with_tests or not problem_with_tests.is_public:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена или не опубликована",
            )

        db_submission = await self.submission_repository.create_submission(
            user_id=user_id,
            problem_id=submission_data.problem_id,
            language=submission_data.language,
            code=submission_data.code,
        )

        test_case_inputs = [
            ExecutionTestInput(
                id=str(test.id),
                input_data=test.input_data,
                expected_output=test.output_data,
            ).model_dump()
            for test in problem_with_tests.test_cases
        ]

        go_payload = {
            "submission_id": str(db_submission.id),
            "language": submission_data.language,
            "code": submission_data.code,
            "time_limit": problem_with_tests.time_limit or 2000,
            "memory_limit": problem_with_tests.memory_limit or 256,
            "checker_type": problem_with_tests.checker_type.value,
            "test_cases": test_case_inputs,
        }

        message = ""
        final_status = SubmissionStatus.INTERNAL_ERROR

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(CODE_EXECUTION_URL, json=go_payload)
                response.raise_for_status()

                judge_result = ExecutionResponseGo.model_validate(response.json())

                # Обновляем submission с результатами
                db_submission.status = SubmissionStatus(judge_result.final_status)
                db_submission.execution_time = judge_result.max_time_ms
                db_submission.memory_used = judge_result.max_memory_mb
                db_submission.test_results = [
                    res.model_dump() for res in judge_result.test_results
                ]
                db_submission.error_message = judge_result.error_message

                final_status = db_submission.status
                message = f"Вердикт: {final_status.value}"

        except httpx.ConnectError:
            message = f"Ошибка: Go-Executor недоступен по адресу {CODE_EXECUTION_URL}"
            final_status = SubmissionStatus.INTERNAL_ERROR
        except Exception as e:
            message = f"Критическая ошибка при проверке: {type(e).__name__}: {str(e)}"
            final_status = SubmissionStatus.INTERNAL_ERROR

        db_submission.status = final_status
        db_submission.error_message = message
        db_submission = await self.submission_repository.update_submission(db_submission)

        return SubmissionResponse(
            submission_id=db_submission.id,
            user_id=db_submission.user_id,
            problem_id=db_submission.problem_id,
            status=db_submission.status.value,
            message=db_submission.error_message or f"Вердикт: {db_submission.status.value}",
            final_status=db_submission.status.value,
            created_at=db_submission.created_at,
            language=db_submission.language,
            execution_time=db_submission.execution_time,
            memory_used=db_submission.memory_used,
            test_results=db_submission.test_results or [],
        )

    async def delete_submission(self, submission_id: str, user_id: uuid.UUID) -> dict:
        """Удалить submission (только PENDING)."""
        if not submission_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="submission_id не указан",
            )

        try:
            submission_uuid = uuid.UUID(submission_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неправильный формат uuid"
            )

        existing_submission = await self.submission_repository.get_submission_by_id(submission_uuid)

        if not existing_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission не найден",
            )

        if existing_submission.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете удалить чужой submission",
            )

        if existing_submission.status != SubmissionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Удалять разрешено только PENDING. Текущий статус: {existing_submission.status.value}",
            )

        deleted_count = await self.submission_repository.delete_submissions([submission_uuid])

        return {
            "message": "Submission успешно удален",
            "submission_id": str(submission_id),
            "status": "DELETED",
        }

    async def get_user_submissions(
            self, user_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> List[SubmissionResponse]:
        """Получить все submissions пользователя."""
        db_submissions = await self.submission_repository.get_user_submissions(
            user_id, skip=skip, limit=limit
        )

        return [
            SubmissionResponse(
                submission_id=sub.id,
                user_id=sub.user_id,
                problem_id=sub.problem_id,
                status=sub.status.value,
                message=sub.error_message or f"Статус: {sub.status.value}",
                final_status=sub.status.value,
                created_at=sub.created_at,
                language=sub.language,
                execution_time=sub.execution_time,
                memory_used=sub.memory_used,
                test_results=sub.test_results or [],
            )
            for sub in db_submissions
        ]

    async def get_submission(self, submission_id: str, user_id: uuid.UUID) -> SubmissionResponse:
        """Получить информацию о submission."""
        if not submission_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="submission_id не указан",
            )
        try:
            submission_uuid = uuid.UUID(submission_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неправильный формат uuid для submission_id",
            )

        db_submission = await self.submission_repository.get_submission_by_id(submission_uuid)

        if not db_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission {submission_uuid} не найден",
            )

        if db_submission.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете просмотреть чужой submission",
            )
        return SubmissionResponse(
            submission_id=db_submission.id,
            user_id=db_submission.user_id,
            problem_id=db_submission.problem_id,
            status=db_submission.status.value,
            message=db_submission.error_message or f"Статус: {db_submission.status.value}",
            final_status=db_submission.status.value,
            created_at=db_submission.created_at,
            language=db_submission.language,
            execution_time=db_submission.execution_time,
            memory_used=db_submission.memory_used,
            test_results=db_submission.test_results or [],
        )
