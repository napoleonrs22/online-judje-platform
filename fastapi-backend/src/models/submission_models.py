from .base import Base, Column, UUID, String, Text, DateTime, ForeignKey, Enum, JSON, Integer, relationship, datetime, uuid
from .base import SubmissionStatus 

class Submission(Base):
    """Модель для хранения отправленных решений студентов."""
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem")
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)

    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    execution_time = Column(Integer, nullable=True)
    memory_used = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    test_results = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Submission id={self.id} user_id={self.user_id}>, problem_id={self.problem_id}> status: {self.status}"