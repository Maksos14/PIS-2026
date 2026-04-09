# application/command/reject_offer_command.py
from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class RejectOfferCommand:
    """
    Команда: отклонить отклик
    
    Атрибуты:
        offer_id: ID отклика (формат OFFER-YYYY-NNNN)
        reason: Причина отклонения (опционально, макс 500 символов)
    """
    offer_id: str
    reason: Optional[str] = None
    
    def __post_init__(self):
        # Валидация offer_id
        if not self.offer_id or not self.offer_id.strip():
            raise ValueError("Offer ID cannot be empty")
        
        offer_id_stripped = self.offer_id.strip()
        if not re.match(r'OFFER-\d{4}-[A-Z0-9]{4,8}', offer_id_stripped):
            raise ValueError(f"Invalid Offer ID format: {self.offer_id}. Expected format: OFFER-YYYY-NNNN")
        
        # Валидация reason
        if self.reason is not None:
            if len(self.reason) > 500:
                raise ValueError(f"Reason too long (max 500 chars): {len(self.reason)}")