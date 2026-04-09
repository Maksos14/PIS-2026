import pytest
from datetime import datetime
import uuid

from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from domain.value_objects.stage_type import StageType, StageTypeEnum
from infrastructure.config.database import DatabaseConfig
from infrastructure.adapter.out.postgres_job_offer_repository import PostgresJobOfferRepository
from infrastructure.adapter.out.console_notification_service import ConsoleNotificationService
from infrastructure.adapter.on.job_offer_controller import JobOfferController
from application.service.job_offer_service_impl import JobOfferServiceImpl
from application.command.create_job_offer_command import CreateJobOfferCommand
from application.command.change_stage_command import ChangeStageCommand
from application.command.add_note_command import AddNoteCommand
from application.command.reject_offer_command import RejectOfferCommand


@pytest.fixture
def e2e_setup():
    """Фикстура для E2E тестов"""
    import tempfile
    import os
    
    # Создаем временную БД
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    db_config = DatabaseConfig(f"sqlite:///{db_path}")
    db_config.create_tables()
    
    session = db_config.get_session()
    repository = PostgresJobOfferRepository(session)
    notification = ConsoleNotificationService()
    
    # Создаем сервис и контроллер
    service = JobOfferServiceImpl(repository, notification)
    controller = JobOfferController(service, service)
    
    yield {
        "repository": repository,
        "service": service,
        "controller": controller,
        "db_config": db_config,
        "session": session,
        "db_path": db_path,
        "db_fd": db_fd
    }
    
    # Cleanup
    session.close()
    db_config.close()
    os.close(db_fd)
    os.unlink(db_path)


class TestRequestFlow:
    """E2E тесты полного сценария работы с откликами"""
    
    def test_full_offer_lifecycle(self, e2e_setup):
        """Тест: полный жизненный цикл отклика"""
        controller = e2e_setup["controller"]
        repository = e2e_setup["repository"]
        
        # Шаг 1: Создание отклика
        request_data = {
            "company": "ООО Ромашка",
            "position": "Python Developer",
            "user_id": "USR-001"
        }
        create_result = controller.create_offer(request_data)
        assert "offer_id" in create_result
        assert create_result["status"] == "created"
        offer_id = create_result["offer_id"]
        
        # Шаг 2: Получение отклика по ID
        get_result = controller.get_offer(offer_id)
        assert get_result["company"] == "ООО Ромашка"
        assert get_result["position"] == "Python Developer"
        assert get_result["status"] == "active"
        assert get_result["current_stage"] == "resume_sent"
        
        # Шаг 3: Смена этапа (HR скрининг)
        stage_request = {"stage": "hr_screening", "note": "Позвонили"}
        # Используем service напрямую для смены этапа
        command = ChangeStageCommand(offer_id, StageTypeEnum.HR_SCREENING, "Позвонили")
        stage_result = e2e_setup["service"].change_stage(command)
        assert stage_result["new_stage"] == "hr_screening"
        
        # Шаг 4: Проверка обновленного этапа
        get_result = controller.get_offer(offer_id)
        assert get_result["current_stage"] == "hr_screening"
        
        # Шаг 5: Добавление заметки
        note_data = {"content": "HR сказала, что команда хорошая"}
        note_command = AddNoteCommand(offer_id, "HR сказала, что команда хорошая")
        note_result = e2e_setup["service"].add_note(note_command)
        assert note_result["notes_added_count"] == 1
        
        # Шаг 6: Проверка заметки
        get_result = controller.get_offer(offer_id)
        assert len(get_result.get("notes", [])) >= 1
        
        # Шаг 7: Смена этапа на техническое интервью
        command2 = ChangeStageCommand(offer_id, StageTypeEnum.TECH_INTERVIEW, "Назначили тех. интервью")
        e2e_setup["service"].change_stage(command2)
        
        # Шаг 8: Проверка прогресса
        get_result = controller.get_offer(offer_id)
        assert get_result["current_stage"] == "tech_interview"
        assert get_result["progress_percentage"] == 40.0
        
        # Шаг 9: Отклонение отклика
        reject_command = RejectOfferCommand(offer_id, "Не подходит по опыту")
        reject_result = e2e_setup["service"].reject_offer(reject_command)
        assert reject_result["new_status"] == "rejected"
        
        # Шаг 10: Проверка финального статуса
        get_result = controller.get_offer(offer_id)
        assert get_result["status"] == "rejected"
    
    def test_create_and_get_offer(self, e2e_setup):
        """Тест: создание и получение отклика"""
        controller = e2e_setup["controller"]
        
        request_data = {
            "company": "Google",
            "position": "Senior Python Developer",
            "user_id": "USR-002"
        }
        create_result = controller.create_offer(request_data)
        assert "offer_id" in create_result
        offer_id = create_result["offer_id"]
        
        get_result = controller.get_offer(offer_id)
        assert get_result["company"] == "Google"
        assert get_result["position"] == "Senior Python Developer"
        assert get_result["user_id"] == "USR-002"
    
    def test_create_offer_missing_fields(self, e2e_setup):
        """Тест: создание отклика с отсутствующими полями"""
        controller = e2e_setup["controller"]
        
        request_data = {"company": "ООО Тест"}
        result = controller.create_offer(request_data)
        
        assert result[1] == 400
        assert "error" in result[0]
    
    def test_get_nonexistent_offer(self, e2e_setup):
        """Тест: получение несуществующего отклика"""
        controller = e2e_setup["controller"]
        
        result = controller.get_offer("OFFER-NOT-EXIST")
        
        assert result[1] == 404
        assert "error" in result[0]
    
    def test_stage_transition_flow(self, e2e_setup):
        """Тест: последовательный переход по всем этапам"""
        service = e2e_setup["service"]
        controller = e2e_setup["controller"]
        
        # Создание
        create_cmd = CreateJobOfferCommand("Microsoft", "C# Developer", "USR-003")
        offer_id = service.create_offer(create_cmd)
        
        # Последовательный переход по этапам
        stages = [
            (StageTypeEnum.HR_SCREENING, "hr_screening"),
            (StageTypeEnum.TECH_INTERVIEW, "tech_interview"),
            (StageTypeEnum.TEST_TASK, "test_task"),
            (StageTypeEnum.FINAL_INTERVIEW, "final_interview"),
            (StageTypeEnum.OFFER, "offer")
        ]
        
        for stage_enum, stage_name in stages:
            command = ChangeStageCommand(offer_id, stage_enum, f"Переход на {stage_name}")
            result = service.change_stage(command)
            assert result["new_stage"] == stage_name
        
        # Проверка финального статуса
        get_result = controller.get_offer(offer_id)
        assert get_result["status"] == "offer_received"
        assert get_result["progress_percentage"] == 100.0
    
    def test_cannot_skip_stages(self, e2e_setup):
        """Тест: нельзя пропускать этапы"""
        service = e2e_setup["service"]
        
        create_cmd = CreateJobOfferCommand("Amazon", "DevOps Engineer", "USR-004")
        offer_id = service.create_offer(create_cmd)
        
        # Пытаемся сразу перейти на TECH_INTERVIEW
        command = ChangeStageCommand(offer_id, StageTypeEnum.TECH_INTERVIEW)
        
        with pytest.raises(ValueError, match="Cannot skip stages"):
            service.change_stage(command)
    
    def test_cannot_change_stage_after_reject(self, e2e_setup):
        """Тест: после отклонения нельзя менять этап"""
        service = e2e_setup["service"]
        
        create_cmd = CreateJobOfferCommand("Meta", "Frontend Developer", "USR-005")
        offer_id = service.create_offer(create_cmd)
        
        # Отклоняем
        reject_cmd = RejectOfferCommand(offer_id, "Не подходит")
        service.reject_offer(reject_cmd)
        
        # Пытаемся сменить этап
        command = ChangeStageCommand(offer_id, StageTypeEnum.HR_SCREENING)
        
        with pytest.raises(ValueError, match="Cannot modify rejected offer"):
            service.change_stage(command)
    
    def test_add_multiple_notes(self, e2e_setup):
        """Тест: добавление нескольких заметок"""
        service = e2e_setup["service"]
        controller = e2e_setup["controller"]
        
        create_cmd = CreateJobOfferCommand("Netflix", "SRE", "USR-006")
        offer_id = service.create_offer(create_cmd)
        
        notes = ["Первая заметка", "Вторая заметка", "Третья заметка"]
        
        for note in notes:
            note_cmd = AddNoteCommand(offer_id, note)
            service.add_note(note_cmd)
        
        get_result = controller.get_offer(offer_id)
        assert len(get_result.get("notes", [])) >= 3
        for note in notes:
            assert any(note in n for n in get_result["notes"])