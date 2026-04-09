import pytest
from datetime import datetime
import uuid

from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from domain.value_objects.stage_type import StageType
from infrastructure.config.database import DatabaseConfig
from infrastructure.adapter.out.postgres_job_offer_repository import PostgresJobOfferRepository
from infrastructure.models.job_offer_orm import Base, JobOfferORM


@pytest.fixture
def db_session():
    """Фикстура для создания тестовой БД SQLite"""
    import tempfile
    import os
    
    # Создаем временную БД
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    db_config = DatabaseConfig(f"sqlite:///{db_path}")
    db_config.create_tables()
    
    session = db_config.get_session()
    
    yield session
    
    session.close()
    db_config.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def repository(db_session):
    """Фикстура репозитория"""
    return PostgresJobOfferRepository(db_session)


@pytest.fixture
def sample_offer():
    """Фикстура тестового отклика"""
    company = CompanyName("ООО Тест")
    return JobOffer(
        offer_id=f"OFFER-2024-{uuid.uuid4().hex[:4].upper()}",
        company=company,
        position="Python Developer",
        user_id="USR-INT-001"
    )


class TestPostgresJobOfferRepository:
    
    def test_save_and_find_by_id(self, repository, sample_offer):
        """Тест: сохранение и поиск отклика по ID"""
        # Act
        repository.save(sample_offer)
        found = repository.find_by_id(sample_offer.id)
        
        # Assert
        assert found is not None
        assert found.id == sample_offer.id
        assert str(found.company) == str(sample_offer.company)
        assert found.position == sample_offer.position
        assert found.user_id == sample_offer.user_id
    
    def test_find_by_user_id(self, repository, sample_offer):
        """Тест: поиск всех откликов пользователя"""
        # Arrange
        repository.save(sample_offer)
        
        # Act
        offers = repository.find_by_user_id("USR-INT-001")
        
        # Assert
        assert len(offers) == 1
        assert offers[0].id == sample_offer.id
    
    def test_find_active_offers(self, repository, sample_offer):
        """Тест: поиск только активных откликов"""
        # Arrange
        repository.save(sample_offer)
        
        # Act
        active = repository.find_active_offers("USR-INT-001")
        
        # Assert
        assert len(active) == 1
        assert active[0].is_active is True
    
    def test_find_active_offers_excludes_rejected(self, repository):
        """Тест: отклонённые отклики не попадают в активные"""
        # Arrange
        company = CompanyName("ООО Тест")
        offer = JobOffer("OFFER-2024-REJ01", company, "Java Dev", "USR-INT-002")
        offer.mark_rejected("Not a fit")
        repository.save(offer)
        
        # Act
        active = repository.find_active_offers("USR-INT-002")
        
        # Assert
        assert len(active) == 0
    
    def test_update_offer(self, repository, sample_offer):
        """Тест: обновление существующего отклика"""
        # Arrange
        repository.save(sample_offer)
        
        # Act
        found = repository.find_by_id(sample_offer.id)
        found.change_stage(StageType.hr_screening())
        repository.save(found)
        
        # Assert
        updated = repository.find_by_id(sample_offer.id)
        assert updated.current_stage.value == "hr_screening"
    
    def test_delete_offer(self, repository, sample_offer):
        """Тест: удаление отклика"""
        # Arrange
        repository.save(sample_offer)
        
        # Act
        result = repository.delete(sample_offer.id)
        
        # Assert
        assert result is True
        assert repository.find_by_id(sample_offer.id) is None
    
    def test_delete_nonexistent_offer(self, repository):
        """Тест: удаление несуществующего отклика"""
        result = repository.delete("OFFER-NOT-EXIST")
        assert result is False
    
    def test_save_updates_existing_offer(self, repository, sample_offer):
        """Тест: повторное сохранение обновляет существующий отклик"""
        # Arrange
        repository.save(sample_offer)
        sample_offer.add_note("Тестовая заметка")
        
        # Act
        repository.save(sample_offer)
        
        # Assert
        found = repository.find_by_id(sample_offer.id)
        assert len(found.notes) == 1
        assert "Тестовая заметка" in found.notes[0]
    
    def test_multiple_offers_per_user(self, repository):
        """Тест: у пользователя может быть несколько откликов"""
        # Arrange
        company = CompanyName("ООО Тест")
        offer1 = JobOffer("OFFER-2024-M01", company, "Python Dev", "USR-MULTI")
        offer2 = JobOffer("OFFER-2024-M02", company, "Java Dev", "USR-MULTI")
        
        repository.save(offer1)
        repository.save(offer2)
        
        # Act
        offers = repository.find_by_user_id("USR-MULTI")
        
        # Assert
        assert len(offers) == 2
        ids = [o.id for o in offers]
        assert "OFFER-2024-M01" in ids
        assert "OFFER-2024-M02" in ids
    
    def test_find_by_user_and_company(self, repository, sample_offer):
        """Тест: поиск отклика по пользователю и компании"""
        # Arrange
        repository.save(sample_offer)
        
        # Act
        found = repository.find_by_user_and_company("USR-INT-001", "ООО Тест")
        
        # Assert
        assert found is not None
        assert found.id == sample_offer.id
    
    def test_find_by_user_and_company_not_found(self, repository, sample_offer):
        """Тест: поиск по несуществующей компании"""
        # Arrange
        repository.save(sample_offer)
        
        # Act
        found = repository.find_by_user_and_company("USR-INT-001", "Несуществующая компания")
        
        # Assert
        assert found is None
    
    def test_preserves_created_at_on_update(self, repository, sample_offer):
        """Тест: при обновлении created_at не меняется"""
        # Arrange
        repository.save(sample_offer)
        original_created = sample_offer.created_at
        
        # Act
        import time
        time.sleep(0.1)
        sample_offer.add_note("Новая заметка")
        repository.save(sample_offer)
        
        # Assert
        found = repository.find_by_id(sample_offer.id)
        assert found.created_at == original_created
        assert found.updated_at > original_created