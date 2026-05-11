# Clinical Trials ETL Pipeline

## Project Overview

This project is a simple ETL pipeline built with Python and PostgreSQL for loading and transforming ClinicalTrials.gov COVID clinical trial data.

The pipeline reads a CSV file, loads the raw data into a staging schema to preserve the raw data. Then transforms and normalizes the data, and 
finally loads it into a relational schema optimized for analytics following a dimensional modeling approach

The project follows a layered approach:

1. Raw ingestion into staging tables
2. Data transformation and normalization through dataframes treatment
3. Loading into analytical tables with lookup dimensions

---

# Architecture

```text
                +----------------------+
                |   CSV Input File     |
                | COVID clinical trials|
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      ETL Layer:       |
                |  small pandas usage  | 
                |    in this point     |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   staging.raw_trials |
                |   Raw unprocessed    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Transformation Layer |
                | normalization        |
                | date parsing         |
                | lookup extraction    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      ct schema       |
                | lookups + studies    |
                +----------------------+
```

---

# Tech Stack

* Python
* pandas
* PostgreSQL
* Docker

---

# Local Setup

## Prerequisites
Docker installed

Docker Compose installed

## 1. Clone repository

```bash
git clone https://github.com/jadigu18/clinical-trials-etl.git
cd clinical-trials-etl
```

---



## 2. Add dataset

Place the CSV file inside:

```text
/data/COVID clinical trials.csv
```


## 3. Build and start Docker from project directory

```bash
docker compose build
docker compose up -d

```

# Database Design

The project uses two schemas:

## staging schema

Stores the raw CSV exactly as received.

Table:

* staging.raw_trials

Purpose:

* preserve original source data
* simplify debugging
* separate raw and transformed data

---

## ct schema

Contains normalized analytical tables.

Main table:

* ct.studies

Lookup tables:

* conditions
* interventions
* organizations
* phases
* funding_sources
* statuses
* study_types

This approach reduces duplicated text values and improves query performance.

---

# Design Decisions

## Staging Layer

I decided to use a staging table to easily keep the raw source untouched before transformations for this project.

This makes debugging easier and allows reprocessing if transformation logic changes later.

---

## Lookup Tables

Instead of storing repeated text values directly in the studies table, I created lookup tables for:

* conditions
* interventions
* organizations
* phases
* funding_sources
* statuses
* study_types

This reduces duplication and creates a cleaner relational model.

The ct schema separates textual attributes into lookup tables instead of storing them directly in the main studies table. 
This follows a Star Schema approach with:
* better performance
* a single source of truth
* business readability using lookups tables that give the meaning of each value
* data integrity ensured with the foreign keys values


---

## Data Normalization

Text normalization was added to avoid duplicated values caused by:

* uppercase/lowercase differences
* extra spaces
* null-like strings

Example:

* "COVID-19"
* "covid-19 "
* "Covid-19"

All become normalized before insertion.

However it is important to remark that this normalization could be done much more robust with more time making a more
deep analysis of the dataset. 

Some enhancements considered:
* Conditions field

The conditions column shows a clear fragmentation problem: "SARS-CoV-2", "covid19", "covid 19", "sarscov2", 
and "COVID-19" all refer to the same underlying pathology but currently live under different IDs. Also, some appears to 
have multiple components inside one record "infection viral|thromboses, venous|covid-19". A stronger normalization
could be built by creating equivalence dictionaries that map the most common variants to a single canonical term. 
This dictionary approach would handle the majority of cases without complex logic, leaving only edge cases for manual review. 

* Location field

The geographic analysis currently relies on the raw locations field directly from the dataset. Since this data is stored
as free text with no standardization, the current approach is only a basic approximation — not reliable enough for precise 
geographic distribution reporting.

And more fields could be added..

With more time, a stronger normalization process could be applied to better group similar locations. For example, using 
external geographic datasets (GeoNames, OpenStreetMap) combined with fuzzy matching techniques to:
* Identify similar country or city names ("USA" ↔ "United States" ↔ "U.S.A.")
* Assign each variant to the same geographic area accurately
* Potentially split compound location strings into structured fields (city, state, country)
This would transform the location dimension from a noisy free-text field into a reliable analytical axis, enabling accurate questions like "trial distribution by country" or "top recruiting cities."
....

---

## Cache Dictionaries

During loading, lookup IDs are cached in memory to avoid running SQL SELECT queries for every row.

This improves performance during inserts.

---

## Incremental Safety

`ON CONFLICT` was used for:

* lookup tables
* studies table

This prevents duplicated records and allows safe re-runs of the pipeline.

---

# Trade-offs and Limitations

## Simplified Relationships

For simplicity and time constraints, the current model uses single foreign keys for:

* condition
* intervention
* phase

In reality, clinical trials can have multiple conditions or interventions, so a many-to-many design would be more accurate.



## No Orchestration Tool

The pipeline runs sequentially from a Python script.

Tools like Airflow were intentionally not added to keep the solution lightweight.

---

# Analytics Support

The final schema supports analytics such as:

* trials by phase and study type
* most common conditions
* intervention completion rates
* study duration analysis
* organization-based reporting

You can find those queries in sql/analytics/analytics_queries.sql
Indexes were added on the most queried columns to improve filtering and joins.

---

# Time Allocation

| Task                       | Time |
| -------------------------- |------|
| Database design            | 2h   |
| ETL development            | 1h   |
| Transformation logic       | 1h   |
| Testing and debugging      | 0.5h |
| README and documentation   | 1h   |

Approximate total: 5.5 hours

---

# Future Improvements

Possible next steps:

* Add many-to-many relationship tables
* Incremental loading: If the source CSV is updated periodically with the same structure, new and modified records could
be detected by comparing nct_number against the existing staging table, then only inserting or updating the changed 
rows instead of reprocessing the entire dataset.
* Add Airflow orchestration
* Add automated tests and robust dq
* Add logging system
* Add data quality validations
* Add incremental loading support
* Add country and location normalization
* Containerize the full application with docker-compose
* Add monitoring and retry mechanisms

---

# Scalability Considerations

For larger datasets, the following improvements could help:

* connection pooling
* partitioning large tables
* async processing
* Using s3 buckets among steps and create backups and layers for raw and transformed data
* cloud object storage ingestion
* distributed processing tools like Spark

The current implementation is designed for simplicity and readability rather than very large-scale processing.


# AI Tools & Coding Assistance
AI tools (Gemini) was used sparingly during development for:

* documentation structure and wording
* brainstorming normalization strategies for messy text fields
* troubleshooting specific syntax issues and PostgreSQL function quirks

All core decisions — schema design, ETL architecture, transformation logic, and trade-offs — are my own. Every part of 
the codebase has been reviewed, tested, and is fully explainable.