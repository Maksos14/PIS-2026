from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import enum


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Project:
    """Агрегат: Проект/Группа поиска работы"""
    
    id: str
    name: str
    user_id: str
    description: str = ""
    status: str = ProjectStatus.DRAFT.value
    member_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    events: List[object] = field(default_factory=list)
    
    MIN_MEMBERS = 3
    
    @classmethod
    def create(cls, project_id: str, name: str, user_id: str, description: str = "") -> "Project":
        project = cls(
            id=project_id,
            name=name,
            user_id=user_id,
            description=description
        )
        from domain.events.project_events import ProjectCreatedEvent
        project.events.append(ProjectCreatedEvent(project_id, name, user_id))
        return project
    
    def add_member(self, member_id: str) -> None:
        if member_id in self.member_ids:
            raise ValueError(f"Member {member_id} already in project")
        self.member_ids.append(member_id)
        self.updated_at = datetime.now()
        
        if len(self.member_ids) >= self.MIN_MEMBERS and self.status == ProjectStatus.DRAFT.value:
            self.activate()
    
    def remove_member(self, member_id: str) -> None:
        if member_id not in self.member_ids:
            raise ValueError(f"Member {member_id} not in project")
        self.member_ids.remove(member_id)
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        if self.status != ProjectStatus.DRAFT.value:
            raise ValueError(f"Cannot activate project with status {self.status}")
        if len(self.member_ids) < self.MIN_MEMBERS:
            raise ValueError(f"Need at least {self.MIN_MEMBERS} members to activate")
        
        self.status = ProjectStatus.ACTIVE.value
        self.updated_at = datetime.now()
        
        from domain.events.project_events import ProjectActivatedEvent
        self.events.append(ProjectActivatedEvent(self.id, self.user_id, len(self.member_ids)))
    
    def pause(self) -> None:
        if self.status != ProjectStatus.ACTIVE.value:
            raise ValueError(f"Cannot pause project with status {self.status}")
        self.status = ProjectStatus.PAUSED.value
        self.updated_at = datetime.now()
    
    def complete(self) -> None:
        if self.status == ProjectStatus.COMPLETED.value:
            raise ValueError("Project already completed")
        self.status = ProjectStatus.COMPLETED.value
        self.updated_at = datetime.now()
