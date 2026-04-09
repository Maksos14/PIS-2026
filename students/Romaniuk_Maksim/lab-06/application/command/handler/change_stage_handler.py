# application/command/handlers/change_stage_handler.py
from typing import Optional

from domain.value_objects.stage_type import StageType, StageTypeEnum
from port.out.job_offer_repository import JobOfferRepository
from port.out.notification_service import NotificationService
from command.change_stage_command import ChangeStageCommand


class ChangeStageHandler:
    """
    Обработчик команды смены этапа отбора
    
    Шаги обработки:
    1. Валидация входных данных
    2. Загрузка агрегата из репозитория
    3. Проверка существования агрегата
    4. Проверка возможности смены этапа (application-level)
    5. Вызов метода агрегата change_stage()
    6. Сохранение изменений
    7. Публикация доменных событий
    """
    
    def __init__(self, repository: JobOfferRepository, notification_service: NotificationService):
        self._repository = repository
        self._notification_service = notification_service
    
    def handle(self, command: ChangeStageCommand) -> dict:
        # 1. Валидация входных данных
        if not command.offer_id or not command.offer_id.strip():
            raise ValueError("Offer ID cannot be empty")
        if not command.new_stage:
            raise ValueError("New stage cannot be empty")
        
        # 2. Загрузка агрегата
        job_offer = self._repository.find_by_id(command.offer_id)
        if not job_offer:
            raise ValueError(f"Job offer {command.offer_id} not found")
        
        # 3. Проверка возможности смены этапа (application-level validation)
        if job_offer.is_rejected:
            raise ValueError(f"Cannot change stage of rejected offer {command.offer_id}")
        
        if job_offer.is_offer_received:
            raise ValueError(f"Cannot change stage of completed offer {command.offer_id}")
        
        # 4. Сохраняем старый этап для возврата в ответе
        old_stage = job_offer.current_stage.value
        
        # 5. Вызов метода агрегата
        new_stage = StageType(command.new_stage)
        
        # Проверка перехода (дополнительная защита)
        if not job_offer.current_stage.can_transition_to(new_stage):
            raise ValueError(
                f"Cannot transition from {job_offer.current_stage.value} to {new_stage.value}. "
                f"Only next stage is allowed."
            )
        
        job_offer.change_stage(new_stage, command.note)
        
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
            "old_stage": old_stage,
            "new_stage": command.new_stage.value,
            "is_offer_received": job_offer.is_offer_received
        }