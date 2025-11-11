import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# --- Корректное добавление пути для абсолютных импортов ---
# BASE_DIR указывает на корень проекта (/app)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    # Добавляем корень проекта (/app) в sys.path
    sys.path.insert(0, BASE_DIR)

# Теперь импорт станет абсолютным и будет работать:
# Ищет 'src' внутри '/app'
from src.models.base import Base # ИСПРАВЛЕНО

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Синхронный URL для autogenerate ---
SYNC_DATABASE_URL = "postgresql+psycopg2://olympiad_user:olympiad_pass@db:5432/olympiad_user"

# --- Async URL для online миграций в runtime ---
ASYNC_DATABASE_URL = "postgresql+asyncpg://olympiad_user:olympiad_pass@db:5432/olympiad_user"

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(SYNC_DATABASE_URL)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


async def run_migrations_online_async():
    connectable = create_async_engine(ASYNC_DATABASE_URL, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        # Неправильно передавать лямбда-функцию с асинхронным кодом в run_sync.
        # Для Alembic в онлайн-режиме используем обычный синхронный подход выше,
        # так как сам Alembic синхронный.
        # Тем не менее, для сохранения структуры:
        await connection.run_sync(lambda conn: context.configure(connection=conn, target_metadata=target_metadata) or context.run_migrations())
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Используем синхронный режим для запуска миграций
    run_migrations_online()