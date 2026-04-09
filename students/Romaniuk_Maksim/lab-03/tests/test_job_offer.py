import pytest

from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from domain.value_objects.stage_type import StageType
from domain.events.domain_events import (
    JobOfferCreatedEvent,
    StageChangedEvent,
    OfferRejectedEvent,
    OfferReceivedEvent
)


class TestJobOffer:

    def _create_valid_offer(self):
        company = CompanyName("ООО ТехноПарк")
        return JobOffer(
            offer_id="OFFER-2024-0001",
            company=company,
            position="Python Developer",
            user_id="USR-12345"
        )

    def test_should_create_job_offer_successfully(self):
        company = CompanyName("ООО ТехноПарк")
        
        offer = JobOffer(
            offer_id="OFFER-2024-0001",
            company=company,
            position="Python Developer",
            user_id="USR-12345"
        )
        
        assert offer.id == "OFFER-2024-0001"
        assert offer.company == company
        assert offer.position == "Python Developer"
        assert offer.user_id == "USR-12345"
        assert offer.is_active is True
        assert offer.current_stage == StageType.resume_sent()

    def test_should_not_create_offer_with_empty_company(self):
        with pytest.raises(ValueError, match="Company name cannot be empty"):
            CompanyName("")

    def test_should_not_create_offer_with_short_company_name(self):
        with pytest.raises(ValueError, match="Company name too short"):
            CompanyName("A")

    def test_should_not_create_offer_with_empty_position(self):
        company = CompanyName("ООО ТехноПарк")
        
        with pytest.raises(ValueError, match="Position cannot be empty"):
            JobOffer(
                offer_id="OFFER-2024-0001",
                company=company,
                position="",
                user_id="USR-12345"
            )

    def test_should_not_create_offer_with_invalid_id_format(self):
        company = CompanyName("ООО ТехноПарк")
        
        with pytest.raises(ValueError, match="Invalid offer ID format"):
            JobOffer(
                offer_id="INVALID-123",
                company=company,
                position="Python Developer",
                user_id="USR-12345"
            )

    def test_should_change_stage_to_next(self):
        offer = self._create_valid_offer()
        
        offer.change_stage(StageType.hr_screening())
        
        assert offer.current_stage == StageType.hr_screening()

    def test_should_not_skip_stages(self):
        offer = self._create_valid_offer()
        
        with pytest.raises(ValueError) as exc_info:
            offer.change_stage(StageType.tech_interview())
        
        assert "Only next stage is allowed" in str(exc_info.value)

    def test_should_not_go_back_to_previous_stage(self):
        offer = self._create_valid_offer()
        offer.change_stage(StageType.hr_screening())
        
        with pytest.raises(ValueError) as exc_info:
            offer.change_stage(StageType.resume_sent())
        
        assert "Only next stage is allowed" in str(exc_info.value)

    def test_should_not_change_stage_of_rejected_offer(self):
        offer = self._create_valid_offer()
        offer.mark_rejected("Not a fit")
        
        with pytest.raises(ValueError, match="Cannot modify rejected offer"):
            offer.change_stage(StageType.hr_screening())

    def test_should_mark_offer_as_rejected(self):
        offer = self._create_valid_offer()
        
        offer.mark_rejected("Position closed")
        
        assert offer.is_rejected is True
        assert offer.is_active is False

    def test_should_not_reject_already_rejected_offer(self):
        offer = self._create_valid_offer()
        offer.mark_rejected("First reason")
        
        with pytest.raises(ValueError, match="already rejected"):
            offer.mark_rejected("Second reason")

    def test_should_add_note_to_offer(self):
        offer = self._create_valid_offer()
        
        offer.add_note("HR said they will call back")
        
        assert len(offer.notes) == 1
        assert "HR said" in offer.notes[0]

    def test_should_not_add_empty_note(self):
        offer = self._create_valid_offer()
        
        with pytest.raises(ValueError, match="Note cannot be empty"):
            offer.add_note("")

    def test_should_not_add_note_to_rejected_offer(self):
        offer = self._create_valid_offer()
        offer.mark_rejected("Not a fit")
        
        with pytest.raises(ValueError, match="Cannot modify rejected offer"):
            offer.add_note("This note should not be added")

    def test_should_register_event_when_created(self):
        offer = self._create_valid_offer()
        
        events = offer.events
        assert len(events) >= 1
        assert isinstance(events[0], JobOfferCreatedEvent)

    def test_should_register_event_when_stage_changed(self):
        offer = self._create_valid_offer()
        offer.clear_events()
        
        offer.change_stage(StageType.hr_screening())
        
        events = offer.events
        assert len(events) == 1
        assert isinstance(events[0], StageChangedEvent)

    def test_should_register_event_when_offer_rejected(self):
        offer = self._create_valid_offer()
        offer.clear_events()
        
        offer.mark_rejected("Position closed")
        
        events = offer.events
        assert len(events) == 1
        assert isinstance(events[0], OfferRejectedEvent)

    def test_should_clear_events_after_saving(self):
        offer = self._create_valid_offer()
        assert len(offer.events) >= 1
        
        offer.clear_events()
        
        assert len(offer.events) == 0


def test_should_register_offer_received_event_when_offer_stage_reached():
    company = CompanyName("Google")
    offer = JobOffer(
        offer_id="OFFER-2024-0002",
        company=company,
        position="Senior Python Developer",
        user_id="USR-67890"
    )
    
    offer.change_stage(StageType.hr_screening())
    offer.change_stage(StageType.tech_interview())
    offer.change_stage(StageType.test_task())
    offer.change_stage(StageType.final_interview())
    offer.clear_events()
    
    offer.change_stage(StageType.offer())
    
    events = offer.events
    assert len(events) == 2
    assert isinstance(events[0], StageChangedEvent)
    assert isinstance(events[1], OfferReceivedEvent)
    assert events[1].company_name == "Google"