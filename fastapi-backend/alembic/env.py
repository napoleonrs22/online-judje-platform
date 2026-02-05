# alembic/env.py

import asyncio
import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# --- Путь к проекту ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --- ПРАВИЛЬНЫЙ ИМПОРТ Base ИЗ database.py ---
from src.database import Base
# --- ИМПОРТИРУЕМ ВСЕ МОДЕЛИ (они должны быть загружены ДО Alembic) ---
from src.models.user_models import User
from src.models.problem_models import Problem, TestCase, Example
from src.models.submission_models import Submission
from src.models.contest_models import Contest
from  src.models.group_models import Group, GroupAssignment
# --- Конфиг ---
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- URL ---
SYNC_DATABASE_URL = "postgresql+psycopg2://olympiad_user:olympiad_pass@db:5432/olympiad_user"
ASYNC_DATABASE_URL = "postgresql+asyncpg://olympiad_user:olympiad_pass@db:5432/olympiad_user"

target_metadata = Base.metadata

# --- Offline (autogenerate) ---
def run_migrations_offline():
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# --- Online (синхронный) для alembic upgrade ---
def run_migrations_online():
    connectable = create_engine(
        SYNC_DATABASE_URL,
        poolclass=pool.StaticPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

# --- Запуск ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()