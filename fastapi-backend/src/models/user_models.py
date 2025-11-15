#user.models.py
from enum import Enum
from .base import (
    Base, Column, UUID, String, Integer, DateTime, relationship, datetime, uuid
)
from sqlalchemy import Boolean

class Role(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя системы.

    Поддерживает три роли:
    - student
    - teacher
    - admin
    """

    __tablename__ = "users"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    username: str = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)

    role: Role = Column(String(50), nullable=False, index=True, default=Role.STUDENT.value)
    full_name: str | None = Column(String(200), nullable=True)
    university_id: str | None = Column(String(100), nullable=True, index=True)
    rating: int = Column(Integer, default=1500)

    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    refresh_token_hash: str | None = Column(String, nullable=True)

    is_active: bool = Column(Boolean, default=True, nullable=False, server_default="true")

    # --- Связи ---
    problems = relationship("Problem", back_populates="author", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")


    def __repr__(self) -> str:

        return f"<User {self.username} ({self.role.value})>"

    def is_teacher(self) -> bool:
        return self.role in {Role.TEACHER, Role.ADMIN}

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    def is_student(self) -> bool:
        return self.role == Role.STUDENT

    def update_rating(self, delta: int) -> None:
        self.rating = max(0, self.rating + delta)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "role": self.role.value,
            "full_name": self.full_name,
            "university_id": self.university_id,
            "rating": self.rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
