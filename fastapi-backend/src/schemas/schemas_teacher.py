#schemas_teacher
from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal, Optional
from datetime import datetime
from ..schemas.schemas import ProblemBase,ExampleResponse,TestCaseResponse
import uuid
from ..models.base import DifficultyLevel, CheckerType


class ProblemResponse(ProblemBase):

    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    examples: List[ExampleResponse] = []
    test_cases: List[TestCaseResponse] = []

    class Config:
        from_attributes = True