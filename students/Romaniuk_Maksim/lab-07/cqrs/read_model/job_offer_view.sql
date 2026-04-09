-- cqrs/read_model/job_offer_view.sql

-- Денормализованная таблица для read модели
CREATE TABLE IF NOT EXISTS job_offer_views (
    id VARCHAR(50) PRIMARY KEY,
    company VARCHAR(100) NOT NULL,
    position VARCHAR(200) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_stage VARCHAR(30) NOT NULL,
    progress_percentage FLOAT DEFAULT 0,
    notes JSON DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    is_rejected BOOLEAN DEFAULT FALSE,
    is_offer_received BOOLEAN DEFAULT FALSE,
    notes_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX idx_job_offer_views_user_id ON job_offer_views(user_id);
CREATE INDEX idx_job_offer_views_status ON job_offer_views(status);
CREATE INDEX idx_job_offer_views_current_stage ON job_offer_views(current_stage);
CREATE INDEX idx_job_offer_views_user_status ON job_offer_views(user_id, status);
CREATE INDEX idx_job_offer_views_user_stage ON job_offer_views(user_id, current_stage);
CREATE INDEX idx_job_offer_views_is_active ON job_offer_views(is_active);

-- Материализованное представление для активных откликов
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_active_offers AS
SELECT 
    id,
    company,
    position,
    user_id,
    current_stage,
    progress_percentage,
    created_at
FROM job_offer_views
WHERE is_active = TRUE 
  AND is_rejected = FALSE 
  AND is_offer_received = FALSE;

-- Индекс для материализованного представления
CREATE INDEX idx_mv_active_offers_user_id ON mv_active_offers(user_id);

-- Функция обновления материализованного представления
CREATE OR REPLACE FUNCTION refresh_active_offers_mv()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_offers;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического обновления MV
CREATE TRIGGER trigger_refresh_active_offers
AFTER INSERT OR UPDATE OR DELETE ON job_offer_views
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_active_offers_mv();