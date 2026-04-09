import pytest
from datetime import datetime, timedelta

from domain.models.job_offer import JobOffer
from domain.models.user import User
from domain.models.project import Project
from domain.value_objects.company_name import CompanyName
from domain.value_objects.offer_status import OfferStatus
from domain.value_objects.stage_type import StageType
from domain.value_objects.reminder_time import ReminderTime


# ==================== Тесты Value Objects ====================

class TestCompanyName:
    
    def test_create_valid_company_name(self):
        name = CompanyName("ООО Яндекс")
        assert name.value == "ООО Яндекс"
    
    def test_company_name_trim_whitespace(self):
        name = CompanyName("  Google  ")
        assert name.value == "Google"
    
    def test_company_name_too_short(self):
        with pytest.raises(ValueError, match="Company name too short"):
            CompanyName("A")
    
    def test_company_name_too_long(self):
        long_name = "A" * 101
        with pytest.raises(ValueError, match="Company name too long"):
            CompanyName(long_name)
    
    def test_company_name_empty(self):
        with pytest.raises(ValueError, match="Company name cannot be empty"):
            CompanyName("")
    
    def test_company_name_short_name_truncate(self):
        long_name = "Very Long Company Name Exceeds Twenty"
        name = CompanyName(long_name)
        assert len(name.short_name) <= 20
        assert name.short_name.endswith("...")


class TestOfferStatus:
    
    def test_active_status(self):
        status = OfferStatus.active()
        assert status.is_active is True
        assert status.is_rejected is False
        assert status.is_offer_received is False
        assert status.can_change_stage() is True
    
    def test_rejected_status(self):
        status = OfferStatus.rejected()
        assert status.is_active is False
        assert status.is_rejected is True
        assert status.can_change_stage() is False
    
    def test_offer_received_status(self):
        status = OfferStatus.offer_received()
        assert status.is_active is False
        assert status.is_offer_received is True
        assert status.can_change_stage() is False


class TestStageType:
    
    def test_stage_order(self):
        assert StageType.resume_sent().order == 0
        assert StageType.hr_screening().order == 1
        assert StageType.tech_interview().order == 2
        assert StageType.test_task().order == 3
        assert StageType.final_interview().order == 4
        assert StageType.offer().order == 5
    
    def test_can_transition_to_next(self):
        current = StageType.resume_sent()
        next_stage = StageType.hr_screening()
        assert current.can_transition_to(next_stage) is True
    
    def test_cannot_skip_stages(self):
        current = StageType.resume_sent()
        skip = StageType.tech_interview()
        assert current.can_transition_to(skip) is False
    
    def test_cannot_go_back(self):
        current = StageType.hr_screening()
        previous = StageType.resume_sent()
        assert current.can_transition_to(previous) is False
    
    def test_is_first_stage(self):
        assert StageType.resume_sent().is_first is True
        assert StageType.hr_screening().is_first is False
    
    def test_is_last_stage(self):
        assert StageType.offer().is_last is True
        assert StageType.final_interview().is_last is False


class TestReminderTime:
    
    def test_create_future_reminder(self):
        future = datetime.now() + timedelta(days=1)
        reminder = ReminderTime(future)
        assert reminder.value == future
    
    def test_cannot_create_past_reminder(self):
        past = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="cannot be in the past"):
            ReminderTime(past)
    
    def test_is_urgent(self):
        soon = datetime.now() + timedelta(minutes=30)
        reminder = ReminderTime(soon)
        assert reminder.is_urgent(60) is True
    
    def test_not_urgent(self):
        later = datetime.now() + timedelta(hours=2)
        reminder = ReminderTime(later)
        assert reminder.is_urgent(60) is False
    
    def test_format_relative(self):
        soon = datetime.now() + timedelta(hours=5)
        reminder = ReminderTime(soon)
        assert "через" in reminder.format_relative()


# ==================== Тесты агрегата JobOffer ====================

class TestJobOffer:
    
    def setup_method(self):
        self.company = CompanyName("ООО Тест")
        self.offer = JobOffer(
            offer_id="OFFER-2024-0001",
            company=self.company,
            position="Python Developer",
            user_id="USR-001"
        )
    
    def test_create_job_offer_success(self):
        assert self.offer.id == "OFFER-2024-0001"
        assert str(self.offer.company) == "ООО Тест"
        assert self.offer.position == "Python Developer"
        assert self.offer.user_id == "USR-001"
        assert self.offer.is_active is True
        assert self.offer.current_stage == StageType.resume_sent()
    
    def test_create_offer_invalid_id_format(self):
        with pytest.raises(ValueError, match="Invalid offer ID format"):
            JobOffer("INVALID", self.company, "Dev", "USR-001")
    
    def test_create_offer_empty_position(self):
        with pytest.raises(ValueError, match="Position cannot be empty"):
            JobOffer("OFFER-2024-0001", self.company, "", "USR-001")
    
    def test_change_stage_to_next(self):
        self.offer.change_stage(StageType.hr_screening())
        assert self.offer.current_stage == StageType.hr_screening()
    
    def test_cannot_skip_stages(self):
        with pytest.raises(ValueError, match="Only next stage is allowed"):
            self.offer.change_stage(StageType.tech_interview())
    
    def test_cannot_go_back(self):
        self.offer.change_stage(StageType.hr_screening())
        with pytest.raises(ValueError, match="Only next stage is allowed"):
            self.offer.change_stage(StageType.resume_sent())
    
    def test_change_stage_with_note(self):
        self.offer.change_stage(StageType.hr_screening(), note="Позвонили")
        assert len(self.offer.notes) == 1
        assert "Позвонили" in self.offer.notes[0]
    
    def test_mark_offer_as_rejected(self):
        self.offer.mark_rejected("Не подходит")
        assert self.offer.is_rejected is True
        assert self.offer.is_active is False
    
    def test_cannot_reject_already_rejected(self):
        self.offer.mark_rejected("Причина")
        with pytest.raises(ValueError, match="already rejected"):
            self.offer.mark_rejected("Другая причина")
    
    def test_cannot_change_stage_of_rejected_offer(self):
        self.offer.mark_rejected("Не подходит")
        with pytest.raises(ValueError, match="Cannot modify rejected offer"):
            self.offer.change_stage(StageType.hr_screening())
    
    def test_add_note(self):
        self.offer.add_note("Важная заметка")
        assert len(self.offer.notes) == 1
        assert "Важная заметка" in self.offer.notes[0]
    
    def test_cannot_add_empty_note(self):
        with pytest.raises(ValueError, match="Note cannot be empty"):
            self.offer.add_note("")
    
    def test_cannot_add_note_to_rejected_offer(self):
        self.offer.mark_rejected("Не подходит")
        with pytest.raises(ValueError, match="Cannot modify rejected offer"):
            self.offer.add_note("Заметка")
    
    def test_progress_percentage(self):
        assert self.offer.progress_percentage == 0.0
        self.offer.change_stage(StageType.hr_screening())
        assert self.offer.progress_percentage == 20.0
        self.offer.change_stage(StageType.tech_interview())
        assert self.offer.progress_percentage == 40.0
        self.offer.change_stage(StageType.test_task())
        assert self.offer.progress_percentage == 60.0
        self.offer.change_stage(StageType.final_interview())
        assert self.offer.progress_percentage == 80.0
        self.offer.change_stage(StageType.offer())
        assert self.offer.progress_percentage == 100.0
    
    def test_offer_received_auto_status(self):
        self.offer.change_stage(StageType.hr_screening())
        self.offer.change_stage(StageType.tech_interview())
        self.offer.change_stage(StageType.test_task())
        self.offer.change_stage(StageType.final_interview())
        self.offer.change_stage(StageType.offer())
        assert self.offer.is_offer_received is True
    
    def test_register_event_on_creation(self):
        events = self.offer.events
        assert len(events) >= 1
        from domain.events.domain_events import JobOfferCreatedEvent
        assert isinstance(events[0], JobOfferCreatedEvent)
    
    def test_register_event_on_stage_change(self):
        self.offer.clear_events()
        self.offer.change_stage(StageType.hr_screening())
        events = self.offer.events
        assert len(events) == 1
        from domain.events.domain_events import StageChangedEvent
        assert isinstance(events[0], StageChangedEvent)
    
    def test_register_event_on_reject(self):
        self.offer.clear_events()
        self.offer.mark_rejected("Не подходит")
        events = self.offer.events
        assert len(events) == 1
        from domain.events.domain_events import OfferRejectedEvent
        assert isinstance(events[0], OfferRejectedEvent)
    
    def test_clear_events(self):
        assert len(self.offer.events) >= 1
        self.offer.clear_events()
        assert len(self.offer.events) == 0


# ==================== Тесты сущности User ====================

class TestUser:
    
    def setup_method(self):
        self.user = User(
            user_id="USR-001",
            email="user@example.com",
            full_name="Иван Иванов"
        )
    
    def test_create_user_success(self):
        assert self.user.id == "USR-001"
        assert self.user.email == "user@example.com"
        assert self.user.full_name == "Иван Иванов"
        assert self.user.is_active is True
    
    def test_change_email(self):
        self.user.change_email("new@example.com")
        assert self.user.email == "new@example.com"
    
    def test_change_email_invalid(self):
        with pytest.raises(ValueError, match="Некорректный формат email"):
            self.user.change_email("invalid")
    
    def test_deactivate_user(self):
        self.user.deactivate()
        assert self.user.is_active is False
    
    def test_cannot_deactivate_already_deactivated(self):
        self.user.deactivate()
        with pytest.raises(ValueError, match="уже деактивирован"):
            self.user.deactivate()
    
    def test_add_job_offer(self):
        self.user.add_job_offer("OFFER-001")
        assert "OFFER-001" in self.user.job_offer_ids
    
    def test_cannot_add_duplicate_offer(self):
        self.user.add_job_offer("OFFER-001")
        with pytest.raises(ValueError, match="уже привязан"):
            self.user.add_job_offer("OFFER-001")
    
    def test_promote_to_recruiter(self):
        self.user.promote_to_recruiter()
        assert self.user.role.value == "recruiter"


# ==================== Тесты сущности Project ====================

class TestProject:
    
    def setup_method(self):
        self.project = Project(
            project_id="PRJ-001",
            name="Весенний поиск",
            user_id="USR-001",
            description="Поиск работы весной 2026"
        )
    
    def test_create_project_success(self):
        assert self.project.id == "PRJ-001"
        assert self.project.name == "Весенний поиск"
        assert self.project.user_id == "USR-001"
        assert self.project.status.value == "draft"
    
    def test_add_job_offer(self):
        self.project.add_job_offer("OFFER-001")
        assert "OFFER-001" in self.project.job_offer_ids
        assert self.project.offers_count == 1
    
    def test_auto_activate_when_min_offers_reached(self):
        self.project.add_job_offer("OFFER-001")
        self.project.add_job_offer("OFFER-002")
        self.project.add_job_offer("OFFER-003")
        assert self.project.status.value == "active"
    
    def test_remove_job_offer(self):
        self.project.add_job_offer("OFFER-001")
        self.project.remove_job_offer("OFFER-001")
        assert "OFFER-001" not in self.project.job_offer_ids
    
    def test_activate_project(self):
        self.project.add_job_offer("OFFER-001")
        self.project.add_job_offer("OFFER-002")
        self.project.add_job_offer("OFFER-003")
        assert self.project.status.value == "active"
    
    def test_pause_project(self):
        self.project.add_job_offer("OFFER-001")
        self.project.add_job_offer("OFFER-002")
        self.project.add_job_offer("OFFER-003")
        self.project.pause()
        assert self.project.status.value == "paused"
    
    def test_complete_project(self):
        self.project.complete()
        assert self.project.status.value == "completed"
    
    def test_cannot_add_offer_to_completed_project(self):
        self.project.complete()
        with pytest.raises(ValueError, match="Нельзя добавить отклик в завершённый"):
            self.project.add_job_offer("OFFER-001")