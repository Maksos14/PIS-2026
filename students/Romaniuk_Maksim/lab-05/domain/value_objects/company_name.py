from dataclasses import dataclass
import re


@dataclass(frozen=True)
class CompanyName:
    """Value Object: Название компании"""
    
    value: str
    
    _VALID_PATTERN = re.compile(r'^[a-zA-Zа-яА-Я0-9\s\-.&]+$')
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Company name cannot be empty")
        
        stripped = self.value.strip()
        
        if len(stripped) < 2:
            raise ValueError(f"Company name too short (min 2 chars): {self.value}")
        
        if len(stripped) > 100:
            raise ValueError(f"Company name too long (max 100 chars): {self.value}")
        
        if not self._VALID_PATTERN.match(stripped):
            raise ValueError(f"Company name contains invalid characters: {self.value}")
        
        object.__setattr__(self, 'value', stripped)
    
    @property
    def short_name(self) -> str:
        if len(self.value) <= 20:
            return self.value
        return self.value[:17] + "..."
    
    @property
    def normalized(self) -> str:
        return self.value.lower().strip()
    
    def contains(self, text: str) -> bool:
        return text.lower() in self.normalized
    
    def __str__(self) -> str:
        return self.value