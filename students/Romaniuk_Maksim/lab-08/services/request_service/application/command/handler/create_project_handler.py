# application/command/handlers/create_project_handler.py
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from domain.models.project import Project
from port.out.job_offer_repository import JobOfferRepository
from port.out.notification_service import NotificationService
from command.create_project_command import CreateProjectCommand


class CreateProjectHandler:
    """Обработчик команды создания проекта"""
    
    def __init__(self, repository: JobOfferRepository, notification_service: NotificationService):
        self._repository = repository
        self._notification_service = notification_service
    
    def handle(self, command: CreateProjectCommand) -> str:
        # 1. Валидация входных данных
        if not command.name or not command.name.strip():
            raise ValueError("Project name is required")
        if not command.user_id or not command.user_id.strip():
            raise ValueError("User ID is required")
        
        # 2. Создание агрегата
        project_id = f"PRJ-{uuid.uuid4().hex[:4].upper()}"
        
        project = Project(
            project_id=project_id,
            name=command.name,
            user_id=command.user_id,
            description=command.description or ""
        )
        
        # 3. Сохранение через Repository
        self._repository.save(project)
        
        # 4. Публикация доменных событий
        for event in project.events:
            self._notification_service.publish(event)
        project.clear_events()
        
        return project_id