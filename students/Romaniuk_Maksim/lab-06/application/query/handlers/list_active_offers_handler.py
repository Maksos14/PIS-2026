import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from port.out.job_offer_repository import JobOfferRepository
from query.list_active_offers_query import ListActiveOffersQuery
from query.dto.job_offer_dto import JobOfferBriefDto


class ListActiveOffersHandler:
    """Обработчик запроса списка активных откликов"""
    
    def __init__(self, repository: JobOfferRepository):
        self._repository = repository
    
    def handle(self, query: ListActiveOffersQuery) -> dict:
        # 1. Извлечение данных через Repository
        all_offers = self._repository.find_by_user_id(query.user_id)
        
        # 2. Фильтрация активных откликов
        active_offers = [
            offer for offer in all_offers
            if offer.is_active and not offer.is_rejected and not offer.is_offer_received
        ]
        
        # 3. Пагинация
        total = len(active_offers)
        start = query.offset
        end = start + query.limit
        paginated_offers = active_offers[start:end]
        
        # 4. Преобразование в Read DTOs
        items = [
            JobOfferBriefDto(
                id=offer.id,
                company=str(offer.company),
                position=offer.position,
                status=offer.status.value,
                current_stage=offer.current_stage.value,
                progress_percentage=offer.progress_percentage
            )
            for offer in paginated_offers
        ]
        
        # 5. Возврат с метаинформацией
        return {
            "items": items,
            "total": total,
            "limit": query.limit,
            "offset": query.offset
        }
