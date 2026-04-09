import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.adapter.on.job_offer_controller import JobOfferController


class MockCreateUseCase:
    def create_offer(self, command):
        return "OFFER-MOCK-001"

class MockGetUseCase:
    def get_offer(self, offer_id):
        return None


class TestJobOfferController:
    
    def setup_method(self):
        self.mock_create = MockCreateUseCase()
        self.mock_get = MockGetUseCase()
        self.controller = JobOfferController(self.mock_create, self.mock_get)
    
    def test_create_offer_success(self):
        request = {
            "company": "ООО Тест",
            "position": "Python Dev",
            "user_id": "USR-001"
        }
        result = self.controller.create_offer(request)
        
        assert result["offer_id"] == "OFFER-MOCK-001"
        assert result["status"] == "created"
    
    def test_create_offer_missing_fields(self):
        request = {"company": "ООО Тест"}
        result = self.controller.create_offer(request)
        
        assert result[1] == 400
        assert "error" in result[0]
    
    def test_get_offer_not_found(self):
        result = self.controller.get_offer("NOT_EXISTS")
        
        assert result[1] == 404
        assert "error" in result[0]
