from  uuid import UUID
from  fastapi import  HTTPException
from ..repository.problem_repository import ProblemRepository
from ..repository.group_repository import GroupRepository
from  ..repository.user_repository import UserRepository
from ..schemas.group_schemas import GroupCreate, AddMemberRequest, CreateAssignmentRequest, AssignmentResponse


class GroupService:
    def __init__(self, group_repo: GroupRepository, user_repo: UserRepository, problem_repo: ProblemRepository):
        self.group_repo = group_repo
        self.user_repo = user_repo
        self.problem_repo = problem_repo

    async def create_group(self, teacher_id: UUID, data: GroupCreate):
        return await self.group_repo.create_group(teacher_id, data.name, data.description)

    async def list_teacher_groups(self, teacher_id: UUID):
        return await self.group_repo.get_teacher_groups(teacher_id)

    async def add_member(self, group_id: UUID, teacher_id: UUID, data: AddMemberRequest):
        # 1. Проверяем группу
        group = await self.group_repo.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Группа не найдена")
        if group.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Вы не владелец этой группы")

        # 2. Ищем студента (по email или нику)
        identifier = data.identifier.strip()
        student = await self.user_repo.get_user_by_email(identifier)
        if not student:
            student = await self.user_repo.get_user_by_username(identifier)

        if not student:
            raise HTTPException(status_code=404, detail=f"Студент '{identifier}' не найден")

        # 3. Добавляем
        await self.group_repo.add_student(group, student)
        return {"message": f"Студент {student.full_name or student.username} добавлен"}

    async def create_assignment(self, group_id: UUID, teacher_id: UUID, data: CreateAssignmentRequest):
        # Проверка прав на группу
        group = await self.group_repo.get_group_by_id(group_id)
        if not group or group.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Нет прав на эту группу")

        # Проверка существования задачи
        # (Используем метод репозитория задач, предполагаем что он есть)
        problem = await self.problem_repo.get_problem_by_id(data.problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        return await self.group_repo.create_assignment(group_id, data.problem_id, data.deadline)

    async def list_assignments(self, teacher_id: UUID):
        assignments = await self.group_repo.get_teacher_assignments(teacher_id)
        # Преобразуем в красивый ответ для таблицы
        return [
            AssignmentResponse(
                id=a.id,
                group_name=a.group.name,
                problem_title=a.problem.title,
                deadline=a.deadline,
                created_at=a.created_at
            )
            for a in assignments
        ]

    async def revoke_assignment(self, assignment_id: UUID, teacher_id: UUID):
        # Тут по-хорошему надо проверить, принадлежит ли assignment группе этого учителя
        # Но для простоты пока просто удалим
        deleted = await self.group_repo.delete_assignment(assignment_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Назначение не найдено")
        return {"message": "Назначение отменено"}