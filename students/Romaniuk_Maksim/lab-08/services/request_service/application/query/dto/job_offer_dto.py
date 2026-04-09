from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class JobOfferDto:
    """DTO для чтения информации об отклике"""
    id: str
    company: str
    position: str
    user_id: str
    status: str
    current_stage: str
    progress_percentage: float
    notes: List[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class JobOfferBriefDto:
    """DTO для краткой информации об отклике (для списков)"""
    id: str
    company: str
    position: str
    status: str
    current_stage: str
    progress_percentage: float