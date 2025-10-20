from .base import (
    Base, Column, UUID, String, Integer, DateTime, relationship, datetime, uuid # <-- Импорт должен работать
)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(50), nullable=False)
    full_name = Column(String(200), nullable=True)
    university_id = Column(String(100), nullable=True)
    rating = Column(Integer, default=1500)
    created_at = Column(DateTime, default=datetime.utcnow)

    problems = relationship("Problem", back_populates="author")
    submissions = relationship("Submission", back_populates="user")

    refresh_token_hash = Column(String, nullable=True)