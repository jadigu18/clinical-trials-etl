-- CONDITIONS
CREATE TABLE IF NOT EXISTS ct.conditions (
    condition_id  SERIAL PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE
);

-- INTERVENTIONS
CREATE TABLE IF NOT EXISTS ct.interventions (
    intervention_id  SERIAL PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE
);

-- ORGANIZATIONS
CREATE TABLE IF NOT EXISTS ct.organizations (
    organization_id  SERIAL PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE
);

-- PHASES
CREATE TABLE IF NOT EXISTS ct.phases (
    phase_id  SERIAL PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE
);

-- FUNDING SOURCES
CREATE TABLE IF NOT EXISTS ct.funding_sources (
    funding_source_id  SERIAL PRIMARY KEY,
    name               TEXT NOT NULL UNIQUE
);

-- STATUSES
CREATE TABLE IF NOT EXISTS ct.statuses (
    status_id  SERIAL PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE
);

-- STUDY TYPES
CREATE TABLE IF NOT EXISTS ct.study_types (
    study_type_id  SERIAL PRIMARY KEY,
    name           TEXT NOT NULL UNIQUE
);

