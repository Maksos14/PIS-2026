# cqrs/read_model/optimized_read_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from cqrs.read_model.job_offer_view import JobOfferView, JobOfferSummaryView
from cqrs.read_model.job_offer_read_repository import JobOfferReadRepository


class OptimizedJobOfferReadRepository(JobOfferReadRepository):
    """
    Оптимизированная read-репозиторий с использованием:
    - материализованных представлений
    - прямых SQL запросов
    - агрегатных функций
    """
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, view: JobOfferView) -> None:
        """Сохранить в обычную таблицу (триггер обновит MV)"""
        from cqrs.read_model.postgres_job_offer_read_repository import PostgresJobOfferReadRepository
        repo = PostgresJobOfferReadRepository(self._session)
        repo.save(view)
    
    def find_by_id(self, offer_id: str) -> Optional[JobOfferView]:
        """Обычный поиск по ID"""
        from cqrs.read_model.postgres_job_offer_read_repository import PostgresJobOfferReadRepository
        repo = PostgresJobOfferReadRepository(self._session)
        return repo.find_by_id(offer_id)
    
    def find_by_user_id(self, user_id: str) -> List[JobOfferView]:
        """Обычный поиск по пользователю"""
        from cqrs.read_model.postgres_job_offer_read_repository import PostgresJobOfferReadRepository
        repo = PostgresJobOfferReadRepository(self._session)
        return repo.find_by_user_id(user_id)
    
    def find_active_offers(self, user_id: str) -> List[JobOfferSummaryView]:
        """
        ОПТИМИЗИРОВАННЫЙ запрос через материализованное представление
        (значительно быстрее, чем обычный SELECT)
        """
        sql = text("""
            SELECT 
                id, company, position, current_stage, progress_percentage
            FROM mv_active_offers
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """)
        
        result = self._session.execute(sql, {"user_id": user_id})
        rows = result.fetchall()
        
        return [
            JobOfferSummaryView(
                id=row[0],
                company=row[1],
                position=row[2],
                current_stage=row[3],
                progress_percentage=row[4]
            )
            for row in rows
        ]
    
    def find_by_stage(self, user_id: str, stage: str) -> List[JobOfferSummaryView]:
        """Поиск по этапу с использованием индекса"""
        from cqrs.read_model.postgres_job_offer_read_repository import PostgresJobOfferReadRepository
        repo = PostgresJobOfferReadRepository(self._session)
        return repo.find_by_stage(user_id, stage)
    
    def delete(self, offer_id: str) -> bool:
        """Удаление"""
        from cqrs.read_model.postgres_job_offer_read_repository import PostgresJobOfferReadRepository
        repo = PostgresJobOfferReadRepository(self._session)
        return repo.delete(offer_id)
    
    # ========== Дополнительные оптимизированные методы ==========
    
    def get_user_statistics(self, user_id: str) -> dict:
        """
        Получение статистики пользователя из материализованного представления
        """
        sql = text("""
            SELECT 
                total_offers,
                active_count,
                rejected_count,
                offer_received_count,
                avg_progress,
                last_activity
            FROM mv_user_offer_stats
            WHERE user_id = :user_id
        """)
        
        result = self._session.execute(sql, {"user_id": user_id}).first()
        
        if not result:
            return {
                "total_offers": 0,
                "active_count": 0,
                "rejected_count": 0,
                "offer_received_count": 0,
                "avg_progress": 0.0,
                "last_activity": None
            }
        
        return {
            "total_offers": result[0],
            "active_count": result[1],
            "rejected_count": result[2],
            "offer_received_count": result[3],
            "avg_progress": float(result[4]) if result[4] else 0.0,
            "last_activity": result[5]
        }
    
    def search_offers(self, user_id: str, query: str) -> List[JobOfferSummaryView]:
        """
        Полнотекстовый поиск по компании и позиции
        """
        sql = text("""
            SELECT 
                id, company, position, current_stage, progress_percentage
            FROM job_offer_views
            WHERE user_id = :user_id
              AND to_tsvector('russian', company || ' ' || position) @@ plainto_tsquery('russian', :query)
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        result = self._session.execute(sql, {"user_id": user_id, "query": query})
        
        return [
            JobOfferSummaryView(
                id=row[0],
                company=row[1],
                position=row[2],
                current_stage=row[3],
                progress_percentage=row[4]
            )
            for row in result.fetchall()
        ]
    
    def get_top_active_users(self, limit: int = 10) -> List[dict]:
        """
        Получение топ пользователей по активности (из MV)
        """
        sql = text("""
            SELECT 
                user_id,
                total_offers,
                active_count,
                avg_progress
            FROM mv_user_offer_stats
            ORDER BY total_offers DESC
            LIMIT :limit
        """)
        
        result = self._session.execute(sql, {"limit": limit})
        
        return [
            {
                "user_id": row[0],
                "total_offers": row[1],
                "active_count": row[2],
                "avg_progress": float(row[3]) if row[3] else 0.0
            }
            for row in result.fetchall()
        ]
    
    def refresh_materialized_views(self) -> None:
        """
        Ручное обновление всех материализованных представлений
        """
        sql = text("SELECT refresh_all_views()")
        self._session.execute(sql)
        self._session.commit()
