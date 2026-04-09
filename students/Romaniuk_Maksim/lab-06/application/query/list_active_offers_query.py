from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ListActiveOffersQuery:
    """Запрос: список активных откликов пользователя"""
    user_id: str
    limit: Optional[int] = 20
    offset: Optional[int] = 0
    
    def __post_init__(self):
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if self.limit and self.limit <= 0:
            raise ValueError("Limit must be positive")
        if self.offset and self.offset < 0:
            raise ValueError("Offset cannot be negative")