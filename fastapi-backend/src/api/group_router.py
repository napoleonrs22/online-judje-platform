# src/api/group_router.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.user_models import User
from ..services.auth_service import get_current_teacher

from ..schemas.group_schemas import (
    GroupCreate, GroupResponse, AddMemberRequest,
    CreateAssignmentRequest, AssignmentResponse
)
from ..repository.group_repository import GroupRepository
from ..repository.user_repository import UserRepository
from ..repository.problem_repository import ProblemRepository
from ..services.group_service import GroupService

router = APIRouter(prefix="/api/groups", tags=["Teacher Groups"])


# ==========================================
# 1. Dependency Injection (Сборка Сервиса)
# ==========================================

async def get_group_repository(db: AsyncSession = Depends(get_db)) -> GroupRepository:
    return GroupRepository(db)


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_problem_repository(db: AsyncSession = Depends(get_db)) -> ProblemRepository:
    return ProblemRepository(db)


# "Фабрика", которая собирает GroupService со всеми нужными репозиториями
async def get_group_service(
        group_repo: GroupRepository = Depends(get_group_repository),
        user_repo: UserRepository = Depends(get_user_repository),
        problem_repo: ProblemRepository = Depends(get_problem_repository)
) -> GroupService:
    return GroupService(group_repo, user_repo, problem_repo)


# ==========================================
# 2. Endpoints (Контроллеры)
# ==========================================

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
        data: GroupCreate,
        user: User = Depends(get_current_teacher),
        service: GroupService = Depends(get_group_service)
):
    """
    Создать новую учебную группу.
    """
    return await service.create_group(user.id, data)


@router.get("/", response_model=List[GroupResponse])
async def list_groups(
        user: User = Depends(get_current_teacher),
        service: GroupService = Depends(get_group_service)
):
    """
    Получить список групп, где пользователь является преподавателем.
    """
    return await service.list_teacher_groups(user.id)


@router.post("/{group_id}/members", status_code=status.HTTP_200_OK)
async def add_student(
        group_id: str,
        data: AddMemberRequest,
        user: User = Depends(get_current_teacher),
        service: GroupService = Depends(get_group_service)
):
    """
    Добавить студента в группу по email или username.
    """
    try:
        g_uuid = UUID(group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    return await service.add_student(g_uuid, user.id, data)


@router.get("/{group_id}/students/count", status_code=status.HTTP_200_OK)
async def get_student_count(
        group_id: str,
        user: User = Depends(get_current_teacher),
        service: GroupService = Depends(get_group_service)
):
    """
    Получить количество студентов в группе.
    """
    try:
        g_uuid = UUID(group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    count = await service.get_student_count(g_uuid)
    return {"group_id": group_id, "student_count": count}


# --- Assignments (Назначение задач) ---

@router.post("/{group_id}/assignments", response_model=AssignmentResponse)
async def assign_task(
        group_id: str,
        data: CreateAssignmentRequest,
        user: User = Depends(get_current_teacher),
        service: GroupService = Depends(get_group_service)
):
    """
    Назначить задачу группе с дедлайном.
    """
    try:
        g_uuid = UUID(group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    return await service.create_assignment(g_uuid, user.id, data)


@router.get("/assignments/active", response_model=List[AssignmentResponse])
async def list_active_assignments(
        user: User = Depends(get_current_teacher),
        service: GroupService = Depends(get_group_service)
):
    """
    Получить все активные назначения задач преподавателя.
    """
    return await service.list_teacher_assignments(user.id)


@router.delete("/assignments/{assignment_id}")
async def revoke_assignment(
        assignment_id: str,
        user: User = Depends(get_current_teacher),
        service: GroupService = Depends(get_group_service)
):
    """
    Отменить назначение задачи (удалить дедлайн для группы).
    """
    try:
        a_uuid = UUID(assignment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    return await service.revoke_assignment(a_uuid, user.id)