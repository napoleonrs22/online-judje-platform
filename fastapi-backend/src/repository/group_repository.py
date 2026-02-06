# src/repository/group_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional

from ..models.group_models import Group, GroupAssignment, group_members
from ..models.user_models import User
from ..models.problem_models import Problem


class GroupRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_group(self, group: Group) -> Group:
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def get_by_id(self, group_id: UUID) -> Optional[Group]:
        stmt = select(Group).where(Group.id == group_id).options(selectinload(Group.students))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_teacher(self, teacher_id: UUID) -> List[Group]:
        stmt = select(Group).where(Group.teacher_id == teacher_id).order_by(Group.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def add_student(self, group: Group, student: User):
        if student not in group.students:
            group.students.append(student)
            await self.db.commit()

    async def get_student_count(self, group_id: UUID) -> int:
        """Получить количество студентов в группе"""
        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.students))
        )
        result = await self.db.execute(stmt)
        group = result.scalars().first()
        return len(group.students) if group else 0

    # --- Assignments ---

    async def create_assignment(self, assignment: GroupAssignment) -> GroupAssignment:
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def get_teacher_assignments(self, teacher_id: UUID) -> List[GroupAssignment]:
        """Получить все задания, созданные учителем (для таблицы управления)"""
        stmt = (
            select(GroupAssignment)
            .join(Group, GroupAssignment.group_id == Group.id)
            .where(Group.teacher_id == teacher_id)
            .options(
                selectinload(GroupAssignment.group),
                selectinload(GroupAssignment.problem)
            )
            .order_by(GroupAssignment.deadline)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_student_assignments_raw(self, student_id: UUID):
        """Получить задачи, назначенные студенту"""
        stmt = (
            select(
                GroupAssignment,
                Group.name.label("group_name"),
                Problem.title.label("problem_title")
            )
            .join(Group, GroupAssignment.group_id == Group.id)
            .join(Problem, GroupAssignment.problem_id == Problem.id)
            .join(group_members, Group.id == group_members.c.group_id)
            .where(group_members.c.user_id == student_id)
            .order_by(GroupAssignment.deadline)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def delete_assignment(self, assignment_id: UUID) -> bool:
        stmt = delete(GroupAssignment).where(GroupAssignment.id == assignment_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_assignment_by_id(self, assignment_id: UUID) -> Optional[GroupAssignment]:
        stmt = select(GroupAssignment).where(GroupAssignment.id == assignment_id).options(
            selectinload(GroupAssignment.group))
        result = await self.db.execute(stmt)
        return result.scalars().first()