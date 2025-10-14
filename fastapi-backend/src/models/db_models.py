# fastapi-backend/src/models/db_models.py

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
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


class Problem(Base):
    """Модель для задачи (основная информация)."""
    __tablename__ = "problems"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    description = Column(Text, nullable=False)
    
    time_limit = Column(Integer, default=1000) # мс
    memory_limit = Column(Integer, default=256) # МБ
    
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    checker_type = Column(Enum(CheckerType), nullable=False, default=CheckerType.EXACT)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    examples = relationship("Example", back_populates="problem")
    test_cases = relationship("TestCase", back_populates="problem")


class TestCase(Base):
    """Модель для скрытых тестов."""
    __tablename__ = "test_cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"))
    
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False) 
    is_sample = Column(Boolean, default=False)

    problem = relationship("Problem", back_populates="test_cases")


class Example(Base):
    """Модель для примеров, которые видит студент в описании задачи."""
    __tablename__ = "examples"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"))
    
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    
    problem = relationship("Problem", back_populates="examples")
    

class Submission(Base):
    """Модель для хранения отправленных решений студентов."""
    __tablename__ = "submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False)
    
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    execution_time = Column(Integer, nullable=True)     
    memory_used = Column(Integer, nullable=True)        
    error_message = Column(Text, nullable=True)         
    
    test_results = Column(JSON, nullable=True) 
    
    submitted_at = Column(DateTime, default=datetime.utcnow)

