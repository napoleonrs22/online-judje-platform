from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Literal
from ..database import get_db
from ..schemas.user_schemas import  UserResponse, CreateUserRequest, UpdateUserRequest
from ..repository.problem_repository import ProblemRepository
from  ..repository.submission_repository import  SubmissionRepository
from ..services.problem_service import ProblemService
from  ..services.submission_service import SubmissionService
from ..services.user_service import UserService
from ..services.admin_service import AdminUserService
from  ..repository.user_repository import UserRepository
from ..services.auth_service import get_current_user
from ..core.security import require_roles
from ..models.user_models import User
from typing import List, Optional
import uuid


router = APIRouter(prefix="/api/admin", tags=["admin"])



async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_admin_user_service(repo: UserRepository = Depends(get_user_repository)) -> AdminUserService:

    return AdminUserService(repo)


@router.get("", response_model=list[UserResponse], dependencies=[Depends(require_roles("ADMIN"))])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role: str = Query(None),
    service: AdminUserService = Depends(get_admin_user_service)
):
    """Получить список всех пользователей (только ADMIN)"""
    users = await service.list_users(skip, limit, role)
    return users

@router.post("", response_model=UserResponse, dependencies=[Depends(require_roles("ADMIN"))])
async def create_user_admin(
        data: CreateUserRequest,
        service: AdminUserService = Depends(get_admin_user_service)
):
    try:
        user = await service.create_user_as_admin(data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}", response_model= UserResponse, dependencies=[Depends(require_roles("ADMIN"))])

async def update_user_admin(
        user_id: uuid.UUID,
        data: UpdateUserRequest,
        service: AdminUserService = Depends(get_admin_user_service)
):
    try:
        user = await service.update_user_as_admin(user_id, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", dependencies=[Depends(require_roles("ADMIN"))])
async def delete_user_admin(
        user_id: uuid.UUID,
        service: AdminUserService = Depends(get_admin_user_service)
):
    try:
        await service.delete_user_as_admin(user_id)
        return {"message": "Пользователь удален"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}/role", response_model=UserResponse, dependencies=[Depends(require_roles("ADMIN"))])
async  def change_user_role(
        user_id: uuid.UUID,
        new_role: Literal["STUDENT", "TEACHER", "ADMIN"] = Query(...),
        service: AdminUserService = Depends(get_admin_user_service)
):
    try:
        updated_user = await service.change_user_role(user_id, new_role)
        if not updated_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

