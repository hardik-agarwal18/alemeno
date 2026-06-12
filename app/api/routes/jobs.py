import os
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db
from app.db.models.job import Job
from app.db.models.transaction import Transaction
from app.schemas.job import JobCreateResponse, JobStatusResponse, JobResultsResponse, TransactionSchema, JobSummarySchema
from app.workers.tasks import process_transactions_job
from app.core.config import settings
from app.db.repositories.job_repository import job_repo

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    # Calculate file size (read into memory, can be optimized if needed, but for simplicity here)
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB")
        
    # Save file
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(contents)
        
    # Create Job in DB
    job = Job(filename=file.filename, status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Enqueue task
    process_transactions_job.delay(str(job.id), filepath)
    
    return JobCreateResponse(job_id=job.id, status=job.status)

@router.get("/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = job_repo.get(db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Calculate progress (simple binary for now, can be expanded)
    progress = 0
    summary_data = None
    if job.status == "COMPLETED":
        progress = 100
        if job.summary:
            summary_data = JobSummarySchema.model_validate(job.summary).model_dump()
    elif job.status == "PROCESSING":
        progress = 50
        
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=progress,
        created_at=job.created_at,
        completed_at=job.completed_at,
        summary=summary_data
    )

@router.get("/{job_id}/results", response_model=JobResultsResponse)
def get_job_results(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = job_repo.get(db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.status != "COMPLETED":
        raise HTTPException(status_code=400, detail=f"Job is not completed. Current status: {job.status}")
        
    # Fetch transactions and summary
    transactions = db.query(Transaction).filter(Transaction.job_id == job_id).all()
    anomalies = [t for t in transactions if t.is_anomaly]
    
    summary_data = None
    if job.summary:
        summary_data = JobSummarySchema.model_validate(job.summary)
        
    # Using model_validate for Pydantic V2
    tx_schemas = [TransactionSchema.model_validate(t) for t in transactions]
    an_schemas = [TransactionSchema.model_validate(a) for a in anomalies]
    
    return JobResultsResponse(
        summary=summary_data,
        transactions=tx_schemas,
        anomalies=an_schemas
    )

@router.get("", response_model=List[JobStatusResponse])
def list_jobs(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    jobs = job_repo.get_jobs(db, skip=skip, limit=limit, status=status)
    
    responses = []
    for job in jobs:
        progress = 0
        if job.status == "COMPLETED":
            progress = 100
        elif job.status == "PROCESSING":
            progress = 50
            
        responses.append(
            JobStatusResponse(
                job_id=job.id,
                status=job.status,
                progress=progress,
                created_at=job.created_at,
                completed_at=job.completed_at
            )
        )
        
    return responses
