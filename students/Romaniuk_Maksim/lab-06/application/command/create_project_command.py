# application/command/create_project_command.py
from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class CreateProjectCommand:
    """
    Команда: создать проект/кампанию поиска работы
    
    Атрибуты:
        name: Название проекта (1-100 символов)
        user_id: ID владельца (формат USR-XXXX)
        description: Описание проекта (опционально, макс 500 символов)
    """
    name: str
    user_id: str
    description: Optional[str] = None
    
    def __post_init__(self):
        # Валидация name
        if not self.name or not self.name.strip():
            raise ValueError("Project name cannot be empty")
        
        name_stripped = self.name.strip()
        if len(name_stripped) < 1:
            raise ValueError("Project name too short (min 1 char)")
        if len(name_stripped) > 100:
            raise ValueError(f"Project name too long (max 100 chars): {len(name_stripped)}")
        
        # Валидация user_id
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        user_id_stripped = self.user_id.strip()
        if not re.match(r'USR-[A-Z0-9]{4,8}', user_id_stripped):
            raise ValueError(f"Invalid User ID format: {self.user_id}. Expected format: USR-XXXX")
        
        # Валидация description
        if self.description is not None:
            if len(self.description) > 500:
                raise ValueError(f"Description too long (max 500 chars): {len(self.description)}")