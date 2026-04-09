import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from domain.value_objects.stage_type import StageType, StageTypeEnum
from domain.events.domain_events import (
    JobOfferCreatedEvent,
    StageChangedEvent,
    OfferRejectedEvent,
    NoteAddedEvent
)

from application.command.create_job_offer_command import CreateJobOfferCommand
from application.command.change_stage_command import ChangeStageCommand
from application.command.add_note_command import AddNoteCommand
from application.command.reject_offer_command import RejectOfferCommand
from application.command.create_project_command import CreateProjectCommand

from application.command.handler.create_job_offer_handler import CreateJobOfferHandler
from application.command.handler.change_stage_handler import ChangeStageHandler
from application.command.handler.add_note_handler import AddNoteHandler
from application.command.handler.reject_offer_handler import RejectOfferHandler
from application.command.handler.create_project_handler import CreateProjectHandler

from application.query.get_job_offer_by_id_query import GetJobOfferByIdQuery
from application.query.dto.job_offer_dto import JobOfferDto
from application.query.handlers.get_job_offer_by_id_handler import GetJobOfferByIdHandler


# ==================== Тесты CreateJobOfferHandler ====================

class TestCreateJobOfferHandler:
    
    def setup_method(self):
        self.mock_repository = Mock()
        self.mock_publisher = Mock()
        self.handler = CreateJobOfferHandler(self.mock_repository, self.mock_publisher)
    
    def test_handle_creates_offer_successfully(self):
        command = CreateJobOfferCommand(
            company="ООО Тест",
            position="Python Developer",
            user_id="USR-001"
        )
        
        offer_id = self.handler.handle(command)
        
        assert offer_id.startswith("OFFER-2026-")
        self.mock_repository.save.assert_called_once()
        self.mock_publisher.publish.assert_called_once()
    
    def test_handle_validates_company(self):
        command = CreateJobOfferCommand(
            company="",
            position="Python Developer",
            user_id="USR-001"
        )
        
        with pytest.raises(ValueError, match="Company name cannot be empty"):
            self.handler.handle(command)
    
    def test_handle_validates_position(self):
        command = CreateJobOfferCommand(
            company="ООО Тест",
            position="",
            user_id="USR-001"
        )
        
        with pytest.raises(ValueError, match="Position cannot be empty"):
            self.handler.handle(command)
    
    def test_handle_validates_user_id(self):
        command = CreateJobOfferCommand(
            company="ООО Тест",
            position="Python Developer",
            user_id=""
        )
        
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            self.handler.handle(command)
    
    def test_handle_publishes_events(self):
        command = CreateJobOfferCommand(
            company="ООО Тест",
            position="Python Developer",
            user_id="USR-001"
        )
        
        offer_id = self.handler.handle(command)
        
        self.mock_publisher.publish.assert_called_once()
        args = self.mock_publisher.publish.call_args[0][0]
        assert len(args) >= 1
        assert isinstance(args[0], JobOfferCreatedEvent)


# ==================== Тесты ChangeStageHandler ====================

class TestChangeStageHandler:
    
    def setup_method(self):
        self.mock_repository = Mock()
        self.mock_publisher = Mock()
        self.handler = ChangeStageHandler(self.mock_repository, self.mock_publisher)
    
    def test_handle_changes_stage_successfully(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        command = ChangeStageCommand(
            offer_id="OFFER-2024-0001",
            new_stage=StageTypeEnum.HR_SCREENING
        )
        
        result = self.handler.handle(command)
        
        assert result["offer_id"] == "OFFER-2024-0001"
        assert result["old_stage"] == "resume_sent"
        assert result["new_stage"] == "hr_screening"
        self.mock_repository.save.assert_called_once()
        self.mock_publisher.publish.assert_called_once()
    
    def test_handle_offer_not_found(self):
        self.mock_repository.find_by_id.return_value = None
        
        command = ChangeStageCommand(
            offer_id="OFFER-2024-0001",
            new_stage=StageTypeEnum.HR_SCREENING
        )
        
        with pytest.raises(ValueError, match="not found"):
            self.handler.handle(command)
    
    def test_handle_cannot_change_stage_of_rejected_offer(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        offer.mark_rejected("Not a fit")
        self.mock_repository.find_by_id.return_value = offer
        
        command = ChangeStageCommand(
            offer_id="OFFER-2024-0001",
            new_stage=StageTypeEnum.HR_SCREENING
        )
        
        with pytest.raises(ValueError, match="Cannot change stage of rejected offer"):
            self.handler.handle(command)
    
    def test_handle_cannot_skip_stages(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        command = ChangeStageCommand(
            offer_id="OFFER-2024-0001",
            new_stage=StageTypeEnum.TECH_INTERVIEW
        )
        
        with pytest.raises(ValueError, match="Cannot skip stages"):
            self.handler.handle(command)
    
    def test_handle_publishes_stage_changed_event(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        command = ChangeStageCommand(
            offer_id="OFFER-2024-0001",
            new_stage=StageTypeEnum.HR_SCREENING,
            note="Позвонили"
        )
        
        self.handler.handle(command)
        
        self.mock_publisher.publish.assert_called_once()
        args = self.mock_publisher.publish.call_args[0][0]
        assert len(args) >= 1
        assert isinstance(args[0], StageChangedEvent)


# ==================== Тесты AddNoteHandler ====================

class TestAddNoteHandler:
    
    def setup_method(self):
        self.mock_repository = Mock()
        self.mock_publisher = Mock()
        self.handler = AddNoteHandler(self.mock_repository, self.mock_publisher)
    
    def test_handle_adds_note_successfully(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        command = AddNoteCommand(
            offer_id="OFFER-2024-0001",
            content="Важная заметка"
        )
        
        result = self.handler.handle(command)
        
        assert result["offer_id"] == "OFFER-2024-0001"
        assert result["notes_added_count"] == 1
        self.mock_repository.save.assert_called_once()
    
    def test_handle_offer_not_found(self):
        self.mock_repository.find_by_id.return_value = None
        
        command = AddNoteCommand(
            offer_id="OFFER-2024-0001",
            content="Заметка"
        )
        
        with pytest.raises(ValueError, match="not found"):
            self.handler.handle(command)
    
    def test_handle_cannot_add_note_to_rejected_offer(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        offer.mark_rejected("Not a fit")
        self.mock_repository.find_by_id.return_value = offer
        
        command = AddNoteCommand(
            offer_id="OFFER-2024-0001",
            content="Заметка"
        )
        
        with pytest.raises(ValueError, match="Cannot add note to rejected offer"):
            self.handler.handle(command)
    
    def test_handle_empty_note(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        command = AddNoteCommand(
            offer_id="OFFER-2024-0001",
            content=""
        )
        
        with pytest.raises(ValueError, match="Note cannot be empty"):
            self.handler.handle(command)
    
    def test_handle_publishes_note_added_event(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        command = AddNoteCommand(
            offer_id="OFFER-2024-0001",
            content="Новая заметка"
        )
        
        self.handler.handle(command)
        
        self.mock_publisher.publish.assert_called_once()
        args = self.mock_publisher.publish.call_args[0][0]
        assert len(args) >= 1
        assert isinstance(args[0], NoteAddedEvent)


# ==================== Тесты RejectOfferHandler ====================

class TestRejectOfferHandler:
    
    def setup_method(self):
        self.mock_repository = Mock()
        self.mock_publisher = Mock()
        self.handler = RejectOfferHandler(self.mock_repository, self.mock_publisher)
    
    def test_handle_rejects_offer_successfully(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        command = RejectOfferCommand(
            offer_id="OFFER-2024-0001",
            reason="Не подходит по требованиям"
        )
        
        result = self.handler.handle(command)
        
        assert result["offer_id"] == "OFFER-2024-0001"
        assert result["old_status"] == "active"
        assert result["new_status"] == "rejected"
        self.mock_repository.save.assert_called_once()
    
    def test_handle_offer_not_found(self):
        self.mock_repository.find_by_id.return_value = None
        
        command = RejectOfferCommand(offer_id="OFFER-2024-0001")
        
        with pytest.raises(ValueError, match="not found"):
            self.handler.handle(command)
    
    def test_handle_cannot_reject_already_rejected(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        offer.mark_rejected("First reason")
        self.mock_repository.find_by_id.return_value = offer
        
        command = RejectOfferCommand(offer_id="OFFER-2024-0001")
        
        with pytest.raises(ValueError, match="already rejected"):
            self.handler.handle(command)
    
    def test_handle_publishes_rejected_event(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        command = RejectOfferCommand(
            offer_id="OFFER-2024-0001",
            reason="Not a fit"
        )
        
        self.handler.handle(command)
        
        self.mock_publisher.publish.assert_called_once()
        args = self.mock_publisher.publish.call_args[0][0]
        assert len(args) >= 1
        assert isinstance(args[0], OfferRejectedEvent)


# ==================== Тесты Query Handlers ====================

class TestGetJobOfferByIdHandler:
    
    def setup_method(self):
        self.mock_repository = Mock()
        self.handler = GetJobOfferByIdHandler(self.mock_repository)
    
    def test_handle_returns_dto_when_offer_exists(self):
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-0001", company, "Python Dev", "USR-001")
        self.mock_repository.find_by_id.return_value = offer
        
        query = GetJobOfferByIdQuery(offer_id="OFFER-2024-0001")
        result = self.handler.handle(query)
        
        assert isinstance(result, JobOfferDto)
        assert result.id == "OFFER-2024-0001"
        assert result.company == "ООО Тест"
        assert result.position == "Python Dev"
    
    def test_handle_returns_none_when_offer_not_found(self):
        self.mock_repository.find_by_id.return_value = None
        
        query = GetJobOfferByIdQuery(offer_id="OFFER-2024-0001")
        result = self.handler.handle(query)
        
        assert result is None