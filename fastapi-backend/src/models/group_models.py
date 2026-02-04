import uuid
from  datetime import datetime
from symtable import Class

from  sqlalchemy import  Column, String, ForeignKey, Table, DateTime, Text, Boolean
from  sqlalchemy.orm import relationship
from  sqlalchemy.dialects.postgresql import UUID

from src.database import Base



group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("joined_at", DateTime, default=datetime.utcnow),
)


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)


    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", back_populates="teaching_groups")
    students = relationship("User", secondary=group_members, back_populates="enrolled_groups")
    assignments = relationship("GroupAssignment", back_populates="group", cascade="all, delete-orphan")

class GroupAssignment(Base):

    __tablename__ = "group_assignments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)


    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="assignments")
    problem = relationship("Problem")