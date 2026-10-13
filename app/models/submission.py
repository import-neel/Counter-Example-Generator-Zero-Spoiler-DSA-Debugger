import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, DateTime
from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    problem_id = Column(String(100), nullable=False, index=True)
    language = Column(String(50), nullable=False, default="python")
    code = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, index=True)
    stdout = Column(Text, nullable=False, default="")
    stderr = Column(Text, nullable=False, default="")
    exit_code = Column(Integer, nullable=False, default=0)
    execution_time = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
