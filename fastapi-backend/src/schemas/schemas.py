# fastapi-backend/src/schemas/schemas.py

from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import List, Literal, Optional
from datetime import datetime
import uuid

from ..models.base import DifficultyLevel, CheckerType

SUPPORTED_LANGUAGES = Literal["python", "java", "cpp", "javascript"]


# ============ USER SCHEMAS ============

class UserBase(BaseModel):
    """Базовая схема пользователя."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    rating: int


class UserCreate(BaseModel):
    """Создание нового пользователя."""
    email: EmailStr
    username: str
    password: str = Field(..., min_length=8, max_length=72)
    role: Literal["student", "teacher", "admin"] = "student"
    full_name: Optional[str] = None


class LoginData(BaseModel):
    """Данные для входа."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT токен."""
    access_token: str
    token_type: str = "bearer"


# ============ TEST CASE & EXAMPLE SCHEMAS ============

class TestCaseCreate(BaseModel):
    """Создание тестового случая."""
    input_data: str
    output_data: str
    is_sample: bool = Field(False, description="Если True, тест виден студенту.")


class TestCaseResponse(BaseModel):
    """Ответ с тестовым случаем."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    problem_id: uuid.UUID
    input_data: str
    output_data: str
    is_sample: bool
    order_index: int


class ExampleCreate(BaseModel):
    """Создание примера."""
    input_data: str
    output_data: str
    explanation: Optional[str] = None


class ExampleResponse(BaseModel):
    """Ответ с примером."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    problem_id: uuid.UUID
    input_data: str
    output_data: str
    explanation: Optional[str] = None


# ============ PROBLEM SCHEMAS ============

class ProblemBase(BaseModel):
    """Базовая схема для отображения задачи в списке."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    difficulty: DifficultyLevel
    is_public: bool


class ProblemCreate(BaseModel):
    """Создание новой задачи."""
    title: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    difficulty: DifficultyLevel
    checker_type: CheckerType = CheckerType.EXACT
    examples: List[ExampleCreate] = []
    test_cases: List[TestCaseCreate] = Field(..., min_items=1)
    is_public: bool = False


class ProblemUpdate(BaseModel):
    """Обновление задачи."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    slug: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    difficulty: Optional[DifficultyLevel] = None
    checker_type: Optional[CheckerType] = None
    is_public: Optional[bool] = None


class ProblemResponse(ProblemBase):
    """Полный ответ о задаче."""
    user_id: uuid.UUID
    description:str
    created_at: datetime
    updated_at: Optional[datetime] = None
    examples: List[ExampleResponse] = []
    test_cases: List[TestCaseResponse] = []


# ============ SUBMISSION SCHEMAS ============

class SubmissionCreate(BaseModel):
    """Создание новой попытки решения."""
    problem_id: uuid.UUID = Field(..., description="ID задачи.")
    language: SUPPORTED_LANGUAGES = Field(..., description="Язык программирования.")
    code: str = Field(..., min_length=10, description="Исходный код решения.")


class SubmissionResponse(BaseModel):
    """Ответ с информацией о попытке решения."""
    model_config = ConfigDict(from_attributes=True)

    submission_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    problem_id: Optional[uuid.UUID] = None
    status: str
    message: str
    final_status: str
    created_at: Optional[datetime] = None
    language: Optional[str] = None
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None


# ============ GO-EXECUTOR SCHEMAS ============

class ExecutionTestInput(BaseModel):
    """Входные данные теста для Go-Executor."""
    id: str
    input_data: str
    expected_output: str


class TestResultGo(BaseModel):
    """Результат выполнения одного теста от Go-Executor."""
    id: str
    status: str
    is_passed: bool
    actual_output: str
    execution_time_ms: int
    memory_used_mb: int
    details: str


class ExecutionResponseGo(BaseModel):
    """Полный ответ от Go-Executor."""
    submission_id: str
    final_status: str
    max_time_ms: int
    max_memory_mb: int
    error_message: Optional[str] = None
    test_results: List[TestResultGo]