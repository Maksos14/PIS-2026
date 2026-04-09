
from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from domain.value_objects.stage_type import StageType
from infrastructure.config.database import DatabaseConfig
from infrastructure.adapter.out.postgres_job_offer_repository import PostgresJobOfferRepository
from infrastructure.adapter.on.job_offer_controller import JobOfferController


class MockCreateUseCase:
    def __init__(self, repo):
        self.repo = repo
    def create_offer(self, command):
        company = CompanyName(command.company)
        offer = JobOffer("OFFER-INT-001", company, command.position, command.user_id)
        self.repo.save(offer)
        return "OFFER-INT-001"

class MockGetUseCase:
    def __init__(self, repo):
        self.repo = repo
    def get_offer(self, offer_id):
        return self.repo.find_by_id(offer_id)


class TestIntegration:
    
    def setup_method(self):
        self.db = DatabaseConfig("sqlite:///./test_integration.db")
        self.db.create_tables()
        self.session = self.db.get_session()
        self.repo = PostgresJobOfferRepository(self.session)
        
        self.create_uc = MockCreateUseCase(self.repo)
        self.get_uc = MockGetUseCase(self.repo)
        self.controller = JobOfferController(self.create_uc, self.get_uc)
    
    def teardown_method(self):
        self.session.close()
        self.db.close()
    
    def test_full_flow(self):
        # 1. Создание отклика через контроллер
        request = {
            "company": "ООО Интеграция",
            "position": "Lead Developer",
            "user_id": "USR-INT-001"
        }
        result = self.controller.create_offer(request)
        assert result["offer_id"] == "OFFER-INT-001"
        
        # 2. Получение отклика через контроллер
        get_result = self.controller.get_offer("OFFER-INT-001")
        assert (get_result["company"]) == "ООО Интеграция"
        assert get_result["position"] == "Lead Developer"
        
        # 3. Проверка через репозиторий
        saved = self.repo.find_by_id("OFFER-INT-001")
        assert saved is not None
        assert str(saved.company) == "ООО Интеграция"
