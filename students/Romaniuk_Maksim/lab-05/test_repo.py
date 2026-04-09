from infrastructure.config.database import DatabaseConfig
from infrastructure.adapter.out.postgres_job_offer_repository import PostgresJobOfferRepository
from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName

# Используем SQLite
db = DatabaseConfig("sqlite:///./joboffer.db")
session = db.get_session()
repo = PostgresJobOfferRepository(session)

# Создаем и сохраняем
company = CompanyName("ООО Тест")
offer = JobOffer("OFFER-2024-0001", company, "Python Developer", "USR-12345")
repo.save(offer)
print(f"✅ Сохранен: {offer.id}")

# Находим
found = repo.find_by_id("OFFER-2024-0001")
print(f"✅ Найден: {found.company} - {found.position}")

# Список активных
active = repo.find_active_offers("USR-12345")
print(f"✅ Активных: {len(active)}")

session.close()
db.close()
print("✅ Все тесты пройдены!")
