from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class GroupCreate(BaseModel):
    __tablename__ = "groups"

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None


class GroupResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    teacher_id: UUID
    created_at: datetime

    class Config:
        from_attributes =True


class AddMemberRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None


class CreateAssignmentRequest(BaseModel):
    problem_id: UUID
    deadline: datetime  # Фронтенд пришлет ISO формат даты


class AssignmentResponse(BaseModel):
    id: UUID
    group_name: str
    deadline: datetime
    created_at: datetime

    class Config:
        from_attributes = True