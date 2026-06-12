import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Boolean, Text, DateTime, ForeignKey, Date, UUID
from sqlalchemy.orm import relationship
from app.db.models.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    txn_id = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    merchant = Column(String, nullable=True)
    amount = Column(Numeric(12, 2), nullable=True)
    currency = Column(String, nullable=True)
    status = Column(String, nullable=True)
    category = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(Text, nullable=True)
    llm_failed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="transactions")
