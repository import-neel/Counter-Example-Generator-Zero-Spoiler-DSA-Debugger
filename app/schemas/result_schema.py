from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    RUNTIME_ERROR = "runtime_error"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    OUTPUT_LIMIT_EXCEEDED = "output_limit_exceeded"
    SANDBOX_ERROR = "sandbox_error"
    INTERNAL_ERROR = "internal_error"


class ExecutionResult(BaseModel):
    status: ExecutionStatus
    stdout: str = Field(default="", description="Captured standard output")
    stderr: str = Field(default="", description="Captured standard error or exception")
    exit_code: int = Field(default=0, description="Process exit code")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    error_message: Optional[str] = Field(
        default=None, description="Summarized explanation or error category"
    )
    truncated: bool = Field(
        default=False, description="Flag indicating if output was truncated due to limit"
    )
