# application/command/create_job_offer_command.py
from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class CreateJobOfferCommand:
    """
    Команда: создать новый отклик на вакансию
    
    Атрибуты:
        company: Название компании (2-100 символов, только допустимые символы)
        position: Должность (1-200 символов)
        user_id: ID пользователя (формат USR-XXXX)
        salary_expectation: Ожидаемая зарплата (опционально, положительное число)
    """
    company: str
    position: str
    user_id: str
    salary_expectation: Optional[int] = None
    
    def __post_init__(self):
        # Валидация company
        if not self.company or not self.company.strip():
            raise ValueError("Company name cannot be empty")
        
        company_stripped = self.company.strip()
        if len(company_stripped) < 2:
            raise ValueError(f"Company name too short (min 2 chars): {self.company}")
        if len(company_stripped) > 100:
            raise ValueError(f"Company name too long (max 100 chars): {self.company}")
        
        # Валидация position
        if not self.position or not self.position.strip():
            raise ValueError("Position cannot be empty")
        
        position_stripped = self.position.strip()
        if len(position_stripped) < 1:
            raise ValueError("Position too short (min 1 char)")
        if len(position_stripped) > 200:
            raise ValueError(f"Position too long (max 200 chars): {self.position}")
        
        # Валидация user_id
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        user_id_stripped = self.user_id.strip()
        if not re.match(r'USR-[A-Z0-9]{4,8}', user_id_stripped):
            raise ValueError(f"Invalid User ID format: {self.user_id}. Expected format: USR-XXXX")
        
        # Валидация salary_expectation
        if self.salary_expectation is not None:
            if self.salary_expectation <= 0:
                raise ValueError(f"Salary expectation must be positive: {self.salary_expectation}")
            if self.salary_expectation > 1_000_000:
                raise ValueError(f"Salary expectation too high (max 1,000,000): {self.salary_expectation}")