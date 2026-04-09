from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class ReminderTime:
    """Value Object: Время напоминания"""
    
    value: datetime
    MAX_DAYS_FORWARD = 365
    
    def __post_init__(self):
        if not isinstance(self.value, datetime):
            raise ValueError(f"Reminder time must be datetime, got {type(self.value)}")
        
        now = datetime.now()
        
        if self.value < now:
            raise ValueError(f"Reminder time cannot be in the past: {self.value}")
        
        max_future = now + timedelta(days=self.MAX_DAYS_FORWARD)
        if self.value > max_future:
            raise ValueError(f"Reminder time cannot be more than {self.MAX_DAYS_FORWARD} days in future")
    
    @property
    def year(self) -> int:
        return self.value.year
    
    @property
    def month(self) -> int:
        return self.value.month
    
    @property
    def day(self) -> int:
        return self.value.day
    
    @property
    def hour(self) -> int:
        return self.value.hour
    
    @property
    def minute(self) -> int:
        return self.value.minute
    
    @property
    def is_today(self) -> bool:
        now = datetime.now()
        return self.value.date() == now.date()
    
    @property
    def is_tomorrow(self) -> bool:
        tomorrow = datetime.now().date() + timedelta(days=1)
        return self.value.date() == tomorrow
    
    @property
    def days_from_now(self) -> int:
        now = datetime.now()
        delta = self.value - now
        return delta.days
    
    @property
    def hours_from_now(self) -> float:
        now = datetime.now()
        delta = self.value - now
        return delta.total_seconds() / 3600
    
    def is_urgent(self, minutes_threshold: int = 60) -> bool:
        now = datetime.now()
        delta = self.value - now
        return delta.total_seconds() <= minutes_threshold * 60
    
    def format_for_display(self, locale: str = "ru") -> str:
        if locale == "ru":
            return self.value.strftime("%d.%m.%Y %H:%M")
        return self.value.strftime("%Y-%m-%d %H:%M")
    
    def format_relative(self, locale: str = "ru") -> str:
        now = datetime.now()
        delta = self.value - now
        
        if delta.total_seconds() < 0:
            return "просрочено"
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"через {days} дн."
        elif hours > 0:
            return f"через {hours} ч."
        elif minutes > 0:
            return f"через {minutes} мин."
        else:
            return "скоро"
    
    def to_iso(self) -> str:
        return self.value.isoformat()
    
    @classmethod
    def from_iso(cls, iso_string: str) -> "ReminderTime":
        """Создать из ISO строки"""
        try:
            iso_string = iso_string.replace('T', ' ')
            dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M:%S")
            return cls(dt)
        except ValueError as e:
            raise ValueError(f"Invalid ISO datetime string: {iso_string}") from e
    
    @classmethod
    def now(cls) -> "ReminderTime":
        return cls(datetime.now())
    
    @classmethod
    def in_hours(cls, hours: int) -> "ReminderTime":
        if hours <= 0:
            raise ValueError("Hours must be positive")
        return cls(datetime.now() + timedelta(hours=hours))
    
    @classmethod
    def in_days(cls, days: int) -> "ReminderTime":
        if days <= 0:
            raise ValueError("Days must be positive")
        return cls(datetime.now() + timedelta(days=days))
    
    def __str__(self) -> str:
        return self.format_for_display()