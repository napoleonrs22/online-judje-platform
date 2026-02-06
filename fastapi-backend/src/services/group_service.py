# src/services/group_service.py

from uuid import UUID
from fastapi import HTTPException, status
from typing import List
from datetime import datetime, timezone

from ..repository.group_repository import GroupRepository
from ..repository.user_repository import UserRepository
from ..repository.problem_repository import ProblemRepository

from ..schemas.group_schemas import (
    GroupCreate, AddMemberRequest,
    CreateAssignmentRequest, AssignmentResponse,
    StudentAssignmentDTO
)
from ..models.group_models import Group, GroupAssignment


class GroupService:
    def __init__(
            self,
            group_repo: GroupRepository,
            user_repo: UserRepository,
            problem_repo: ProblemRepository
    ):
        self.group_repo = group_repo
        self.user_repo = user_repo
        self.problem_repo = problem_repo

    async def create_group(self, teacher_id: UUID, data: GroupCreate) -> Group:
        """Создание новой группы."""
        new_group = Group(
            teacher_id=teacher_id,
            name=data.name,
            description=data.description
        )
        return await self.group_repo.create_group(new_group)

    async def list_teacher_groups(self, teacher_id: UUID) -> List[Group]:
        """Получение списка групп преподавателя."""
        return await self.group_repo.get_by_teacher(teacher_id)

    async def add_student(self, group_id: UUID, teacher_id: UUID, data: AddMemberRequest):
        """Добавление студента в группу по email или username."""
        # 1. Проверяем группу
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Группа не найдена")

        # 2. Проверяем права (владелец группы)
        if group.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Вы не владелец этой группы")

        # 3. Ищем студента
        identifier = data.identifier.strip()
        student = await self.user_repo.get_user_by_email(identifier)
        if not student:
            student = await self.user_repo.get_user_by_username(identifier)

        if not student:
            raise HTTPException(status_code=404, detail=f"Студент '{identifier}' не найден")

        # 4. Добавляем
        await self.group_repo.add_student(group, student)
        return {"message": f"Студент {student.full_name or student.username} добавлен"}

    async def get_student_count(self, group_id: UUID) -> int:
        """Получить количество студентов в группе."""
        return await self.group_repo.get_student_count(group_id)

    async def create_assignment(self, group_id: UUID, teacher_id: UUID,
                                data: CreateAssignmentRequest) -> AssignmentResponse:
        """Назначение задачи группе с дедлайном."""
        # 1. Проверяем группу
        group = await self.group_repo.get_by_id(group_id)
        if not group or group.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Нет прав на эту группу")

        # 2. Проверяем задачу
        problem = await self.problem_repo.get_problem_by_id(data.problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        # 3. Очищаем таймзону для сохранения в Postgres (timestamp without time zone)
        # Postgres сохранит это время "как есть". Мы подразумеваем, что это UTC.
        deadline_naive = data.deadline.replace(tzinfo=None)

        assignment = GroupAssignment(
            group_id=group_id,
            problem_id=data.problem_id,
            deadline=deadline_naive
        )
        created = await self.group_repo.create_assignment(assignment)

        # 4. Восстанавливаем UTC метку для ответа API
        # Чтобы фронтенд видел 'Z' или '+00:00' и понимал, что это UTC
        deadline_aware = created.deadline.replace(tzinfo=timezone.utc)

        return AssignmentResponse(
            id=created.id,
            group_name=group.name,
            problem_title=problem.title,
            deadline=deadline_aware,
            created_at=created.created_at
        )

    async def list_teacher_assignments(self, teacher_id: UUID) -> List[AssignmentResponse]:
        """Получить все активные назначения преподавателя."""
        assignments = await self.group_repo.get_teacher_assignments(teacher_id)

        # Преобразуем naive даты из БД в aware UTC для корректного JSON ответа
        return [
            AssignmentResponse(
                id=a.id,
                group_name=a.group.name,
                problem_title=a.problem.title,
                deadline=a.deadline.replace(tzinfo=timezone.utc),
                created_at=a.created_at
            )
            for a in assignments
        ]

    async def revoke_assignment(self, assignment_id: UUID, teacher_id: UUID):
        """Отменить назначение (удалить дедлайн)."""
        assignment = await self.group_repo.get_assignment_by_id(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Назначение не найдено")

        if assignment.group.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Нет прав удалять это назначение")

        await self.group_repo.delete_assignment(assignment_id)
        return {"message": "Назначение отменено"}

    async def get_student_assignments(self, student_id: UUID) -> List[StudentAssignmentDTO]:
        """Получить список задач студента с статусом просрочки."""
        raw_data = await self.group_repo.get_student_assignments_raw(student_id)
        result = []

        # Получаем текущее время в UTC (с информацией о зоне)
        now_aware = datetime.now(timezone.utc)

        for row in raw_data:
            # row - это результат join, содержащий объект GroupAssignment и доп. поля
            assignment = row.GroupAssignment

            # Превращаем дату из БД (naive) в UTC (aware) для корректного сравнения
            deadline_aware = assignment.deadline.replace(tzinfo=timezone.utc)

            # Сравниваем две даты с часовыми поясами
            is_overdue = now_aware > deadline_aware

            result.append(StudentAssignmentDTO(
                assignment_id=assignment.id,
                group_name=row.group_name,
                problem_id=assignment.problem_id,
                problem_title=row.problem_title,
                deadline=deadline_aware,  # Фронт получит дату с Z
                is_overdue=is_overdue
            ))
        return result