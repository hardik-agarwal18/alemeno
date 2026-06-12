from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.repositories.base import BaseRepository
from app.db.models.job import Job
from typing import List, Optional

class JobRepository(BaseRepository[Job]):
    def __init__(self):
        super().__init__(Job)

    def get_jobs(self, db: Session, skip: int = 0, limit: int = 10, status: Optional[str] = None) -> List[Job]:
        query = db.query(Job)
        if status:
            query = query.filter(Job.status == status)
        return query.order_by(desc(Job.created_at)).offset(skip).limit(limit).all()

job_repo = JobRepository()
