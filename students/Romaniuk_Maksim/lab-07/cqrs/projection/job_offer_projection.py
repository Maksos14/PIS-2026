# cqrs/projection/job_offer_projection.py
from datetime import datetime
from typing import Optional

from domain.events.domain_events import (
    DomainEvent,
    JobOfferCreatedEvent,
    StageChangedEvent,
    OfferRejectedEvent,
    OfferReceivedEvent,
    NoteAddedEvent
)
from cqrs.read_model.job_offer_view import JobOfferView
from cqrs.read_model.job_offer_read_repository import JobOfferReadRepository
from domain.value_objects.stage_type import StageType, STAGE_ORDER


class JobOfferProjection:
    """
    Проекция: обновляет Read Model на основе доменных событий
    """
    
    def __init__(self, read_repository: JobOfferReadRepository):
        self._read_repository = read_repository
    
    def handle_event(self, event: DomainEvent) -> None:
        """Обработка доменного события"""
        if isinstance(event, JobOfferCreatedEvent):
            self._on_job_offer_created(event)
        elif isinstance(event, StageChangedEvent):
            self._on_stage_changed(event)
        elif isinstance(event, OfferRejectedEvent):
            self._on_offer_rejected(event)
        elif isinstance(event, OfferReceivedEvent):
            self._on_offer_received(event)
        elif isinstance(event, NoteAddedEvent):
            self._on_note_added(event)
    
    def _on_job_offer_created(self, event: JobOfferCreatedEvent) -> None:
        """Создание отклика → создание read модели"""
        view = JobOfferView(
            id=event.offer_id,
            company=event.company_name,
            position=event.position,
            user_id=event.user_id,
            status="active",
            current_stage="resume_sent",
            progress_percentage=0.0,
            notes=[],
            is_active=True,
            is_rejected=False,
            is_offer_received=False,
            created_at=event.occurred_at(),
            updated_at=event.occurred_at()
        )
        self._read_repository.save(view)
    
    def _on_stage_changed(self, event: StageChangedEvent) -> None:
        """Смена этапа → обновление read модели"""
        view = self._read_repository.find_by_id(event.offer_id)
        if not view:
            return
        
        # Правильное получение значения этапа
        new_stage_value = event.new_stage.value if hasattr(event.new_stage, 'value') else event.new_stage
        view.current_stage = new_stage_value
        view.updated_at = event.occurred_at()
        
        # Пересчитываем прогресс
        from domain.value_objects.stage_type import StageTypeEnum
        stages = [e.value for e in StageTypeEnum]
        current_index = stages.index(new_stage_value) if new_stage_value in stages else 0
        total_stages = len(stages) - 1
        view.progress_percentage = (current_index / total_stages) * 100 if total_stages > 0 else 0
        
        self._read_repository.save(view)
    
    def _on_offer_rejected(self, event: OfferRejectedEvent) -> None:
        """Отклонение отклика → обновление read модели"""
        view = self._read_repository.find_by_id(event.offer_id)
        if not view:
            return
        
        view.status = "rejected"
        view.is_active = False
        view.is_rejected = True
        view.updated_at = event.occurred_at()
        
        self._read_repository.save(view)
    
    def _on_offer_received(self, event: OfferReceivedEvent) -> None:
        """Получение офера → обновление read модели"""
        view = self._read_repository.find_by_id(event.offer_id)
        if not view:
            return
        
        view.status = "offer_received"
        view.is_active = False
        view.is_offer_received = True
        view.progress_percentage = 100.0
        view.updated_at = event.occurred_at()
        
        self._read_repository.save(view)
    
    def _on_note_added(self, event: NoteAddedEvent) -> None:
        """Добавление заметки → обновление read модели"""
        view = self._read_repository.find_by_id(event.offer_id)
        if not view:
            return
        
        if not view.notes:
            view.notes = []
        view.notes.append(f"[{event.occurred_at().strftime('%Y-%m-%d %H:%M:%S')}] {event.note_content}")
        view.notes_count = len(view.notes)
        view.updated_at = event.occurred_at()
        
        self._read_repository.save(view)
