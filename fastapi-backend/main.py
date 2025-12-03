# fastapi-backend/main.py

import uuid
import re
import hashlib
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.future import select

# --- Импорты из файлов проекта ---
from src.database import init_db, AsyncSessionLocal  
from src.api.teacher_router import teacher_router
from src.api.student_router import student_router
from src.api.auth_router import auth_router
from src.api.user_router import users
from src.api.admin_router import router
from src.api.dashboard_router import dashboard_router
# 🔥 ИМПОРТ ORM-модели User
from src.models.user_models import User
from src.models import base as models_base  # Используем 'base' для доступа к Enum'ам

# --- КОНСТАНТА ---
# Используем тот же ID, что и в роутерах (для создания задачи)
TEMP_TEACHER_ID = uuid.UUID('11111111-1111-1111-1111-111111111111')
# -----------------

app = FastAPI(title="Олимпиадный Бэкенд (FastAPI)", version="0.1.0")

origins = ["*"]  # Разрешаем любые источники в режиме разработки

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =======================================================

async def create_temp_user():
    """Создает временного учителя для тестирования, если его нет."""
    async with AsyncSessionLocal() as session:
        # 1. Проверяем, существует ли пользователь
        stmt = select(User).where(User.id == TEMP_TEACHER_ID)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            # 2. Создаем нового пользователя с ID-заглушкой
            temp_user = User(
                id=TEMP_TEACHER_ID,
                email="temp.teacher@example.com",
                username="temp_teacher",
                # Имитация хешированного пароля (в реальном коде хешировать!)
                hashed_password=hashlib.sha256(b"password123").hexdigest(),
                role="teacher"
            )
            session.add(temp_user)
            await session.commit()
            print(f"✅ Создан временный пользователь: {TEMP_TEACHER_ID}")
        else:
            print(f"☑️ Временный пользователь {TEMP_TEACHER_ID} уже существует.")


@app.on_event("startup")
async def on_startup():
    """Инициализация базы данных и создание временного пользователя."""
    print("Инициализация базы данных...")
    await init_db()  # Создаст таблицы (включая users)
    # await create_temp_user()  # 🔥 ВЫЗЫВАЕМ ФУНКЦИЮ
    print("База данных готова.")


def generate_slug(title: str) -> str:
    """Генерация URL-friendly slug из названия с обходом кириллицы."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')

    if not slug:
        return 'problem-' + str(uuid.uuid4())[:8]

    return slug

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(users)
app.include_router(router)
