from dataclasses import dataclass
from typing import Optional
from domain.value_objects.stage_type import StageTypeEnum


@dataclass(frozen=True)
class ListOffersByStageQuery:
    """Запрос: список откликов по этапу отбора"""
    user_id: str
    stage: StageTypeEnum
    limit: Optional[int] = 20
    offset: Optional[int] = 0
    
    def __post_init__(self):
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if not self.stage:
            raise ValueError("Stage cannot be empty")