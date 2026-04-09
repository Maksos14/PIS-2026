# tests/test_optimized_queries.py
import pytest
from datetime import datetime, timedelta

from cqrs.read_model.job_offer_view import JobOfferView
from cqrs.read_model.job_offer_read_repository import InMemoryJobOfferReadRepository


class TestOptimizedQueries:
    """Тесты оптимизированных запросов (in-memory версия)"""
    
    def setup_method(self):
        self.repo = InMemoryJobOfferReadRepository()
        
        now = datetime.now()
        
        # Создаем тестовые данные
        offers = [
            JobOfferView(
                id="OFFER-001", company="Google", position="Python Dev",
                user_id="USR-001", status="active", current_stage="tech_interview",
                progress_percentage=40.0, is_active=True, is_rejected=False,
                is_offer_received=False, created_at=now - timedelta(days=1)
            ),
            JobOfferView(
                id="OFFER-002", company="Microsoft", position="Java Dev",
                user_id="USR-001", status="active", current_stage="hr_screening",
                progress_percentage=20.0, is_active=True, is_rejected=False,
                is_offer_received=False, created_at=now - timedelta(days=2)
            ),
            JobOfferView(
                id="OFFER-003", company="Amazon", position="DevOps",
                user_id="USR-001", status="rejected", current_stage="final_interview",
                progress_percentage=80.0, is_active=False, is_rejected=True,
                is_offer_received=False, created_at=now - timedelta(days=3)
            ),
            JobOfferView(
                id="OFFER-004", company="Meta", position="Frontend",
                user_id="USR-002", status="offer_received", current_stage="offer",
                progress_percentage=100.0, is_active=False, is_rejected=False,
                is_offer_received=True, created_at=now - timedelta(days=4)
            ),
        ]
        
        for offer in offers:
            self.repo.save(offer)
    
    def test_get_user_statistics(self):
        """Тест получения статистики пользователя"""
        all_offers = self.repo.find_by_user_id("USR-001")
        
        assert len(all_offers) == 3
        active = len([o for o in all_offers if o.is_active])
        rejected = len([o for o in all_offers if o.is_rejected])
        
        assert active == 2
        assert rejected == 1
    
    def test_find_active_offers_optimized(self):
        """Тест поиска активных откликов"""
        active = self.repo.find_active_offers("USR-001")
        
        assert len(active) == 2
        companies = [a.company for a in active]
        assert "Google" in companies
        assert "Microsoft" in companies
    
    def test_search_offers(self):
        """Тест поиска откликов"""
        all_offers = self.repo.find_by_user_id("USR-001")
        
        results = [o for o in all_offers if "Google" in o.company]
        
        assert len(results) == 1
        assert results[0].company == "Google"
    
    def test_dashboard_stats(self):
        """Тест статистики для дашборда"""
        all_offers = self.repo.find_by_user_id("USR-001")
        active = self.repo.find_active_offers("USR-001")
        
        assert len(active) == 2
        assert len(all_offers) == 3