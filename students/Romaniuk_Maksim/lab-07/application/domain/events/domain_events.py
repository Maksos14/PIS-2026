from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional


class DomainEvent(ABC):
    """Базовый класс для всех доменных событий"""
    
    @abstractmethod
    def occurred_at(self) -> datetime:
        pass
    
    @abstractmethod
    def event_name(self) -> str:
        pass


@dataclass(frozen=True)
class JobOfferCreatedEvent(DomainEvent):
    """Событие: создан новый отклик на вакансию"""
    offer_id: str
    company_name: str
    position: str
    user_id: str
    _occurred_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self._occurred_at is None:
            object.__setattr__(self, '_occurred_at', datetime.now())
    
    def occurred_at(self) -> datetime:
        return self._occurred_at
    
    def event_name(self) -> str:
        return "job_offer_created"


@dataclass(frozen=True)
class StageChangedEvent(DomainEvent):
    """Событие: этап отбора изменён"""
    offer_id: str
    old_stage: 'StageType'
    new_stage: 'StageType'
    note: Optional[str] = None
    _occurred_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self._occurred_at is None:
            object.__setattr__(self, '_occurred_at', datetime.now())
    
    def occurred_at(self) -> datetime:
        return self._occurred_at
    
    def event_name(self) -> str:
        return "stage_changed"


@dataclass(frozen=True)
class OfferRejectedEvent(DomainEvent):
    """Событие: отклик отклонён"""
    offer_id: str
    reason: Optional[str] = None
    _occurred_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self._occurred_at is None:
            object.__setattr__(self, '_occurred_at', datetime.now())
    
    def occurred_at(self) -> datetime:
        return self._occurred_at
    
    def event_name(self) -> str:
        return "offer_rejected"


@dataclass(frozen=True)
class OfferReceivedEvent(DomainEvent):
    """Событие: получен офер"""
    offer_id: str
    company_name: str
    position: str
    _occurred_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self._occurred_at is None:
            object.__setattr__(self, '_occurred_at', datetime.now())
    
    def occurred_at(self) -> datetime:
        return self._occurred_at
    
    def event_name(self) -> str:
        return "offer_received"


@dataclass(frozen=True)
class NoteAddedEvent(DomainEvent):
    """Событие: добавлена заметка"""
    offer_id: str
    note_content: str
    _occurred_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self._occurred_at is None:
            object.__setattr__(self, '_occurred_at', datetime.now())
    
    def occurred_at(self) -> datetime:
        return self._occurred_at
    
    def event_name(self) -> str:
        return "note_added"