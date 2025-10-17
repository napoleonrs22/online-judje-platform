"""Alembic configuration file."""

from logging.config import fileConfig
import os  # 🔥 НУЖЕН ИМПОРТ OS
import  sys
sys.path.append(os.getcwd())
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from src.database import Base
# Убедись, что все модели импортированы здесь
from src.models.db_models import Problem, Submission, TestCase, Example  # Удалил User, т.к. его нет в db_models

# this is the Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # 🔥 ИСПРАВЛЕНИЕ: Используем переменную окружения, если она есть
    url = os.environ.get("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # Получаем настройки из alembic.ini
    section = config.get_section(config.config_ini_section, {})

    # 🔥 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ПЕРЕЗАПИСЬ URL из переменной окружения
    # Это гарантирует, что мы используем правильный логин/пароль из Docker Compose.
    target_url = os.environ.get("DATABASE_URL")
    if target_url:
        section['sqlalchemy.url'] = target_url

    connectable = engine_from_config(
        section,  # Используем обновленную секцию
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()