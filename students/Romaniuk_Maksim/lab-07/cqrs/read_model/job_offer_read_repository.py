# cqrs/read_model/job_offer_read_repository.py
from typing import List, Optional
from abc import ABC, abstractmethod

from cqrs.read_model.job_offer_view import JobOfferView, JobOfferSummaryView


class JobOfferReadRepository(ABC):
    """Интерфейс read-репозитория"""
    
    @abstractmethod
    def save(self, view: JobOfferView) -> None:
        """Сохранить или обновить read модель"""
        pass
    
    @abstractmethod
    def find_by_id(self, offer_id: str) -> Optional[JobOfferView]:
        """Найти по ID"""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[JobOfferView]:
        """Найти все отклики пользователя"""
        pass
    
    @abstractmethod
    def find_active_offers(self, user_id: str) -> List[JobOfferSummaryView]:
        """Найти активные отклики (быстрый запрос)"""
        pass
    
    @abstractmethod
    def find_by_stage(self, user_id: str, stage: str) -> List[JobOfferSummaryView]:
        """Найти отклики по этапу"""
        pass
    
    @abstractmethod
    def delete(self, offer_id: str) -> bool:
        """Удалить read модель"""
        pass


class InMemoryJobOfferReadRepository(JobOfferReadRepository):
    """InMemory реализация read-репозитория"""
    
    def __init__(self):
        self._views: dict[str, JobOfferView] = {}
    
    def save(self, view: JobOfferView) -> None:
        self._views[view.id] = view
    
    def find_by_id(self, offer_id: str) -> Optional[JobOfferView]:
        return self._views.get(offer_id)
    
    def find_by_user_id(self, user_id: str) -> List[JobOfferView]:
        return [v for v in self._views.values() if v.user_id == user_id]
    
    def find_active_offers(self, user_id: str) -> List[JobOfferSummaryView]:
        active = [
            v for v in self._views.values()
            if v.user_id == user_id and v.is_active and not v.is_rejected and not v.is_offer_received
        ]
        return [
            JobOfferSummaryView(
                id=v.id,
                company=v.company,
                position=v.position,
                current_stage=v.current_stage,
                progress_percentage=v.progress_percentage
            )
            for v in active
        ]
    
    def find_by_stage(self, user_id: str, stage: str) -> List[JobOfferSummaryView]:
        filtered = [
            v for v in self._views.values()
            if v.user_id == user_id and v.current_stage == stage
        ]
        return [
            JobOfferSummaryView(
                id=v.id,
                company=v.company,
                position=v.position,
                current_stage=v.current_stage,
                progress_percentage=v.progress_percentage
            )
            for v in filtered
        ]
    
    def delete(self, offer_id: str) -> bool:
        if offer_id in self._views:
            del self._views[offer_id]
            return True
        return False
