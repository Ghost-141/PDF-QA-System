from fastapi import APIRouter

from backend.api import files, qa

api_router = APIRouter()
api_router.include_router(files.router)
api_router.include_router(qa.router)

__all__ = ["api_router"]
