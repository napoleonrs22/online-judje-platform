# fastapi-backend/src/database.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # Загружаем .env

# ✅ Base для всех моделей
Base = declarative_base()

# ============ DATABASE CONFIGURATION ============

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не установлена в .env файле!")

# Если нет asyncpg, подменяем на асинхронный префикс
if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    elif DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
    else:
        raise ValueError("❌ DATABASE_URL должен быть для PostgreSQL (postgresql:// или postgres://)")

print(f"✅ Подключение к БД: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

# ============ ASYNC ENGINE ============

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Установите True для логирования SQL запросов
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=20,
    max_overflow=0,
)

# ============ ASYNC SESSION ============

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# ============ FASTAPI DEPENDENCY ============

async def get_db():
    """Dependency для получения асинхронной сессии в маршрутах."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ============ DATABASE INITIALIZATION ============

async def init_db():
    """Инициализация БД (только для dev, не использовать с Alembic в production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы созданы успешно!")


async def close_db():
    """Закрытие всех соединений с БД."""
    await engine.dispose()
    print("✅ Соединения с БД закрыты!")