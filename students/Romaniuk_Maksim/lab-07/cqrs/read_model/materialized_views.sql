-- cqrs/read_model/materialized_views.sql

-- =====================================================
-- 1. Материализованное представление для активных откликов
-- =====================================================

-- Создание материализованного представления
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_active_offers AS
SELECT 
    id,
    company,
    position,
    user_id,
    current_stage,
    progress_percentage,
    notes_count,
    created_at,
    updated_at
FROM job_offer_views
WHERE is_active = TRUE 
  AND is_rejected = FALSE 
  AND is_offer_received = FALSE;

-- Индекс для быстрого поиска по пользователю
CREATE INDEX IF NOT EXISTS idx_mv_active_offers_user_id ON mv_active_offers(user_id);

-- Индекс для сортировки по дате создания
CREATE INDEX IF NOT EXISTS idx_mv_active_offers_created_at ON mv_active_offers(created_at DESC);

-- Индекс для фильтрации по этапу
CREATE INDEX IF NOT EXISTS idx_mv_active_offers_stage ON mv_active_offers(current_stage);


-- =====================================================
-- 2. Материализованное представление для статистики по пользователям
-- =====================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_user_offer_stats AS
SELECT 
    user_id,
    COUNT(*) as total_offers,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_count,
    COUNT(CASE WHEN status = 'offer_received' THEN 1 END) as offer_received_count,
    AVG(progress_percentage) as avg_progress,
    MAX(updated_at) as last_activity
FROM job_offer_views
GROUP BY user_id;

CREATE INDEX IF NOT EXISTS idx_mv_user_stats_user_id ON mv_user_offer_stats(user_id);


-- =====================================================
-- 3. Функции для обновления материализованных представлений
-- =====================================================

-- Функция обновления mv_active_offers
CREATE OR REPLACE FUNCTION refresh_active_offers_mv()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_offers;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Функция обновления mv_user_offer_stats
CREATE OR REPLACE FUNCTION refresh_user_stats_mv()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_offer_stats;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- 4. Триггеры для автоматического обновления
-- =====================================================

-- Триггер на обновление job_offer_views
DROP TRIGGER IF EXISTS trigger_refresh_active_offers ON job_offer_views;
CREATE TRIGGER trigger_refresh_active_offers
AFTER INSERT OR UPDATE OR DELETE ON job_offer_views
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_active_offers_mv();

DROP TRIGGER IF EXISTS trigger_refresh_user_stats ON job_offer_views;
CREATE TRIGGER trigger_refresh_user_stats
AFTER INSERT OR UPDATE OR DELETE ON job_offer_views
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_user_stats_mv();


-- =====================================================
-- 5. Дополнительные индексы для оптимизации запросов
-- =====================================================

-- Составной индекс для частых фильтров
CREATE INDEX IF NOT EXISTS idx_job_offer_views_user_status_stage 
ON job_offer_views(user_id, status, current_stage);

-- Индекс для полнотекстового поиска по компании и позиции
CREATE INDEX IF NOT EXISTS idx_job_offer_views_search 
ON job_offer_views USING gin(
    to_tsvector('russian', company || ' ' || position)
);

-- Индекс для быстрой сортировки по прогрессу
CREATE INDEX IF NOT EXISTS idx_job_offer_views_progress 
ON job_offer_views(progress_percentage DESC);


-- =====================================================
-- 6. Функции для работы с материализованными представлениями
-- =====================================================

-- Функция ручного обновления всех представлений
CREATE OR REPLACE FUNCTION refresh_all_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_offers;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_offer_stats;
END;
$$ LANGUAGE plpgsql;

-- Функция получения активных откликов из материализованного представления
CREATE OR REPLACE FUNCTION get_active_offers(p_user_id VARCHAR)
RETURNS TABLE(
    id VARCHAR,
    company VARCHAR,
    position VARCHAR,
    current_stage VARCHAR,
    progress_percentage FLOAT,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mv.id,
        mv.company,
        mv.position,
        mv.current_stage,
        mv.progress_percentage,
        mv.created_at
    FROM mv_active_offers mv
    WHERE mv.user_id = p_user_id
    ORDER BY mv.created_at DESC;
END;
$$ LANGUAGE plpgsql;