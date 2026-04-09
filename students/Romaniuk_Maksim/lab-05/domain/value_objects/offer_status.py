from dataclasses import dataclass
from enum import Enum


class OfferStatusEnum(str, Enum):
    ACTIVE = "active"
    REJECTED = "rejected"
    OFFER_RECEIVED = "offer_received"


@dataclass(frozen=True)
class OfferStatus:
    """Value Object: Статус отклика на вакансию"""
    
    value: OfferStatusEnum
    
    def __post_init__(self):
        if not isinstance(self.value, OfferStatusEnum):
            raise ValueError(f"Invalid offer status: {self.value}")
    
    @property
    def is_active(self) -> bool:
        return self.value == OfferStatusEnum.ACTIVE
    
    @property
    def is_rejected(self) -> bool:
        return self.value == OfferStatusEnum.REJECTED
    
    @property
    def is_offer_received(self) -> bool:
        return self.value == OfferStatusEnum.OFFER_RECEIVED
    
    def can_change_stage(self) -> bool:
        return self.value == OfferStatusEnum.ACTIVE
    
    def __str__(self) -> str:
        return self.value.value
    
    @classmethod
    def active(cls) -> "OfferStatus":
        return cls(OfferStatusEnum.ACTIVE)
    
    @classmethod
    def rejected(cls) -> "OfferStatus":
        return cls(OfferStatusEnum.REJECTED)
    
    @classmethod
    def offer_received(cls) -> "OfferStatus":
        return cls(OfferStatusEnum.OFFER_RECEIVED)