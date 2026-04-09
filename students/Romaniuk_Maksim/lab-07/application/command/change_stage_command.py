# application/command/change_stage_command.py
from dataclasses import dataclass
from typing import Optional
import re
from enum import Enum


class StageTypeEnum(str, Enum):
    RESUME_SENT = "resume_sent"
    HR_SCREENING = "hr_screening"
    TECH_INTERVIEW = "tech_interview"
    TEST_TASK = "test_task"
    FINAL_INTERVIEW = "final_interview"
    OFFER = "offer"


@dataclass(frozen=True)
class ChangeStageCommand:
    """
    Команда: изменить этап отбора по вакансии
    
    Атрибуты:
        offer_id: ID отклика (формат OFFER-YYYY-NNNN)
        new_stage: Новый этап (из StageTypeEnum)
        note: Опциональная заметка о переходе (макс 500 символов)
    """
    offer_id: str
    new_stage: StageTypeEnum
    note: Optional[str] = None
    
    def __post_init__(self):
        # Валидация offer_id
        if not self.offer_id or not self.offer_id.strip():
            raise ValueError("Offer ID cannot be empty")
        
        offer_id_stripped = self.offer_id.strip()
        if not re.match(r'OFFER-\d{4}-[A-Z0-9]{4,8}', offer_id_stripped):
            raise ValueError(f"Invalid Offer ID format: {self.offer_id}. Expected format: OFFER-YYYY-NNNN")
        
        # Валидация new_stage
        if not self.new_stage:
            raise ValueError("New stage cannot be empty")
        
        valid_stages = ["resume_sent", "hr_screening", "tech_interview", "test_task", "final_interview", "offer"]
        if self.new_stage.value not in valid_stages:
            raise ValueError(f"Invalid stage: {self.new_stage}. Allowed: {valid_stages}")
        
        # Валидация note
        if self.note is not None:
            if len(self.note) > 500:
                raise ValueError(f"Note too long (max 500 chars): {len(self.note)}")