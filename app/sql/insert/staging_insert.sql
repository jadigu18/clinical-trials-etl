INSERT INTO staging.raw_trials (
    rank, nct_number, title, acronym, status, study_results,
    conditions, interventions, outcome_measures, sponsor_collaborators,
    gender, age, phases, enrollment, funded_bys, study_type,
    study_designs, other_ids, start_date, primary_completion_date,
    completion_date, first_posted, results_first_posted,
    last_update_posted, locations, study_documents, url, _source_file
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
);