# event_bus/simple_event_bus.py
from typing import List, Callable

class SimpleEventBus:
    """Простой Event Bus"""
    
    def __init__(self):
        self._handlers = []
    
    def subscribe(self, handler: Callable):
        self._handlers.append(handler)
    
    def publish(self, event: dict):
        for handler in self._handlers:
            handler(event)


# Глобальный экземпляр
event_bus = SimpleEventBus()
