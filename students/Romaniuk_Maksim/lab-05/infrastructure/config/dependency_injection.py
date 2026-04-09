from infrastructure.adapter.out.on_memory_job_offer_repository import InMemoryJobOfferRepository
from infrastructure.adapter.out.console_notification_service import ConsoleNotificationService
from application.service.job_offer_service import JobOfferService


class DependencyContainer:
    """Конфигурация DI: связывание портов и адаптеров"""
    
    def __init__(self):
        # Создаём исходящие адаптеры (infrastructure layer)
        self.job_offer_repository = InMemoryJobOfferRepository()
        self.notification_service = ConsoleNotificationService()
        
        # Создаём application service с инжекцией зависимостей
        self.job_offer_service = JobOfferService(
            repository=self.job_offer_repository,
            notification_service=self.notification_service
        )
    
    def get_job_offer_service(self):
        """Возвращает сервис для работы с откликами"""
        return self.job_offer_service
    
    def get_repository(self):
        """Возвращает репозиторий (для тестов/отладки)"""
        return self.job_offer_repository
