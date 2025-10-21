# fastapi-backend/src/models/problem.py

from .base import Base, Column, UUID, String, Integer, Text, DateTime, ForeignKey, Enum, relationship, datetime, uuid, Boolean
from .base import DifficultyLevel, CheckerType


class Problem(Base):
    __tablename__ = "problems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    description = Column(Text, nullable=False)

    time_limit = Column(Integer, default=1000)
    memory_limit = Column(Integer, default=256)

    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    checker_type = Column(Enum(CheckerType), nullable=False, default=CheckerType.EXACT)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="problems") 
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
    __tablename__ = "examples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"))

    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)

    problem = relationship("Problem", back_populates="examples")