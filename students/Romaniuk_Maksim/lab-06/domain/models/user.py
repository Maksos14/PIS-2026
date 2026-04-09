# domain/models/user.py
from datetime import datetime
from typing import List, Optional
from enum import Enum


class UserRole(str, Enum):
    """Роли пользователя"""
    JOB_SEEKER = "job_seeker"      # Соискатель
    RECRUITER = "recruiter"         # Рекрутер


class User:
    """
    Entity: Пользователь системы
    
    Идентификатор: USR-0001, USR-0002
    """
    
    def __init__(self, user_id: str, email: str, full_name: str):
        """
        :param user_id: ID формата USR-0001
        :param email: Электронная почта (уникальная)
        :param full_name: Полное имя
        """
        self._id = user_id
        self._email = email
        self._full_name = full_name
        self._role = UserRole.JOB_SEEKER
        self._is_active = True
        self._job_offer_ids: List[str] = []
        self._project_ids: List[str] = []
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    def change_email(self, new_email: str) -> None:
        """Сменить email с валидацией формата"""
        if not new_email or "@" not in new_email:
            raise ValueError(f"Некорректный формат email: {new_email}")
        
        self._email = new_email
        self._updated_at = datetime.now()
    
    def change_name(self, new_name: str) -> None:
        """Сменить полное имя"""
        if not new_name or not new_name.strip():
            raise ValueError("Имя не может быть пустым")
        
        self._full_name = new_name.strip()
        self._updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """Деактивировать пользователя"""
        if not self._is_active:
            raise ValueError(f"Пользователь {self._id} уже деактивирован")
        
        self._is_active = False
        self._updated_at = datetime.now()
    
    def activate(self) -> None:
        """Активировать пользователя"""
        if self._is_active:
            raise ValueError(f"Пользователь {self._id} уже активен")
        
        self._is_active = True
        self._updated_at = datetime.now()
    
    def add_job_offer(self, offer_id: str) -> None:
        """Привязать отклик к пользователю"""
        if offer_id in self._job_offer_ids:
            raise ValueError(f"Отклик {offer_id} уже привязан к пользователю {self._id}")
        
        self._job_offer_ids.append(offer_id)
        self._updated_at = datetime.now()
    
    def add_project(self, project_id: str) -> None:
        """Привязать проект к пользователю"""
        if project_id in self._project_ids:
            raise ValueError(f"Проект {project_id} уже привязан к пользователю {self._id}")
        
        self._project_ids.append(project_id)
        self._updated_at = datetime.now()
    
    def promote_to_recruiter(self) -> None:
        """Повысить роль до рекрутера"""
        self._role = UserRole.RECRUITER
        self._updated_at = datetime.now()
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def full_name(self) -> str:
        return self._full_name
    
    @property
    def role(self) -> UserRole:
        return self._role
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def job_offer_ids(self) -> List[str]:
        return self._job_offer_ids.copy()
    
    @property
    def project_ids(self) -> List[str]:
        return self._project_ids.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def __eq__(self, other) -> bool:
        """Равенство по ID"""
        if not isinstance(other, User):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"User(id={self._id}, email={self._email}, name={self._full_name})"
