# application/command/handlers/add_note_handler.py
from port.out.job_offer_repository import JobOfferRepository
from port.out.notification_service import NotificationService
from command.add_note_command import AddNoteCommand


class AddNoteHandler:
    """
    Обработчик команды добавления заметки к отклику
    
    Шаги обработки:
    1. Валидация входных данных
    2. Загрузка агрегата
    3. Проверка существования
    4. Проверка возможности добавления заметки
    5. Вызов метода add_note()
    6. Сохранение изменений
    7. Публикация доменных событий
    """
    
    def __init__(self, repository: JobOfferRepository, notification_service: NotificationService):
        self._repository = repository
        self._notification_service = notification_service
    
    def handle(self, command: AddNoteCommand) -> dict:
        # 1. Валидация входных данных
        if not command.offer_id or not command.offer_id.strip():
            raise ValueError("Offer ID cannot be empty")
        if not command.content or not command.content.strip():
            raise ValueError("Note content cannot be empty")
        
        # 2. Загрузка агрегата
        job_offer = self._repository.find_by_id(command.offer_id)
        if not job_offer:
            raise ValueError(f"Job offer {command.offer_id} not found")
        
        # 3. Проверка возможности добавления заметки
        if job_offer.is_rejected:
            raise ValueError(f"Cannot add note to rejected offer {command.offer_id}")
        
        if job_offer.is_offer_received:
            raise ValueError(f"Cannot add note to completed offer {command.offer_id}")
        
        # 4. Сохраняем количество заметок до добавления
        old_notes_count = len(job_offer.notes)
        
        # 5. Вызов метода агрегата
        job_offer.add_note(command.content)
        
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
            "note_added": command.content,
            "total_notes_count": len(job_offer.notes),
            "notes_added_count": len(job_offer.notes) - old_notes_count
        }