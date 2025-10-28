#user_schemas



from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal, Optional
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


class UpdateUserRequest(BaseModel):
    """Схема для обновления данных пользователя (частичное обновление)."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=20)
    full_name: Optional[str] = None
    role: Optional[UserRole] = None # Изменение роли доступно только Admin
    university_id: Optional[str] = None
    # password: Optional[str] = Field(None, min_length=8, max_length=72)

    class Config:
        # Позволяет не включать все поля при обновлении
        extra = "forbid"


class UserRatingUpdate(BaseModel):
    """Схема для изменения рейтинга пользователя (используется AdminService)."""
    # Дельта (разница) рейтинга, а не новое значение
    rating_delta: int = Field(..., description="Разница, на которую нужно изменить рейтинг (может быть отрицательной).")




class UserResponse(BaseModel):
    """Полная схема пользователя для ответа API."""
    id: UUID
    username: str
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    rating: int
    university_id: Optional[str] = None
    # created_at, updated_at

    class Config:

        from_attributes = True