# fastapi-backend/src/schemas/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal, Optional
import uuid
from ..models.base import DifficultyLevel, CheckerType

SUPPORTED_LANGUAGES = Literal["python", "java", "cpp", "javascript"]

class TestCaseCreate(BaseModel):
    input_data: str
    output_data: str
    is_sample: bool = Field(False, description="Если True, тест виден студенту.")

class ExampleCreate(BaseModel):
    input_data: str
    output_data: str
    explanation: Optional[str] = None

class ProblemCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    difficulty: DifficultyLevel 
    checker_type: CheckerType = CheckerType.EXACT 
    examples: List[ExampleCreate] = []
    test_cases: List[TestCaseCreate] = Field(..., min_items=1)
    is_public: bool = False

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    difficulty: Optional[DifficultyLevel] = None
    checker_type: Optional[CheckerType] = None
    is_public: Optional[bool] = None

    class Config:
        from_attributes = True
    
    
class SubmissionCreate(BaseModel):
    problem_id: uuid.UUID = Field(..., description="ID задачи.")
    language: SUPPORTED_LANGUAGES = Field(..., description="Язык программирования.")
    code: str = Field(..., min_length=10, description="Исходный код решения.")
    
class SubmissionResponse(BaseModel):
    submission_id: uuid.UUID
    status: str
    message: str
    final_status: str

    
class ExecutionTestInput(BaseModel):
    id: str
    input_data: str
    expected_output: str

class TestResultGo(BaseModel):
    id: str
    status: str
    is_passed: bool
    actual_output: str
    execution_time_ms: int
    memory_used_mb: int
    details: str

class ExecutionResponseGo(BaseModel):
    submission_id: str
    final_status: str
    max_time_ms: int
    max_memory_mb: int
    error_message: Optional[str] = None
    test_results: List[TestResultGo]

class ProblemBase(BaseModel):
    """Базовая схема для отображения задачи в списке."""
    id: uuid.UUID
    title: str
    slug: str
    difficulty: DifficultyLevel
    is_public: bool

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    rating: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=8, max_length=72)
    role: Literal["student", "teacher", "admin"] = "student"
    full_name: Optional[str] = None

class LoginData(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

