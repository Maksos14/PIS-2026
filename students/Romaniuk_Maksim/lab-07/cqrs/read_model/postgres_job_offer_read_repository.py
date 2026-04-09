# cqrs/read_model/postgres_job_offer_read_repository.py
from typing import List, Optional
from datetime import datetime  # ДОБАВИТЬ ЭТУ СТРОКУ
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base

from cqrs.read_model.job_offer_view import JobOfferView, JobOfferSummaryView
from cqrs.read_model.job_offer_read_repository import JobOfferReadRepository


Base = declarative_base()


class JobOfferViewORM(Base):
    __tablename__ = "job_offer_views"
    
    id = Column(String(50), primary_key=True)
    company = Column(String(100), nullable=False)
    position = Column(String(200), nullable=False)
    user_id = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    current_stage = Column(String(30), nullable=False)
    progress_percentage = Column(Float, default=0.0)
    notes = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    is_rejected = Column(Boolean, default=False)
    is_offer_received = Column(Boolean, default=False)
    notes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PostgresJobOfferReadRepository(JobOfferReadRepository):
    """PostgreSQL реализация read-репозитория"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, view: JobOfferView) -> None:
        orm_obj = self._to_orm(view)
        self._session.merge(orm_obj)
        self._session.commit()
    
    def find_by_id(self, offer_id: str) -> Optional[JobOfferView]:
        orm_obj = self._session.query(JobOfferViewORM).filter(JobOfferViewORM.id == offer_id).first()
        return self._to_view(orm_obj) if orm_obj else None
    
    def find_by_user_id(self, user_id: str) -> List[JobOfferView]:
        orm_objs = self._session.query(JobOfferViewORM).filter(JobOfferViewORM.user_id == user_id).all()
        return [self._to_view(obj) for obj in orm_objs]
    
    def find_active_offers(self, user_id: str) -> List[JobOfferSummaryView]:
        orm_objs = self._session.query(JobOfferViewORM).filter(
            JobOfferViewORM.user_id == user_id,
            JobOfferViewORM.is_active == True,
            JobOfferViewORM.is_rejected == False,
            JobOfferViewORM.is_offer_received == False
        ).all()
        return [
            JobOfferSummaryView(
                id=obj.id,
                company=obj.company,
                position=obj.position,
                current_stage=obj.current_stage,
                progress_percentage=obj.progress_percentage
            )
            for obj in orm_objs
        ]
    
    def find_by_stage(self, user_id: str, stage: str) -> List[JobOfferSummaryView]:
        orm_objs = self._session.query(JobOfferViewORM).filter(
            JobOfferViewORM.user_id == user_id,
            JobOfferViewORM.current_stage == stage
        ).all()
        return [
            JobOfferSummaryView(
                id=obj.id,
                company=obj.company,
                position=obj.position,
                current_stage=obj.current_stage,
                progress_percentage=obj.progress_percentage
            )
            for obj in orm_objs
        ]
    
    def delete(self, offer_id: str) -> bool:
        orm_obj = self._session.query(JobOfferViewORM).filter(JobOfferViewORM.id == offer_id).first()
        if orm_obj:
            self._session.delete(orm_obj)
            self._session.commit()
            return True
        return False
    
    def _to_orm(self, view: JobOfferView) -> JobOfferViewORM:
        return JobOfferViewORM(
            id=view.id,
            company=view.company,
            position=view.position,
            user_id=view.user_id,
            status=view.status,
            current_stage=view.current_stage,
            progress_percentage=view.progress_percentage,
            notes=view.notes,
            is_active=view.is_active,
            is_rejected=view.is_rejected,
            is_offer_received=view.is_offer_received,
            notes_count=view.notes_count,
            created_at=view.created_at,
            updated_at=view.updated_at
        )
    
    def _to_view(self, orm: JobOfferViewORM) -> JobOfferView:
        return JobOfferView(
            id=orm.id,
            company=orm.company,
            position=orm.position,
            user_id=orm.user_id,
            status=orm.status,
            current_stage=orm.current_stage,
            progress_percentage=orm.progress_percentage,
            notes=orm.notes or [],
            is_active=orm.is_active,
            is_rejected=orm.is_rejected,
            is_offer_received=orm.is_offer_received,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
