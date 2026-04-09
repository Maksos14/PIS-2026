from dataclasses import dataclass
from typing import List


@dataclass
class StageDto:
    """DTO для информации об этапе отбора"""
    name: str
    order: int
    is_current: bool
    is_completed: bool


@dataclass
class StagesProgressDto:
    """DTO для прогресса по этапам"""
    current_stage: str
    total_stages: int
    completed_stages: int
    progress_percentage: float
    stages: List[StageDto]