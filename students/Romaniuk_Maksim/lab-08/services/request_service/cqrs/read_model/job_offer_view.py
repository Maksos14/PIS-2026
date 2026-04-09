# cqrs/read_model/job_offer_view.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class JobOfferView:
    """
    Read Model: денормализованное представление отклика для быстрых запросов
    
    Содержит все данные, необходимые для отображения, без необходимости
    загружать весь агрегат и вычислять значения на лету.
    """
    
    id: str
    company: str
    position: str
    user_id: str
    status: str
    current_stage: str
    progress_percentage: float
    notes: List[str] = field(default_factory=list)
    created_at: datetime = None
    updated_at: datetime = None
    
    # Денормализованные поля для быстрых фильтров
    is_active: bool = True
    is_rejected: bool = False
    is_offer_received: bool = False
    
    # Статистические поля (для списков и дашбордов)
    stage_history: List[dict] = field(default_factory=list)
    notes_count: int = 0
    
    def __post_init__(self):
        self.notes_count = len(self.notes)
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для JSON ответа"""
        return {
            "id": self.id,
            "company": self.company,
            "position": self.position,
            "user_id": self.user_id,
            "status": self.status,
            "current_stage": self.current_stage,
            "progress_percentage": self.progress_percentage,
            "notes": self.notes,
            "notes_count": self.notes_count,
            "is_active": self.is_active,
            "is_rejected": self.is_rejected,
            "is_offer_received": self.is_offer_received,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class JobOfferSummaryView:
    """
    Read Model: краткое представление для списков
    """
    id: str
    company: str
    position: str
    current_stage: str
    progress_percentage: float
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "company": self.company,
            "position": self.position,
            "current_stage": self.current_stage,
            "progress_percentage": self.progress_percentage
        }
