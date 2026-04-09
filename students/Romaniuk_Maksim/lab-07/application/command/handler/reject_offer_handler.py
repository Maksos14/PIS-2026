# application/command/handlers/reject_offer_handler.py
from typing import Optional

from port.out.job_offer_repository import JobOfferRepository
from port.out.notification_service import NotificationService
from command.reject_offer_command import RejectOfferCommand


class RejectOfferHandler:
    """
    Обработчик команды отклонения отклика
    
    Шаги обработки:
    1. Валидация входных данных
    2. Загрузка агрегата
    3. Проверка существования
    4. Проверка возможности отклонения
    5. Вызов метода mark_rejected()
    6. Сохранение изменений
    7. Публикация доменных событий
    """
    
    def __init__(self, repository: JobOfferRepository, notification_service: NotificationService):
        self._repository = repository
        self._notification_service = notification_service
    
    def handle(self, command: RejectOfferCommand) -> dict:
        # 1. Валидация входных данных
        if not command.offer_id or not command.offer_id.strip():
            raise ValueError("Offer ID cannot be empty")
        
        # 2. Загрузка агрегата
        job_offer = self._repository.find_by_id(command.offer_id)
        if not job_offer:
            raise ValueError(f"Job offer {command.offer_id} not found")
        
        # 3. Проверка возможности отклонения
        if job_offer.is_offer_received:
            raise ValueError(f"Cannot reject offer {command.offer_id} with received offer")
        
        if job_offer.is_rejected:
            raise ValueError(f"Offer {command.offer_id} already rejected")
        
        # 4. Сохраняем информацию до отклонения
        old_status = job_offer.status.value
        old_stage = job_offer.current_stage.value
        
        # 5. Вызов метода агрегата
        job_offer.mark_rejected(command.reason)
        
        # 6. Сохранение через репозиторий
        try:
            self._repository.save(job_offer)
        except Exception as e:
            raise RuntimeError(f"Failed to save job offer: {e}")
        
        # 7. Публикация доменных событий
        for event in job_offer.events:
            try:
                self._notification_service.publish(event)
            except Exception as e:
                print(f"Failed to publish event {event.event_name()}: {e}")
        
        # 8. Очистка событий
        job_offer.clear_events()
        
        # 9. Возврат результата
        return {
            "offer_id": command.offer_id,
            "old_status": old_status,
            "new_status": job_offer.status.value,
            "old_stage": old_stage,
            "reason": command.reason
        }