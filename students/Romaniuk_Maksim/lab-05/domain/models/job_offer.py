from datetime import datetime
from typing import List, Optional
import re

from domain.value_objects.offer_status import OfferStatus
from domain.value_objects.stage_type import StageType, StageTypeEnum, STAGE_ORDER
from domain.value_objects.company_name import CompanyName
from domain.events.domain_events import (
    DomainEvent,
    JobOfferCreatedEvent,
    StageChangedEvent,
    OfferRejectedEvent,
    OfferReceivedEvent,
    NoteAddedEvent
)


class JobOffer:
    """Aggregate Root: Отклик на вакансию"""
    
    ID_PATTERN = re.compile(r'OFFER-\d{4}-\d{4}')
    
    def __init__(
        self,
        offer_id: str,
        company: CompanyName,
        position: str,
        user_id: str
    ):
        
        if not position or not position.strip():
            raise ValueError("Position cannot be empty")
        
        if len(position) > 200:
            raise ValueError("Position too long (max 200 chars)")
        
        if not user_id:
            raise ValueError("User ID cannot be empty")
        
        self._id = offer_id
        self._company = company
        self._position = position.strip()
        self._user_id = user_id
        self._status = OfferStatus.active()
        self._current_stage = StageType.resume_sent()
        self._notes: List[str] = []
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._events: List[DomainEvent] = []
        
        self._register_event(JobOfferCreatedEvent(
            offer_id=self._id,
            company_name=str(self._company),
            position=self._position,
            user_id=self._user_id
        ))
    
    def change_stage(self, new_stage: StageType, note: Optional[str] = None) -> None:
        self._ensure_editable()
        
        if not self._current_stage.can_transition_to(new_stage):
            raise ValueError(
                f"Cannot transition from {self._current_stage} to {new_stage}. "
                f"Only next stage is allowed."
            )
        
        old_stage = self._current_stage
        self._current_stage = new_stage
        self._updated_at = datetime.now()
        
        if note:
            self._add_note_internal(f"[{old_stage} → {new_stage}] {note}")
        
        self._register_event(StageChangedEvent(
            offer_id=self._id,
            old_stage=old_stage,
            new_stage=new_stage,
            note=note
        ))
        
        if new_stage.value == StageTypeEnum.OFFER:
            self._status = OfferStatus.offer_received()
            self._register_event(OfferReceivedEvent(
                offer_id=self._id,
                company_name=str(self._company),
                position=self._position
            ))
    
    def mark_rejected(self, reason: Optional[str] = None) -> None:
        if self._status.is_offer_received:
            raise ValueError(f"Cannot reject offer {self._id} with received offer")
        
        if self._status.is_rejected:
            raise ValueError(f"Offer {self._id} already rejected")
        
        self._status = OfferStatus.rejected()
        self._updated_at = datetime.now()
        
        if reason:
            self._add_note_internal(f"[REJECTED] {reason}")
        
        self._register_event(OfferRejectedEvent(
            offer_id=self._id,
            reason=reason
        ))
    
    def add_note(self, content: str) -> None:
        self._ensure_editable()
        
        if not content or not content.strip():
            raise ValueError("Note cannot be empty")
        
        if len(content) > 1000:
            raise ValueError("Note too long (max 1000 chars)")
        
        self._add_note_internal(content)
        
        self._register_event(NoteAddedEvent(
            offer_id=self._id,
            note_content=content
        ))
    
    def _add_note_internal(self, content: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._notes.append(f"[{timestamp}] {content}")
        self._updated_at = datetime.now()
    
    def _ensure_editable(self) -> None:
        if self._status.is_rejected:
            raise ValueError(f"Cannot modify rejected offer {self._id}")
        
        if self._status.is_offer_received:
            raise ValueError(f"Cannot modify completed offer {self._id}")
    
    def _register_event(self, event: DomainEvent) -> None:
        self._events.append(event)
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def company(self) -> CompanyName:
        return self._company
    
    @property
    def position(self) -> str:
        return self._position
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def status(self) -> OfferStatus:
        return self._status
    
    @property
    def current_stage(self) -> StageType:
        return self._current_stage
    
    @property
    def notes(self) -> List[str]:
        return self._notes.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def events(self) -> List[DomainEvent]:
        return self._events.copy()
    
    @property
    def is_active(self) -> bool:
        return self._status.is_active
    
    @property
    def is_rejected(self) -> bool:
        return self._status.is_rejected
    
    @property
    def is_offer_received(self) -> bool:
        return self._status.is_offer_received
    
    @property
    def progress_percentage(self) -> float:
        current_index = self._current_stage.order
        total_stages = len(STAGE_ORDER) - 1
        if total_stages == 0:
            return 0.0
        return (current_index / total_stages) * 100
    
    def clear_events(self) -> None:
        self._events.clear()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, JobOffer):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"JobOffer(id={self._id}, company={self._company}, position={self._position}, stage={self._current_stage})"
