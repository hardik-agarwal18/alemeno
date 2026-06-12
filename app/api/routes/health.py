from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.dependencies.db import get_db
import redis
from app.core.config import settings

router = APIRouter()

@router.get("")
def health_check(db: Session = Depends(get_db)):
    status = {"status": "healthy"}
    
    # Check DB
    try:
        db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["status"] = "unhealthy"
        status["database"] = "disconnected"
        status["database_error"] = str(e)
        
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        status["redis"] = "connected"
    except Exception as e:
        status["status"] = "unhealthy"
        status["redis"] = "disconnected"
        status["redis_error"] = str(e)
        
    if status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=status)
        
    return status
