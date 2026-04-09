from dataclasses import dataclass


@dataclass(frozen=True)
class GetJobOfferByIdQuery:
    """Запрос: получить отклик по ID"""
    offer_id: str
    
    def __post_init__(self):
        if not self.offer_id or not self.offer_id.strip():
            raise ValueError("Offer ID cannot be empty")