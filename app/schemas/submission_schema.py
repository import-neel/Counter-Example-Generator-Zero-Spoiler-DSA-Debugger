from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.result_schema import ExecutionResult, ExecutionStatus


class SubmissionCreateRequest(BaseModel):
    problem_id: str = Field(..., min_length=1, max_length=100, description="Identifier of the DSA problem")
    language: str = Field(default="python", description="Programming language (e.g. python)")
    code: str = Field(..., min_length=1, max_length=100000, description="Source code submitted by student")
    input: Optional[str] = Field(default="", max_length=500000, description="Standard input data")
    timeout: Optional[float] = Field(
        default=None, gt=0.0, le=10.0, description="Custom execution timeout in seconds"
    )


class SubmissionRunResponse(BaseModel):
    submission_id: str
    problem_id: str
    language: str
    result: ExecutionResult
    created_at: datetime


class SubmissionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    problem_id: str
    language: str
    code: str
    status: ExecutionStatus
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    created_at: datetime
