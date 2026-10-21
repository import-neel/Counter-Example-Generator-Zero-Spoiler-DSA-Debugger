import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime
from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class DebuggingSession(Base):
    __tablename__ = "debugging_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    problem_id = Column(String(100), nullable=False, index=True)
    current_hint_level = Column(Integer, nullable=False, default=0)
    counterexample_input = Column(Text, nullable=True)
    counterexample_expected = Column(Text, nullable=True)
    counterexample_actual = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="in_progress")  # in_progress, resolved, given_up
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
