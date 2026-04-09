# application/command/add_note_command.py
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class AddNoteCommand:
    """
    Команда: добавить заметку к отклику
    
    Атрибуты:
        offer_id: ID отклика (формат OFFER-YYYY-NNNN)
        content: Текст заметки (1-1000 символов)
    """
    offer_id: str
    content: str
    
    def __post_init__(self):
        # Валидация offer_id
        if not self.offer_id or not self.offer_id.strip():
            raise ValueError("Offer ID cannot be empty")
        
        offer_id_stripped = self.offer_id.strip()
        if not re.match(r'OFFER-\d{4}-[A-Z0-9]{4,8}', offer_id_stripped):
            raise ValueError(f"Invalid Offer ID format: {self.offer_id}. Expected format: OFFER-YYYY-NNNN")
        
        # Валидация content
        if not self.content or not self.content.strip():
            raise ValueError("Note content cannot be empty")
        
        content_stripped = self.content.strip()
        if len(content_stripped) < 1:
            raise ValueError("Note too short (min 1 char)")
        if len(content_stripped) > 1000:
            raise ValueError(f"Note too long (max 1000 chars): {len(content_stripped)}")