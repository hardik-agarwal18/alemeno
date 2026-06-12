import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, Text, DateTime, ForeignKey, UUID, JSON
from sqlalchemy.orm import relationship
from app.db.models.base import Base

class JobSummary(Base):
    __tablename__ = "job_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    total_spend_inr = Column(Numeric(12, 2), nullable=True, default=0)
    total_spend_usd = Column(Numeric(12, 2), nullable=True, default=0)
    
    top_merchants = Column(JSON, nullable=True)
    spend_by_category = Column(JSON, nullable=True)
    anomaly_count = Column(Integer, nullable=True, default=0)
    
    risk_level = Column(String, nullable=True)
    narrative = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="summary")
