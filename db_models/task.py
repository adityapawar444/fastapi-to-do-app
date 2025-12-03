import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    func,
    Boolean,
    text
)

from db import Base


class Task(Base):
    __tablename__ = "task"

    id = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    title = Column(
        String(64),
        nullable=False
    )
    description = Column(
        String(255),
        nullable=False
    )
    status = Column(
        String(64),
        nullable=False
    )
    priority = Column(
        String(64),
        nullable=False
    )
    is_deleted = Column(
        Boolean,
        server_default=text("0"),
        nullable=False
    )
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    due_by = Column(
        DateTime,
        server_default=text("DATE('now')"),
        nullable=True
    )
