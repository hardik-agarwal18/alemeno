from fastapi import APIRouter
from app.api.routes import jobs, health

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
