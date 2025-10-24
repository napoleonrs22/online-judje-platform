from .base import (
    Base, Column, UUID, String, Integer, DateTime, relationship, datetime, uuid
)


class User(Base):
    """Модель пользователя с поддержкой трех ролей: student, teacher, admin."""
    __tablename__ = "users"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(50), nullable=False, index=True)  # student, teacher, admin
    full_name = Column(String(200), nullable=True)
    university_id = Column(String(100), nullable=True, index=True)
    rating = Column(Integer, default=1500)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


    refresh_token_hash = Column(String, nullable=True)


    problems = relationship("Problem", back_populates="author", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

    def is_teacher(self) -> bool:
        return self.role in ["teacher", "admin"]

    def is_admin(self) -> bool:

        return self.role == "admin"

    def is_student(self) -> bool:

        return self.role == "student"