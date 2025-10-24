import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from models.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Синхронный URL для autogenerate ---
SYNC_DATABASE_URL = "postgresql+psycopg2://olympiad_user:olympiad_pass@db:5432/olympiad_db"

# --- Async URL для online миграций в runtime ---
ASYNC_DATABASE_URL = "postgresql+asyncpg://olympiad_user:olympiad_pass@db:5432/olympiad_db"

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
        await connection.run_sync(lambda conn: context.configure(connection=conn, target_metadata=target_metadata) or context.run_migrations())
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # для Alembic autogenerate используем синхронный
    run_migrations_online()
