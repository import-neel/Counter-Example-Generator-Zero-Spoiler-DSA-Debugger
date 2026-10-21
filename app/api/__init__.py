from fastapi import APIRouter
from app.api.routes_submissions import router as submissions_router
from app.api.routes_problems import router as problems_router

__all__ = ["submissions_router", "problems_router"]
