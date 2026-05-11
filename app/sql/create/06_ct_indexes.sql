-- Índices para ct.studies
CREATE INDEX IF NOT EXISTS idx_studies_status_id
    ON ct.studies (status_id);

CREATE INDEX IF NOT EXISTS idx_studies_study_type_id
    ON ct.studies (study_type_id);

CREATE INDEX IF NOT EXISTS idx_studies_start_date
    ON ct.studies (start_date);

CREATE INDEX IF NOT EXISTS idx_studies_condition_id
    ON ct.studies (condition_id);

CREATE INDEX IF NOT EXISTS idx_studies_phase_id
    ON ct.studies (phase_id);
