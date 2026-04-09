from abc import ABC, abstractmethod
from typing import Optional

from command.create_job_offer_command import CreateJobOfferCommand
from command.change_stage_command import ChangeStageCommand
from command.add_note_command import AddNoteCommand
from command.reject_offer_command import RejectOfferCommand
from command.create_project_command import CreateProjectCommand
from query.get_job_offer_by_id_query import GetJobOfferByIdQuery
from query.list_active_offers_query import ListActiveOffersQuery
from query.list_offers_by_stage_query import ListOffersByStageQuery
from query.dto.job_offer_dto import JobOfferDto
from query.dto.stage_dto import StagesProgressDto


class JobOfferService(ABC):
    """Входящий порт: сервис для работы с откликами"""
    
    # ========== Commands ==========
    
    @abstractmethod
    def create_offer(self, command: CreateJobOfferCommand) -> str:
        """Создать отклик. Возвращает ID."""
        pass
    
    @abstractmethod
    def change_stage(self, command: ChangeStageCommand) -> dict:
        """Изменить этап отбора."""
        pass
    
    @abstractmethod
    def add_note(self, command: AddNoteCommand) -> dict:
        """Добавить заметку к отклику."""
        pass
    
    @abstractmethod
    def reject_offer(self, command: RejectOfferCommand) -> dict:
        """Отклонить отклик."""
        pass
    
    @abstractmethod
    def create_project(self, command: CreateProjectCommand) -> str:
        """Создать проект. Возвращает ID."""
        pass
    
    # ========== Queries ==========
    
    @abstractmethod
    def get_offer_by_id(self, query: GetJobOfferByIdQuery) -> Optional[JobOfferDto]:
        """Получить отклик по ID."""
        pass
    
    @abstractmethod
    def list_active_offers(self, query: ListActiveOffersQuery) -> dict:
        """Получить список активных откликов."""
        pass
    
    @abstractmethod
    def list_offers_by_stage(self, query: ListOffersByStageQuery) -> dict:
        """Получить список откликов по этапу."""
        pass
    
    @abstractmethod
    def get_stages_progress(self, query: GetJobOfferByIdQuery) -> Optional[StagesProgressDto]:
        """Получить прогресс по этапам для отклика."""
        pass
