from datetime import datetime
from enum import Enum

class OfferStatus(str, Enum):
    """Статус отклика"""
    ACTIVE = "active"
    REJECTED = "rejected"
    OFFER_RECEIVED = "offer_received"

class StageType(str, Enum):
    """Типы этапов отбора"""
    RESUME_SENT = "resume_sent"
    INTERVIEW = "interview"
    TEST_TASK = "test_task"
    OFFER = "offer"

class JobOffer:
    """Доменная модель: Отклик на вакансию"""
    
    def __init__(self, offer_id: str, company: str, position: str, user_id: str):
        self.id = offer_id
        self.company = company
        self.position = position
        self.user_id = user_id
        self.status = OfferStatus.ACTIVE
        self.current_stage = StageType.RESUME_SENT
        self.created_at = datetime.now()
    
    def change_stage(self, new_stage: StageType):
        """Перевести отклик на новый этап"""
        self.current_stage = new_stage
        # Полную бизнес-логику (проверки, события) добавим в Lab #3
    
    def mark_rejected(self):
        """Отметить отклик как отклонённый"""
        self.status = OfferStatus.REJECTED
        # Полную бизнес-логику добавим в Lab #3
