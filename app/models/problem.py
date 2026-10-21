from sqlalchemy import Column, String, Text
from app.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    input_format = Column(Text, nullable=True)
    output_format = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    difficulty = Column(String(50), default="Easy")
    category = Column(String(50), default="Arrays")
    reference_solution = Column(Text, nullable=True)
