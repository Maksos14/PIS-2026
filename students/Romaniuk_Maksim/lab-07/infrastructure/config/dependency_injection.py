from infrastructure.adapter.out.in_memory_job_offer_repository import InMemoryJobOfferRepository
from infrastructure.adapter.out.console_notification_service import ConsoleNotificationService
from application.service.job_offer_service_impl import JobOfferServiceImpl
from cqrs.read_model.job_offer_read_repository import InMemoryJobOfferReadRepository
from cqrs.read_model.optimized_read_repository import OptimizedJobOfferReadRepository
from cqrs.projection.job_offer_projection import JobOfferProjection
from cqrs.projection.event_publisher import EventPublisher


class DependencyContainer:
    """Конфигурация DI: связывание портов и адаптеров"""
    
    def __init__(self, use_optimized: bool = False, db_session=None):
        # Write Model
        self.job_offer_repository = InMemoryJobOfferRepository()
        self.notification_service = ConsoleNotificationService()
        
        # Read Model (выбор реализации)
        if use_optimized and db_session:
            self.job_offer_read_repository = OptimizedJobOfferReadRepository(db_session)
        else:
            self.job_offer_read_repository = InMemoryJobOfferReadRepository()
        
        # Event Publisher и Projection
        self.event_publisher = EventPublisher()
        self.projection = JobOfferProjection(self.job_offer_read_repository)
        self.event_publisher.subscribe(self.projection.handle_event)
        
        # Application Service
        self.job_offer_service = JobOfferServiceImpl(
            repository=self.job_offer_repository,
            notification_service=self.notification_service,
            event_publisher=self.event_publisher
        )
    
    def get_job_offer_service(self):
        return self.job_offer_service
    
    def get_read_repository(self):
        return self.job_offer_read_repository
    
    def get_event_publisher(self):
        return self.event_publisher
    
    def get_projection(self):
        return self.projection
