# src/schemas/group_schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="CS-101 Introduction")
    description: Optional[str] = None

class AddMemberRequest(BaseModel):
    identifier: str = Field(..., description="Email или Username студента")

class CreateAssignmentRequest(BaseModel):
    problem_id: UUID
    deadline: datetime



class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    teacher_id: UUID
    student_count: int = 0 # SQLAlchemy column_property заполнит это
    created_at: datetime

class AssignmentResponse(BaseModel):
    """Для таблицы активных заданий преподавателя"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_name: str
    problem_title: str
    deadline: datetime
    created_at: datetime

class StudentAssignmentDTO(BaseModel):
    """Для списка 'Мои задания' у студента"""
    model_config = ConfigDict(from_attributes=True)

    assignment_id: UUID
    group_name: str
    problem_id: UUID
    problem_title: str
    deadline: datetime
    is_overdue: bool