import pytest
from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from infrastructure.config.database import DatabaseConfig
from infrastructure.adapter.out.postgres_job_offer_repository import PostgresJobOfferRepository
from domain.value_objects.stage_type import StageType

class TestPostgresJobOfferRepository:
    
    def setup_method(self):
        # Используем SQLite для тестов
        self.db = DatabaseConfig("sqlite:///./test.db")
        self.db.create_tables()
        self.session = self.db.get_session()
        self.repo = PostgresJobOfferRepository(self.session)
        
        self.company = CompanyName("ООО Тест")
        self.offer = JobOffer("OFFER-TEST-001", self.company, "Python Dev", "USR-TEST-001")
    
    def teardown_method(self):
        self.session.close()
        self.db.close()
    
    def test_save_and_find_by_id(self):
        self.repo.save(self.offer)
        found = self.repo.find_by_id("OFFER-TEST-001")
        
        assert found is not None
        assert found.id == "OFFER-TEST-001"
        assert str(found.company) == "ООО Тест"
    
    def test_find_by_user_id(self):
        self.repo.save(self.offer)
        offers = self.repo.find_by_user_id("USR-TEST-001")
        
        assert len(offers) == 1
        assert offers[0].id == "OFFER-TEST-001"
    
    def test_find_active_offers(self):
        self.repo.save(self.offer)
        active = self.repo.find_active_offers("USR-TEST-001")
        
        assert len(active) == 1
    
    def test_update_offer(self):
        self.repo.save(self.offer)
        found = self.repo.find_by_id("OFFER-TEST-001")
        found.change_stage(StageType.hr_screening())
        self.repo.save(found)
        
        updated = self.repo.find_by_id("OFFER-TEST-001")
        assert updated.current_stage.value == "hr_screening"
