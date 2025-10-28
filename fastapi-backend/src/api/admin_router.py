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
from ..services.admin_service import AdminUserService
from  ..repository.user_repository import UserRepository
from ..core.security import  get_current_user, require_role
from ..models.user_models import User
from typing import List, Optional
import uuid


router = APIRouter(prefix="/api/admin", tags=["admin"])



async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_admin_user_service(repo: UserRepository = Depends(get_user_repository)) -> AdminUserService:

    return AdminUserService(repo)


@router.get("", response_model=list[UserResponse], dependencies=[Depends(require_role("ADMIN"))])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role: str = Query(None),
    service: AdminUserService = Depends(get_admin_user_service)
):
    """Получить список всех пользователей (только ADMIN)"""
    users = await service.list_users(skip, limit, role)
    return users
