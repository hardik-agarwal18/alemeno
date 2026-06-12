from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

class JobCreateResponse(BaseModel):
    job_id: UUID
    status: str

class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    progress: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    summary: Optional[Any] = None

class TransactionSchema(BaseModel):
    id: UUID
    txn_id: Optional[str] = None
    date: Optional[datetime] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    account_id: Optional[str] = None
    notes: Optional[str] = None
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class JobSummarySchema(BaseModel):
    total_spend_inr: float = 0.0
    total_spend_usd: float = 0.0
    top_merchants: Any = None
    spend_by_category: Any = None
    anomaly_count: int = 0
    risk_level: Optional[str] = None
    narrative: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class JobResultsResponse(BaseModel):
    summary: Optional[JobSummarySchema] = None
    transactions: List[TransactionSchema] = []
    anomalies: List[TransactionSchema] = []
