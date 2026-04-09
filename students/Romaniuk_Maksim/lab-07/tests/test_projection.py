# tests/test_projection.py
import pytest
from datetime import datetime

from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from domain.value_objects.stage_type import StageType, StageTypeEnum
from domain.events.domain_events import (
    JobOfferCreatedEvent,
    StageChangedEvent,
    OfferRejectedEvent,
    NoteAddedEvent
)
from cqrs.read_model.job_offer_read_repository import InMemoryJobOfferReadRepository
from cqrs.projection.job_offer_projection import JobOfferProjection


class TestJobOfferProjection:
    
    def setup_method(self):
        self.read_repo = InMemoryJobOfferReadRepository()
        self.projection = JobOfferProjection(self.read_repo)
    
    def test_on_job_offer_created_creates_view(self):
        event = JobOfferCreatedEvent(
            offer_id="OFFER-2024-0001",
            company_name="ООО Тест",
            position="Python Dev",
            user_id="USR-001",
            _occurred_at=datetime.now()
        )
        
        self.projection.handle_event(event)
        
        view = self.read_repo.find_by_id("OFFER-2024-0001")
        assert view is not None
        assert view.company == "ООО Тест"
        assert view.position == "Python Dev"
        assert view.status == "active"
    
    def test_on_stage_changed_updates_view(self):
        # Сначала создаем view через created event
        created = JobOfferCreatedEvent(
            offer_id="OFFER-2024-0002",
            company_name="Google",
            position="Java Dev",
            user_id="USR-002",
            _occurred_at=datetime.now()
        )
        self.projection.handle_event(created)
        
        # Затем меняем этап
        stage_event = StageChangedEvent(
            offer_id="OFFER-2024-0002",
            old_stage=StageType.resume_sent(),
            new_stage=StageType.hr_screening(),
            _occurred_at=datetime.now()
        )
        self.projection.handle_event(stage_event)
        
        view = self.read_repo.find_by_id("OFFER-2024-0002")
        assert view.current_stage == "hr_screening"
        assert view.progress_percentage == 20.0
    
    def test_on_offer_rejected_updates_view(self):
        created = JobOfferCreatedEvent(
            offer_id="OFFER-2024-0003",
            company_name="Microsoft",
            position="C# Dev",
            user_id="USR-003",
            _occurred_at=datetime.now()
        )
        self.projection.handle_event(created)
        
        reject_event = OfferRejectedEvent(
            offer_id="OFFER-2024-0003",
            reason="Not a fit",
            _occurred_at=datetime.now()
        )
        self.projection.handle_event(reject_event)
        
        view = self.read_repo.find_by_id("OFFER-2024-0003")
        assert view.status == "rejected"
        assert view.is_rejected is True
        assert view.is_active is False
    
    def test_on_note_added_updates_view(self):
        created = JobOfferCreatedEvent(
            offer_id="OFFER-2024-0004",
            company_name="Amazon",
            position="DevOps",
            user_id="USR-004",
            _occurred_at=datetime.now()
        )
        self.projection.handle_event(created)
        
        note_event = NoteAddedEvent(
            offer_id="OFFER-2024-0004",
            note_content="Важная заметка",
            _occurred_at=datetime.now()
        )
        self.projection.handle_event(note_event)
        
        view = self.read_repo.find_by_id("OFFER-2024-0004")
        assert len(view.notes) == 1
        assert "Важная заметка" in view.notes[0]
        assert view.notes_count == 1
