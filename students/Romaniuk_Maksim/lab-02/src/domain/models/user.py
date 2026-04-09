from datetime import datetime
from typing import List
from enum import Enum


class UserRole(str, Enum):
    """Роли пользователя"""
    JOB_SEEKER = "job_seeker"      # Соискатель
    RECRUITER = "recruiter"         # Рекрутер (если понадобится)


class User:
    """Доменная модель: Пользователь системы"""
    
    def __init__(self, user_id: str, email: str, full_name: str):
        self.id = user_id
        self.email = email
        self.full_name = full_name
        self.role = UserRole.JOB_SEEKER
        self.is_active = True
        self.created_at = datetime.now()
        self.job_offer_ids: List[str] = []  # ID откликов пользователя
    
    def deactivate(self):
        """Деактивировать пользователя"""
        self.is_active = False
        # Полную бизнес-логику (отмена напоминаний и т.д.) добавим в Lab #3
    
    def add_job_offer(self, offer_id: str):
        """Привязать отклик к пользователю"""
        self.job_offer_ids.append(offer_id)
        # Полную бизнес-логику добавим в Lab #3
    
    def change_email(self, new_email: str):
        """Сменить email"""
        self.email = new_email
        # Полную бизнес-логику (валидацию email) добавим в Lab #3
