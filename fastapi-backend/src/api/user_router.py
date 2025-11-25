
# fastapi-backend/src/api/user_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import  Dict
from ..database import get_db
from ..schemas.user_schemas import  UserResponse, CreateUserRequest, UpdateUserRequest
from ..repository.problem_repository import ProblemRepository
from  ..repository.submission_repository import  SubmissionRepository
from ..services.problem_service import ProblemService
from  ..services.submission_service import SubmissionService
from ..services.user_service import UserService
from  ..repository.user_repository import UserRepository
from ..core.security import  get_current_user, require_role
from ..models.user_models import User
from typing import List, Optional
import uuid


users = APIRouter(prefix="/api/users", tags=["users"])



async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return  UserService(user_repo)

# async def get_admin_user_service(repo: UserRepository = Depends(get_user_repository)) -> AdminUSerService:
#
#     return AdminUSerService(repo)

@users.get("/me", response_model=UserResponse)
async def get_current_user_profile(
        current_user: User = Depends(get_current_user)
):
    return current_user

@users.get("/{user_id}", response_model=UserResponse)
async def get_current_user_profile(
        user_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        service: UserService = Depends(get_user_service)
):
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@users.put("/me", response_model=UserResponse)
async def update_current_user(
        data: UpdateUserRequest,
        current_user: User = Depends(get_current_user),
        service: UserService = Depends(get_user_service)
):
    """Обновить свой профиль"""
    if data.email and data.email != current_user.email:
        if not service.validate_email(data.email):
            raise HTTPException(status_code=400, detail="Некорректный email")
        existing = await service.get_user_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    updated_user = await service.update_user(current_user.id, data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated_user

@users.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """Получить профиль пользователя по username"""
    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user