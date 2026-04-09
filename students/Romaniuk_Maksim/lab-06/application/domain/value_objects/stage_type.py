from dataclasses import dataclass
from enum import Enum


class StageTypeEnum(str, Enum):
    RESUME_SENT = "resume_sent"
    HR_SCREENING = "hr_screening"
    TECH_INTERVIEW = "tech_interview"
    TEST_TASK = "test_task"
    FINAL_INTERVIEW = "final_interview"
    OFFER = "offer"


STAGE_ORDER = [
    StageTypeEnum.RESUME_SENT,
    StageTypeEnum.HR_SCREENING,
    StageTypeEnum.TECH_INTERVIEW,
    StageTypeEnum.TEST_TASK,
    StageTypeEnum.FINAL_INTERVIEW,
    StageTypeEnum.OFFER
]


@dataclass(frozen=True)
class StageType:
    """Value Object: Тип этапа отбора"""
    
    value: StageTypeEnum
    
    def __post_init__(self):
        if not isinstance(self.value, StageTypeEnum):
            raise ValueError(f"Invalid stage type: {self.value}")
    
    @property
    def order(self) -> int:
        return STAGE_ORDER.index(self.value)
    
    @property
    def is_first(self) -> bool:
        return self.value == StageTypeEnum.RESUME_SENT
    
    @property
    def is_last(self) -> bool:
        return self.value == StageTypeEnum.OFFER
    
    @property
    def requires_decision(self) -> bool:
        return self.value in [StageTypeEnum.TEST_TASK, StageTypeEnum.FINAL_INTERVIEW]
    
    def can_transition_to(self, other: "StageType") -> bool:
        current_index = self.order
        new_index = other.order
        return new_index == current_index + 1
    
    def __str__(self) -> str:
        return self.value.value
    
    @classmethod
    def resume_sent(cls) -> "StageType":
        return cls(StageTypeEnum.RESUME_SENT)
    
    @classmethod
    def hr_screening(cls) -> "StageType":
        return cls(StageTypeEnum.HR_SCREENING)
    
    @classmethod
    def tech_interview(cls) -> "StageType":
        return cls(StageTypeEnum.TECH_INTERVIEW)
    
    @classmethod
    def test_task(cls) -> "StageType":
        return cls(StageTypeEnum.TEST_TASK)
    
    @classmethod
    def final_interview(cls) -> "StageType":
        return cls(StageTypeEnum.FINAL_INTERVIEW)
    
    @classmethod
    def offer(cls) -> "StageType":
        return cls(StageTypeEnum.OFFER)