from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectCreatedEvent:
    project_id: str
    name: str
    user_id: str
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now()
    
    def event_name(self) -> str:
        return "project_created"


@dataclass
class ProjectActivatedEvent:
    project_id: str
    user_id: str
    members_count: int
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now()
    
    def event_name(self) -> str:
        return "project_activated"
