# fastapi-backend/src/api/teacher_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas.schemas import ProblemCreate 
from ..models.db_models import Problem, Example, TestCase
from ..services.problem_service import generate_slug

teacher_router = APIRouter(prefix="/api/teacher", tags=["Преподавательский функционал"])

@teacher_router.post("/problems", status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание новой задачи преподавателем."""
    
    if not problem_data.test_cases:
        raise HTTPException(status_code=400, detail="Задача должна содержать хотя бы один тест-кейс")

    problem_dict = problem_data.dict(exclude={"examples", "test_cases"})
    
    slug = generate_slug(problem_data.title) 
    
    db_problem = Problem(
        **problem_dict,
        slug=slug,
        time_limit=1000, 
        memory_limit=256
    )
    
    db.add(db_problem)
    await db.flush() 

    db_examples = [Example(problem_id=db_problem.id, **ex.dict()) for ex in problem_data.examples]
    db_tests = [
        TestCase(problem_id=db_problem.id, order_index=idx, **test.dict()) 
        for idx, test in enumerate(problem_data.test_cases)
    ]
    
    db.add_all(db_examples)
    db.add_all(db_tests)
    
    await db.commit()
    await db.refresh(db_problem)
    
    return {"message": "Задача успешно создана", "problem_id": db_problem.id, "slug": db_problem.slug}