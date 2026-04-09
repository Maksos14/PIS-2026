# cqrs/projection/event_publisher.py
from typing import List, Callable
from domain.events.domain_events import DomainEvent


class EventPublisher:
    """Простой Event Publisher для публикации доменных событий"""
    
    def __init__(self):
        self._handlers: List[Callable] = []
    
    def subscribe(self, handler: Callable) -> None:
        """Подписка на события"""
        self._handlers.append(handler)
    
    def publish(self, events: List[DomainEvent]) -> None:
        """Публикация списка событий"""
        for event in events:
            for handler in self._handlers:
                handler(event)
