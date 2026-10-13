from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.problem import Problem
from app.schemas.problem_schema import ProblemSchema

router = APIRouter(prefix="/problems", tags=["Problems"])


@router.get("", response_model=List[ProblemSchema], summary="List all DSA problems")
def list_problems(db: Session = Depends(get_db)) -> List[ProblemSchema]:
    """
    Returns available DSA problems.
    Teammate 2 populates problems, but this contract endpoint is provided for full API consistency.
    """
    problems = db.query(Problem).all()
    return [
        ProblemSchema(
            id=p.id,
            title=p.title,
            description=p.description,
            input_format=p.input_format,
            output_format=p.output_format,
            constraints=p.constraints,
            difficulty=p.difficulty,
            category=p.category,
        )
        for p in problems
    ]


@router.get("/{problem_id}", response_model=ProblemSchema, summary="Get problem by ID")
def get_problem(problem_id: str, db: Session = Depends(get_db)) -> ProblemSchema:
    """Fetch problem specifications and constraints."""
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem '{problem_id}' not found",
        )
    return ProblemSchema(
        id=problem.id,
        title=problem.title,
        description=problem.description,
        input_format=problem.input_format,
        output_format=problem.output_format,
        constraints=problem.constraints,
        difficulty=problem.difficulty,
        category=problem.category,
    )
