import uuid

from database.settings import Base

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy import Enum
from datetime import datetime, timezone


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum("open", "pending", "in_progress", "solved", "closed", name="ticket_status"), nullable=False, default="open")
    priority = Column(Enum("low", "medium", "high", "critical", name="ticket_priority"), nullable=False, default="medium")
    category = Column(String(100), nullable=False)
    client_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    attachment_url = Column(String(512), nullable=True)
    attachment_name = Column(String(255), nullable=True)