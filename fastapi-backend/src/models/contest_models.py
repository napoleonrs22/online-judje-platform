from .base import Base, Column, UUID, String,  DateTime, ForeignKey, relationship, uuid, Boolean
from .base import DifficultyLevel, CheckerType

class Contest(Base):
    __tablename__ = "contests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    problem_ids = Column(UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False)
    participants = relationship("Participant", backref="contest")
