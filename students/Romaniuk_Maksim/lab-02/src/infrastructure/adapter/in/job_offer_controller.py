from application.port.in.create_job_offer_use_case import CreateJobOfferUseCase, CreateJobOfferCommand
from application.port.in.get_job_offer_use_case import GetJobOfferUseCase


class JobOfferController:
    """Входящий адаптер: REST API для работы с откликами"""
    
    def __init__(self, create_offer_use_case: CreateJobOfferUseCase, get_offer_use_case: GetJobOfferUseCase):
        self.create_offer_use_case = create_offer_use_case
        self.get_offer_use_case = get_offer_use_case
    
    def create_offer(self, request_data: dict) -> dict:
        """
        Создание нового отклика на вакансию
        POST /api/offers
        
        :param request_data: {
            "company": "ООО Ромашка",
            "position": "Python Developer",
            "user_id": "user_123"
        }
        :return: {"offer_id": "offer_456", "status": "created"}
        """
        # 1. Извлекаем данные из запроса
        company = request_data.get("company")
        position = request_data.get("position")
        user_id = request_data.get("user_id")
        
        # 2. Валидация входных данных
        if not company or not position or not user_id:
            return {"error": "Missing required fields: company, position, user_id"}, 400
        
        # 3. Создаём команду для use case
        command = CreateJobOfferCommand(company, position, user_id)
        
        # 4. Вызываем use case
        offer_id = self.create_offer_use_case.create_offer(command)
        
        # 5. Возвращаем ответ
        return {"offer_id": offer_id, "status": "created"}
    
    def get_offer(self, offer_id: str) -> dict:
        """
        Получение отклика по ID
        GET /api/offers/{offer_id}
        
        :param offer_id: ID отклика
        :return: dict с данными отклика или ошибка
        """
        # 1. Вызываем use case
        job_offer = self.get_offer_use_case.get_offer(offer_id)
        
        # 2. Проверяем результат
        if job_offer is None:
            return {"error": f"Offer with id {offer_id} not found"}, 404
        
        # 3. Форматируем ответ
        return {
            "id": job_offer.id,
            "company": job_offer.company,
            "position": job_offer.position,
            "user_id": job_offer.user_id,
            "status": job_offer.status.value,
            "current_stage": job_offer.current_stage.value,
            "created_at": job_offer.created_at.isoformat()
        }
