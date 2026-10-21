from typing import List, Optional
from pydantic import BaseModel, Field


class TestCaseSchema(BaseModel):
    id: Optional[str] = None
    input_data: str
    expected_output: str
    is_sample: bool = True
    explanation: Optional[str] = None


class ProblemSchema(BaseModel):
    id: str
    title: str
    description: str
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    difficulty: Optional[str] = "Easy"
    category: Optional[str] = "Arrays"
    sample_test_cases: List[TestCaseSchema] = Field(default_factory=list)
