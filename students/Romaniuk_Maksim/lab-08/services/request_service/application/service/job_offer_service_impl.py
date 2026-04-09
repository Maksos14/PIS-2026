import sys
from pathlib import Path
from datetime import datetime
import uuid
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from port.on.create_job_offer_use_case import CreateJobOfferUseCase, CreateJobOfferCommand 
from port.on.get_job_offer_use_case import GetJobOfferUseCase
from port.out.job_offer_repository import JobOfferRepository
from port.out.notification_service import NotificationService

from domain.models.job_offer import JobOffer
from domain.models.project import Project
from domain.value_objects.company_name import CompanyName
from domain.value_objects.stage_type import StageType, STAGE_ORDER


class JobOfferServiceImpl(CreateJobOfferUseCase, GetJobOfferUseCase):
    """Реализация фасада сервиса откликов"""
    
    def __init__(
        self, 
        repository: JobOfferRepository, 
        notification_service: NotificationService,
        event_publisher = None  # добавлен новый параметр
    ):
        self._repository = repository
        self._notification_service = notification_service
        self._event_publisher = event_publisher  # сохранение publisher
    
    # === Из CreateJobOfferUseCase ===
    def create_offer(self, command: CreateJobOfferCommand) -> str:
        if not command.company or not command.company.strip():
            raise ValueError("Company name cannot be empty")
        if not command.position or not command.position.strip():
            raise ValueError("Position cannot be empty")
        if not command.user_id or not command.user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        year = datetime.now().year
        unique_part = uuid.uuid4().hex[:4].upper()
        offer_id = f"OFFER-{year}-{unique_part}"
        
        company = CompanyName(command.company)
        
        job_offer = JobOffer(
            offer_id=offer_id,
            company=company,
            position=command.position,
            user_id=command.user_id
        )
        
        self._repository.save(job_offer)
        
        # Публикация через event_publisher если есть
        if self._event_publisher:
            self._event_publisher.publish(job_offer.events)
        else:
            for event in job_offer.events:
                self._notification_service.publish(event)
        job_offer.clear_events()
        
        return offer_id
    
    # === Из GetJobOfferUseCase ===
    def get_offer(self, offer_id: str):
        job_offer = self._repository.find_by_id(offer_id)
        if not job_offer:
            return None
        
        from query.dto.job_offer_dto import JobOfferDto
        return JobOfferDto(
            id=job_offer.id,
            company=str(job_offer.company),
            position=job_offer.position,
            user_id=job_offer.user_id,
            status=job_offer.status.value,
            current_stage=job_offer.current_stage.value,
            progress_percentage=job_offer.progress_percentage,
            notes=job_offer.notes,
            created_at=job_offer.created_at,
            updated_at=job_offer.updated_at
        )
    
    # === Новые методы ===
    def change_stage(self, offer_id: str, new_stage, note: str = None) -> dict:
        job_offer = self._repository.find_by_id(offer_id)
        if not job_offer:
            raise ValueError(f"Job offer {offer_id} not found")
        
        if job_offer.is_rejected:
            raise ValueError(f"Cannot change stage of rejected offer {offer_id}")
        if job_offer.is_offer_received:
            raise ValueError(f"Cannot change stage of completed offer {offer_id}")
        
        old_stage = job_offer.current_stage.value
        new_stage_obj = StageType(new_stage)
        
        if not job_offer.current_stage.can_transition_to(new_stage_obj):
            raise ValueError(f"Cannot transition from {old_stage} to {new_stage_obj.value}")
        
        job_offer.change_stage(new_stage_obj, note)
        self._repository.save(job_offer)
        
        # Публикация через event_publisher если есть
        if self._event_publisher:
            self._event_publisher.publish(job_offer.events)
        else:
            for event in job_offer.events:
                self._notification_service.publish(event)
        job_offer.clear_events()
        
        return {"offer_id": offer_id, "old_stage": old_stage, "new_stage": new_stage_obj.value}
    
    def add_note(self, offer_id: str, content: str) -> dict:
        job_offer = self._repository.find_by_id(offer_id)
        if not job_offer:
            raise ValueError(f"Job offer {offer_id} not found")
        
        if job_offer.is_rejected:
            raise ValueError(f"Cannot add note to rejected offer {offer_id}")
        if job_offer.is_offer_received:
            raise ValueError(f"Cannot add note to completed offer {offer_id}")
        
        old_count = len(job_offer.notes)
        job_offer.add_note(content)
        self._repository.save(job_offer)
        
        # Публикация через event_publisher если есть
        if self._event_publisher:
            self._event_publisher.publish(job_offer.events)
        else:
            for event in job_offer.events:
                self._notification_service.publish(event)
        job_offer.clear_events()
        
        return {"offer_id": offer_id, "total_notes_count": len(job_offer.notes), "notes_added_count": len(job_offer.notes) - old_count}
    
    def reject_offer(self, offer_id: str, reason: str = None) -> dict:
        job_offer = self._repository.find_by_id(offer_id)
        if not job_offer:
            raise ValueError(f"Job offer {offer_id} not found")
        
        if job_offer.is_offer_received:
            raise ValueError(f"Cannot reject offer {offer_id} with received offer")
        if job_offer.is_rejected:
            raise ValueError(f"Offer {offer_id} already rejected")
        
        old_status = job_offer.status.value
        job_offer.mark_rejected(reason)
        self._repository.save(job_offer)
        
        # Публикация через event_publisher если есть
        if self._event_publisher:
            self._event_publisher.publish(job_offer.events)
        else:
            for event in job_offer.events:
                self._notification_service.publish(event)
        job_offer.clear_events()
        
        return {"offer_id": offer_id, "old_status": old_status, "new_status": job_offer.status.value}
    
    def create_project(self, name: str, user_id: str, description: str = "") -> str:
        if not name or not name.strip():
            raise ValueError("Project name is required")
        
        project_id = f"PRJ-{uuid.uuid4().hex[:4].upper()}"
        
        project = Project(
            project_id=project_id,
            name=name,
            user_id=user_id,
            description=description
        )
        
        self._repository.save(project)
        
        # Публикация через event_publisher если есть
        if self._event_publisher:
            self._event_publisher.publish(project.events)
        else:
            for event in project.events:
                self._notification_service.publish(event)
        project.clear_events()
        
        return project_id
    
    def list_active_offers(self, user_id: str, limit: int = 20, offset: int = 0) -> dict:
        all_offers = self._repository.find_by_user_id(user_id)
        
        active_offers = [
            o for o in all_offers
            if o.is_active and not o.is_rejected and not o.is_offer_received
        ]
        
        total = len(active_offers)
        paginated = active_offers[offset:offset + limit]
        
        from query.dto.job_offer_dto import JobOfferBriefDto
        items = [
            JobOfferBriefDto(
                id=o.id,
                company=str(o.company),
                position=o.position,
                status=o.status.value,
                current_stage=o.current_stage.value,
                progress_percentage=o.progress_percentage
            )
            for o in paginated
        ]
        
        return {"items": items, "total": total, "limit": limit, "offset": offset}
    
    def list_offers_by_stage(self, user_id: str, stage, limit: int = 20, offset: int = 0) -> dict:
        all_offers = self._repository.find_by_user_id(user_id)
        
        filtered = [
            o for o in all_offers
            if o.current_stage.value == stage.value
        ]
        
        total = len(filtered)
        paginated = filtered[offset:offset + limit]
        
        from query.dto.job_offer_dto import JobOfferBriefDto
        items = [
            JobOfferBriefDto(
                id=o.id,
                company=str(o.company),
                position=o.position,
                status=o.status.value,
                current_stage=o.current_stage.value,
                progress_percentage=o.progress_percentage
            )
            for o in paginated
        ]
        
        return {"items": items, "total": total, "stage": stage.value, "limit": limit, "offset": offset}
    
    def get_stages_progress(self, offer_id: str):
        job_offer = self._repository.find_by_id(offer_id)
        if not job_offer:
            return None
        
        current_stage = job_offer.current_stage
        current_index = current_stage.order
        total_stages = len(STAGE_ORDER)
        
        from query.dto.stage_dto import StageDto, StagesProgressDto
        stages = []
        for i, stage_enum in enumerate(STAGE_ORDER):
            stage = StageType(stage_enum)
            stages.append(StageDto(
                name=stage.value,
                order=i,
                is_current=(i == current_index),
                is_completed=(i < current_index)
            ))
        
        return StagesProgressDto(
            current_stage=current_stage.value,
            total_stages=total_stages,
            completed_stages=current_index,
            progress_percentage=job_offer.progress_percentage,
            stages=stages
        )
