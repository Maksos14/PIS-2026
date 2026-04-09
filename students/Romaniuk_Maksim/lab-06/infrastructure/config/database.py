from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

class DatabaseConfig:
    def __init__(self, db_url: str = None):
        if db_url is None:
            db_url = "postgresql://postgres:postgres@localhost:5432/joboffer_db"
        self._engine = create_engine(db_url, echo=True)
        self._session_factory = sessionmaker(bind=self._engine)

    def get_session(self) -> Session:
        return self._session_factory()

    def create_tables(self):
        from infrastructure.models.job_offer_orm import Base
        Base.metadata.create_all(self._engine)

    def close(self):
        self._engine.dispose()