from datetime import datetime
from typing import List
from enum import Enum


class ProjectStatus(str, Enum):
    """Статус проекта/кампании"""
    ACTIVE = "active"      # Активный поиск
    PAUSED = "paused"      # На паузе
    COMPLETED = "completed" # Завершён (оффер получен)
    ARCHIVED = "archived"   # В архиве


class Project:
    """Доменная модель: Проект/кампания поиска работы"""
    
    def __init__(self, project_id: str, name: str, user_id: str, description: str = ""):
        self.id = project_id
        self.name = name                    # Например: "Весенний поиск 2024"
        self.description = description       # Описание стратегии
        self.user_id = user_id              # Владелец проекта
        self.status = ProjectStatus.ACTIVE
        self.job_offer_ids: List[str] = []  # ID откликов в этом проекте
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_job_offer(self, offer_id: str):
        """Добавить отклик в проект"""
        self.job_offer_ids.append(offer_id)
        self.updated_at = datetime.now()
        # Полную бизнес-логику добавим в Lab #3
    
    def pause(self):
        """Приостановить проект"""
        self.status = ProjectStatus.PAUSED
        self.updated_at = datetime.now()
        # Полную бизнес-логику (пауза напоминаний) добавим в Lab #3
    
    def complete(self):
        """Завершить проект (оффер получен)"""
        self.status = ProjectStatus.COMPLETED
        self.updated_at = datetime.now()
        # Полную бизнес-логику добавим в Lab #3
    
    def archive(self):
        """Архивировать проект"""
        self.status = ProjectStatus.ARCHIVED
        self.updated_at = datetime.now()
        # Полную бизнес-логику добавим в Lab #3
