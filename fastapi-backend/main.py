# fastapi-backend/main.py
import uuid
import re
import hashlib
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware 

from src.database import init_db
from src.api.teacher_router import teacher_router
from src.api.student_router import student_router

from src.models import db_models 

app = FastAPI(title="Олимпиадный Бэкенд (FastAPI)", version="0.1.0")


origins = ["*"] # Разрешаем любые источники в режиме разработки

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)
# =======================================================


@app.on_event("startup")
async def on_startup():
    """Инициализация базы данных при старте приложения."""
    print("Инициализация базы данных...")
    await init_db() 
    print("База данных готова.")

def generate_slug(title: str) -> str:
    """Генерация URL-friendly slug из названия с обходом кириллицы."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    
    # 🔥 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Если slug пустой, генерируем уникальный суффикс
    if not slug:
        return 'problem-' + str(uuid.uuid4())[:8]
        
    return slug

app.include_router(teacher_router)
app.include_router(student_router)