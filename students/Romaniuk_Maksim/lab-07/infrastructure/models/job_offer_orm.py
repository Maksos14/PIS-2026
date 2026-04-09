from sqlalchemy import Column, String, Float, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class OfferStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    REJECTED = "rejected"
    OFFER_RECEIVED = "offer_received"

class StageTypeEnum(str, enum.Enum):
    RESUME_SENT = "resume_sent"
    HR_SCREENING = "hr_screening"
    TECH_INTERVIEW = "tech_interview"
    TEST_TASK = "test_task"
    FINAL_INTERVIEW = "final_interview"
    OFFER = "offer"

class JobOfferORM(Base):
    __tablename__ = "job_offers"

    id = Column(String(50), primary_key=True)
    company = Column(String(100), nullable=False)
    position = Column(String(200), nullable=False)
    user_id = Column(String(50), nullable=False, index=True)
    status = Column(SQLEnum(OfferStatusEnum), nullable=False, default=OfferStatusEnum.ACTIVE)
    current_stage = Column(SQLEnum(StageTypeEnum), nullable=False, default=StageTypeEnum.RESUME_SENT)
    notes = Column(JSON, default=list)
    progress_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)