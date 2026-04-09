from application.port.on.create_job_offer_use_case import CreateJobOfferUseCase, CreateJobOfferCommand
from application.port.on.get_job_offer_use_case import GetJobOfferUseCase


class JobOfferController:
    """Входящий адаптер: REST API для работы с откликами"""
    
    def __init__(self, create_offer_use_case: CreateJobOfferUseCase, get_offer_use_case: GetJobOfferUseCase):
        self.create_offer_use_case = create_offer_use_case
        self.get_offer_use_case = get_offer_use_case
    
    def create_offer(self, request_data: dict) -> dict:
        """POST /api/offers"""
        company = request_data.get("company")
        position = request_data.get("position")
        user_id = request_data.get("user_id")
        
        if not company or not position or not user_id:
            return {"error": "Missing required fields: company, position, user_id"}, 400
        
        command = CreateJobOfferCommand(company, position, user_id)
        offer_id = self.create_offer_use_case.create_offer(command)
        
        return {"offer_id": offer_id, "status": "created"}
    
    def get_offer(self, offer_id: str) -> dict:
        """GET /api/offers/{offer_id}"""
        job_offer = self.get_offer_use_case.get_offer(offer_id)
        
        if job_offer is None:
            return {"error": f"Offer with id {offer_id} not found"}, 404
        
        return {
            "id": job_offer.id,
            "company": str(job_offer.company),
            "position": job_offer.position,
            "user_id": job_offer.user_id,
            "status": job_offer.status.value,
            "current_stage": job_offer.current_stage.value,
            "created_at": job_offer.created_at.isoformat()
        }
    
    def assign_group(self, offer_id: str, request_data: dict) -> dict:
        """POST /api/offers/{id}/assign-group"""
        group_id = request_data.get("group_id")
        if not group_id:
            return {"error": "group_id required"}, 400
        return {"offer_id": offer_id, "group_id": group_id, "status": "assigned"}
    
    def list_active_offers(self, user_id: str) -> dict:
        """GET /api/offers?user_id={user_id}"""
        return {"user_id": user_id, "offers": []}
