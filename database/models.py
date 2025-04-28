import uuid
from sqlalchemy import Column, Integer, String, Enum, Text, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from database.session import Base
import enum


class StatusEnum(str, enum.Enum):
    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"


class EntityEnum(str, enum.Enum):
    tasks_update = "tasks_update"
    tasks_post = "tasks_post"
    tasks_delete = "tasks_delete"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HttpLogs(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    request = Column(JSON, nullable=False)
    response = Column(JSON, nullable=False)
    url = Column(String, nullable=False)
    entity_type = Column(Enum(EntityEnum), nullable=True)
    entity_id = Column(String, nullable=True)
