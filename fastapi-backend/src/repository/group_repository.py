from greenlet.tests.fail_initialstub_already_started import result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List


from ..models.group_models import Group, GroupAssignment, group_members
from ..models.user_models import User
from ..models.problem_models import Problem


class GroupRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def create_group(self, teacher_id: UUID, name: str, description: str) -> Group:
        group = Group(teacher_id=teacher_id, name=name, description=description)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def get_teacher_groups(self, teacher_id: UUID) -> List[Group]:
        stmt = select(Group).where(Group.teacher_id == teacher_id).order_by(Group.teacher_id.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_group_by_id(self, group_id: UUID) -> Group | None:
        stmt = select(Group).where(Group.id == group_id).options(selectinload(Group.students))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def add_student(self, group: Group, student: User):
        # Проверяем дубликаты
        if student not in group.students:
            group.students.append(student)
            await self.db.commit()


    async def create_assignment(self, group_id: UUID, problem_id: UUID, deadline) -> GroupAssignment:
        assignment = GroupAssignment(group_id=group_id, problem_id=problem_id, deadline=deadline)
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def get_teacher_assignments(self, teacher_id: UUID):
        """Получить все активные назначения для преподавателя (для таблицы Assignments)"""
        stmt = (
            select(GroupAssignment)
            .join(Group, GroupAssignment.group_id == Group.id)
            .join(Problem, GroupAssignment.problem_id == Problem.id)
            .where(Group.teacher_id == teacher_id)
            .options(
                selectinload(GroupAssignment.group),
                selectinload(GroupAssignment.problem)
            )
            .order_by(GroupAssignment.deadline)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_assignment(self, assignment_id: UUID) -> bool:
        stmt = delete(GroupAssignment).where(GroupAssignment.id == assignment_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0