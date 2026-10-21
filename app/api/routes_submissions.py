from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.submission import Submission
from app.schemas.result_schema import ExecutionResult, ExecutionStatus
from app.schemas.submission_schema import (
    SubmissionCreateRequest,
    SubmissionDetailResponse,
    SubmissionRunResponse,
)
from app.services.code_runner import code_runner
from app.utils.logger import logger

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post(
    "/run",
    response_model=SubmissionRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run and persist a student code submission",
)
def run_submission(
    payload: SubmissionCreateRequest,
    db: Session = Depends(get_db),
) -> SubmissionRunResponse:
    """
    Executes student code against standard input in a sandbox environment,
    records execution telemetry, and persists the submission to the database.
    """
    logger.info("Received run submission for problem_id=%s", payload.problem_id)

    # Execute code in safe sandbox
    result: ExecutionResult = code_runner.run_code(
        code=payload.code,
        input_data=payload.input or "",
        timeout=payload.timeout,
    )

    # Persist submission into database with trimmed outputs (avoid DB explosion)
    saved_stdout = result.stdout[:65536]
    saved_stderr = result.stderr[:65536]

    submission = Submission(
        problem_id=payload.problem_id,
        language=payload.language,
        code=payload.code,
        status=result.status.value,
        stdout=saved_stdout,
        stderr=saved_stderr,
        exit_code=result.exit_code,
        execution_time=result.execution_time,
        created_at=datetime.now(timezone.utc),
    )

    try:
        db.add(submission)
        db.commit()
        db.refresh(submission)
        logger.info("Persisted submission %s to database", submission.id)
    except Exception as e:
        db.rollback()
        logger.error("Failed to persist submission to database: %s", e)
        # Even if DB write fails, return execution result cleanly
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist submission record",
        )

    return SubmissionRunResponse(
        submission_id=submission.id,
        problem_id=submission.problem_id,
        language=submission.language,
        result=result,
        created_at=submission.created_at,
    )


@router.get(
    "/{submission_id}",
    response_model=SubmissionDetailResponse,
    summary="Retrieve details of a past submission",
)
def get_submission(
    submission_id: str,
    db: Session = Depends(get_db),
) -> SubmissionDetailResponse:
    """Fetch stored submission telemetry and output by ID."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission with ID '{submission_id}' not found",
        )

    return SubmissionDetailResponse(
        id=submission.id,
        problem_id=submission.problem_id,
        language=submission.language,
        code=submission.code,
        status=ExecutionStatus(submission.status),
        stdout=submission.stdout,
        stderr=submission.stderr,
        exit_code=submission.exit_code,
        execution_time=submission.execution_time,
        created_at=submission.created_at,
    )
