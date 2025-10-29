# ============== src/schemas/user_schemas.py ==============

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal, Optional
from uuid import UUID

UserRole = Literal["STUDENT", "TEACHER", "ADMIN"]

class CreateUserRequest(BaseModel):
    """Схема для создания нового пользователя (используется AdminService)."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=72)
    role: UserRole = Field(..., description="Роль пользователя.")
    full_name: Optional[str] = None
    university_id: Optional[str] = None

    @field_validator('role', mode='before')
    @classmethod
    def normalize_role(cls, v):
        if v is not None and isinstance(v, str):
            return v.upper()
        return v


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=20)
    full_name: Optional[str] = None
    role: Optional[UserRole] = None  # Изменение роли доступно только Admin
    university_id: Optional[str] = None
    # password: Optional[str] = Field(None, min_length=8, max_length=72)

    @field_validator('role', mode='before')
    @classmethod
    def normalize_role(cls, v):
        if v is not None and isinstance(v, str):
            return v.upper()
        return v

    class Config:
        # Позволяет не включать все поля при обновлении
        extra = "forbid"


class UserRatingUpdate(BaseModel):
    """Схема для изменения рейтинга пользователя (используется AdminService)."""
    # Дельта (разница) рейтинга, а не новое значение
    rating_delta: int = Field(
        ...,
        description="Разница, на которую нужно изменить рейтинг (может быть отрицательной)."
    )
class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    rating: int
    university_id: Optional[str] = None
    # created_at, updated_at можно добавить при необходимости
    class Config:
        from_attributes = True