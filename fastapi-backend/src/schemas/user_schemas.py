

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from uuid import UUID
from datetime import  datetime
from ..models.user_models import Role


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=72)
    role: Role = Field(..., description="Роль пользователя: student, teacher или admin.")
    full_name: Optional[str] = None
    university_id: Optional[str] = None

    @field_validator('role', mode='before')
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, str):
            v = v.strip().lower()
        if v not in [r.value for r in Role]:
            raise ValueError(f"Некорректная роль: {v}. Допустимые значения: {[r.value for r in Role]}")
        return Role(v)


class UpdateUserRequest(BaseModel):

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=20)
    full_name: Optional[str] = None
    role: Optional[Role] = Field(None, description="Изменение роли доступно только администраторам.")
    university_id: Optional[str] = None

    @field_validator('role', mode='before')
    @classmethod
    def normalize_role(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip().lower()
        if v not in [r.value for r in Role]:
            raise ValueError(f"Некорректная роль: {v}. Допустимые значения: {[r.value for r in Role]}")
        return Role(v)

    class Config:
        extra = "forbid"


class UserRatingUpdate(BaseModel):
    rating_delta: int = Field(
        ...,
        description="Изменение рейтинга (может быть отрицательным)."
    )


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    rating: int
    university_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('role', mode='before')
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, Role):
            return v.value
        if isinstance(v, str):
            return v.strip().lower()
        raise ValueError("Invalid role")

    model_config = {
        "from_attributes": True,
        "exclude": {"hashed_password", "refresh_token_hash"}
    }