from datetime import datetime
import uuid
from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from infrastructure.adapter.out.on_memory_job_offer_repository import InMemoryJobOfferRepository


class TestInMemoryJobOfferRepository:
    
    def setup_method(self):
        self.repo = InMemoryJobOfferRepository()
        self.company = CompanyName("ООО Тест")
        
        # Правильный формат ID: OFFER-2024-0001
        year = datetime.now().year
        unique_part = uuid.uuid4().hex[:4].upper()
        offer_id = f"OFFER-{year}-{unique_part}"
        
        self.offer = JobOffer(offer_id, self.company, "Python Dev", "USR-001")
        self.test_id = offer_id
    
    def test_save_and_find_by_id(self):
        self.repo.save(self.offer)
        found = self.repo.find_by_id(self.test_id)
        
        assert found is not None
        assert found.id == self.test_id
        assert str(found.company) == "ООО Тест"
    
    def test_find_by_user_id(self):
        self.repo.save(self.offer)
        offers = self.repo.find_by_user_id("USR-001")
        
        assert len(offers) == 1
        assert offers[0].id == self.test_id
    
    def test_find_active_offers(self):
        self.repo.save(self.offer)
        active = self.repo.find_active_offers("USR-001")
        
        assert len(active) == 1
        assert active[0].is_active is True
    
    def test_delete_offer(self):
        self.repo.save(self.offer)
        result = self.repo.delete(self.test_id)
        
        assert result is True
        assert self.repo.find_by_id(self.test_id) is None
    
    def test_find_not_found(self):
        found = self.repo.find_by_id("NOT_EXISTS")
        assert found is None