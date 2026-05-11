CREATE TABLE IF NOT EXISTS ct.studies (
    nct_number               CHAR(11)     PRIMARY KEY,
    title                    TEXT         NOT NULL,
    acronym                  VARCHAR(50),
    url                      TEXT,

    status_id                INTEGER      REFERENCES ct.statuses(status_id),
    study_type_id            INTEGER      REFERENCES ct.study_types(study_type_id),
    condition_id             INTEGER      REFERENCES ct.conditions(condition_id),
    phase_id                 INTEGER      REFERENCES ct.phases(phase_id),
    funding_source_id        INTEGER      REFERENCES ct.funding_sources(funding_source_id),
    intervention_id          INTEGER      REFERENCES ct.interventions(intervention_id),
    organization_id          INTEGER      REFERENCES ct.organizations(organization_id),

    has_results              BOOLEAN      NOT NULL DEFAULT FALSE,

    gender                   TEXT,
    age                      TEXT,
    enrollment               INT,

    start_date               DATE,
    primary_completion_date  DATE,
    completion_date          DATE,
    first_posted             DATE,
    results_first_posted     DATE,
    last_update_posted       DATE,

    sponsor_collaborators    TEXT,
    outcome_measures         TEXT,
    study_documents          TEXT,
    locations                TEXT,
    other_ids                TEXT,
    study_designs            TEXT,

    created_at               TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ  NOT NULL DEFAULT now()
);