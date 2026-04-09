# domain/models/project.py
from datetime import datetime
from typing import List, Optional
from enum import Enum


class ProjectStatus(str, Enum):
    """Статус проекта/кампании"""
    DRAFT = "draft"          # Черновик
    ACTIVE = "active"        # Активный поиск
    PAUSED = "paused"        # На паузе
    COMPLETED = "completed"  # Завершён (оффер получен)
    ARCHIVED = "archived"    # В архиве


class Project:
    """
    Entity: Проект/кампания поиска работы
    
    Идентификатор: PRJ-0001, PRJ-0002
    
    Проект позволяет группировать отклики по стратегиям:
    - "Весенний поиск 2024"
    - "IT-компании с релокацией"
    - "Стартапы с гибким графиком"
    """
    
    # Минимальное количество откликов для активного проекта
    MIN_OFFERS_FOR_ACTIVE = 3
    
    def __init__(self, project_id: str, name: str, user_id: str, description: str = ""):
        """
        :param project_id: ID формата PRJ-0001
        :param name: Название проекта
        :param user_id: Владелец проекта (USR-XXXX)
        :param description: Описание стратегии
        """
        self._id = project_id
        self._name = name
        self._description = description
        self._user_id = user_id
        self._status = ProjectStatus.DRAFT
        self._job_offer_ids: List[str] = []
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    def add_job_offer(self, offer_id: str) -> None:
        """Добавить отклик в проект"""
        if self._status in [ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED]:
            raise ValueError(f"Нельзя добавить отклик в завершённый или архивный проект {self._id}")
        
        if offer_id in self._job_offer_ids:
            raise ValueError(f"Отклик {offer_id} уже в проекте {self._id}")
        
        self._job_offer_ids.append(offer_id)
        self._updated_at = datetime.now()
        
        # Автоматически активируем проект, если достаточно откликов и он в черновике
        if self._status == ProjectStatus.DRAFT and len(self._job_offer_ids) >= self.MIN_OFFERS_FOR_ACTIVE:
            self._status = ProjectStatus.ACTIVE
    
    def remove_job_offer(self, offer_id: str) -> None:
        """Удалить отклик из проекта"""
        if self._status in [ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED]:
            raise ValueError(f"Нельзя удалить отклик из завершённого или архивного проекта {self._id}")
        
        if offer_id not in self._job_offer_ids:
            raise ValueError(f"Отклик {offer_id} не найден в проекте {self._id}")
        
        self._job_offer_ids.remove(offer_id)
        self._updated_at = datetime.now()
        
        # Если откликов меньше минимума, возвращаем в черновик
        if len(self._job_offer_ids) < self.MIN_OFFERS_FOR_ACTIVE and self._status == ProjectStatus.ACTIVE:
            self._status = ProjectStatus.DRAFT
    
    def activate(self) -> None:
        """Активировать проект"""
        if self._status == ProjectStatus.ACTIVE:
            raise ValueError(f"Проект {self._id} уже активен")
        
        if self._status == ProjectStatus.COMPLETED:
            raise ValueError(f"Нельзя активировать завершённый проект {self._id}")
        
        if len(self._job_offer_ids) < self.MIN_OFFERS_FOR_ACTIVE:
            raise ValueError(f"Нельзя активировать проект: недостаточно откликов (мин. {self.MIN_OFFERS_FOR_ACTIVE})")
        
        self._status = ProjectStatus.ACTIVE
        self._updated_at = datetime.now()
    
    def pause(self) -> None:
        """Приостановить проект"""
        if self._status != ProjectStatus.ACTIVE:
            raise ValueError(f"Можно приостановить только активный проект. Текущий статус: {self._status}")
        
        self._status = ProjectStatus.PAUSED
        self._updated_at = datetime.now()
    
    def resume(self) -> None:
        """Возобновить проект из паузы"""
        if self._status != ProjectStatus.PAUSED:
            raise ValueError(f"Можно возобновить только проект на паузе. Текущий статус: {self._status}")
        
        if len(self._job_offer_ids) < self.MIN_OFFERS_FOR_ACTIVE:
            raise ValueError(f"Нельзя возобновить проект: недостаточно откликов (мин. {self.MIN_OFFERS_FOR_ACTIVE})")
        
        self._status = ProjectStatus.ACTIVE
        self._updated_at = datetime.now()
    
    def complete(self) -> None:
        """Завершить проект (оффер получен)"""
        if self._status == ProjectStatus.COMPLETED:
            raise ValueError(f"Проект {self._id} уже завершён")
        
        if self._status == ProjectStatus.ARCHIVED:
            raise ValueError(f"Нельзя завершить архивный проект {self._id}")
        
        self._status = ProjectStatus.COMPLETED
        self._updated_at = datetime.now()
    
    def archive(self) -> None:
        """Архивировать проект"""
        if self._status == ProjectStatus.ARCHIVED:
            raise ValueError(f"Проект {self._id} уже в архиве")
        
        self._status = ProjectStatus.ARCHIVED
        self._updated_at = datetime.now()
    
    def update_name(self, new_name: str) -> None:
        """Изменить название проекта"""
        if not new_name or not new_name.strip():
            raise ValueError("Название проекта не может быть пустым")
        
        self._name = new_name.strip()
        self._updated_at = datetime.now()
    
    def update_description(self, new_description: str) -> None:
        """Изменить описание проекта"""
        self._description = new_description
        self._updated_at = datetime.now()
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def status(self) -> ProjectStatus:
        return self._status
    
    @property
    def job_offer_ids(self) -> List[str]:
        return self._job_offer_ids.copy()
    
    @property
    def offers_count(self) -> int:
        return len(self._job_offer_ids)
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def __eq__(self, other) -> bool:
        """Равенство по ID"""
        if not isinstance(other, Project):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"Project(id={self._id}, name={self._name}, status={self._status.value})"
