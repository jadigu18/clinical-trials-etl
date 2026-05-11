-- trials by study type and phase: Only interventional ones have a phase informed
SELECT
    st.name                          AS study_type,
    p.name                           AS phase,
    COUNT(ct.nct_number)             AS trial_count
FROM ct.studies ct
INNER JOIN ct.study_types     st ON ct.study_type_id    = st.study_type_id
LEFT JOIN ct.phases          p  ON ct.phase_id         = p.phase_id
GROUP BY
    st.name,
    p.name
ORDER BY
    st.name,
    trial_count DESC;



-- Ranks conditions by number of trials associated with them
SELECT
    c.name                           AS condition,
    COUNT(ct.nct_number)             AS trial_count,
    ROUND(
        COUNT(ct.nct_number) * 100.0
        / SUM(COUNT(ct.nct_number)) OVER (),
        2
    )                                AS pct_of_all_trials
FROM ct.studies ct
JOIN ct.conditions c ON ct.condition_id = c.condition_id
WHERE c.name IS NOT NULL
GROUP BY c.name
ORDER BY trial_count DESC
LIMIT 25;



--  interventions with the highest completion rates
SELECT
    i.name AS intervention,
    COUNT(ct.nct_number) AS total_trials,

    COUNT(ct.nct_number)
        FILTER (WHERE ct.status_id = 10) AS completed_trials,

    ROUND(
        COUNT(ct.nct_number)
            FILTER (WHERE ct.status_id = 10)
        * 100.0
        / COUNT(ct.nct_number),
        2
    ) AS completion_rate_pct
FROM ct.studies ct
JOIN ct.interventions i
    ON ct.intervention_id = i.intervention_id
GROUP BY i.name
HAVING COUNT(ct.nct_number) >= 10
ORDER BY completion_rate_pct DESC,
         total_trials DESC
LIMIT 50;



-- Geo dritribution: Looks like the last coma of the field covers the country
SELECT
    TRIM(SPLIT_PART(locations, ',', -1)) AS country,
    COUNT(*) AS total_trials
FROM ct.studies
WHERE locations IS NOT NULL
GROUP BY country
ORDER BY total_trials DESC
LIMIT 25;




--timeline analysis
SELECT
    nct_number,
    title,
    start_date,
    completion_date,
    completion_date - start_date AS study_duration_days
FROM ct.studies
WHERE start_date IS NOT NULL
  AND completion_date IS NOT NULL
ORDER BY study_duration_days DESC
LIMIT 25;