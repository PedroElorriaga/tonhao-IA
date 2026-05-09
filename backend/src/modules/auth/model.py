import uuid

from sqlalchemy import Column, String, DateTime, Enum
from datetime import datetime, timezone

from src.database.sqlite_config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)   # null for Google-only accounts
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    role = Column(Enum("agent", "client", name="user_role"), nullable=False, default="client")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
