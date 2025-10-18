# fastapi-backend/src/models/db_models.py

from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, Enum, 
    JSON, Boolean
)
from sqlalchemy.orm import relationship 
# Импорты для утилит
from datetime import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

# 🔥 КЛЮЧ: Импортируем Base только из ВНЕШНЕГО модуля database.py
from ..database import Base

class DifficultyLevel(str, enum.Enum):
    EASY = "Легкий"
    MEDIUM = "Средний"
    HARD = "Сложный"

class CheckerType(str, enum.Enum):

    EXACT = "exact"
    TOKENS = "tokens"

class SubmissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT = "TIME_LIMIT"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    COMPILE_ERROR = "COMPILE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

