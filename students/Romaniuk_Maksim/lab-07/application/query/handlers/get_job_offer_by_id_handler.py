import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from port.out.job_offer_repository import JobOfferRepository
from query.get_job_offer_by_id_query import GetJobOfferByIdQuery
from query.dto.job_offer_dto import JobOfferDto


class GetJobOfferByIdHandler:
    """Обработчик запроса получения отклика по ID"""
    
    def __init__(self, repository: JobOfferRepository):
        self._repository = repository
    
    def handle(self, query: GetJobOfferByIdQuery) -> JobOfferDto:
        # 1. Извлечение данных через Repository
        job_offer = self._repository.find_by_id(query.offer_id)
        
        # 2. Проверка существования
        if not job_offer:
            return None
        
        # 3. Преобразование в Read DTO
        return JobOfferDto(
            id=job_offer.id,
            company=str(job_offer.company),
            position=job_offer.position,
            user_id=job_offer.user_id,
            status=job_offer.status.value,
            current_stage=job_offer.current_stage.value,
            progress_percentage=job_offer.progress_percentage,
            notes=job_offer.notes,
            created_at=job_offer.created_at,
            updated_at=job_offer.updated_at
        )
