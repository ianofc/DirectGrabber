from fastapi import APIRouter
from app.api.v1.endpoints import auth, tasks, media

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth & Sessions"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Scraping Tasks"])
api_router.include_router(media.router, prefix="/media", tags=["Media Items"])
