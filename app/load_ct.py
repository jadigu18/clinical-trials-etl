from db import get_connection
from transform import transform_row, normalize_text, populate_lookups, get_lookup_dicts


def load_ct(df):
    populate_lookups(df)

    conn = get_connection()
    cur = conn.cursor()

    print("[INFO] Cargando caché de diccionarios...")
    caches = get_lookup_dicts(cur)
    cond_cache = caches['conditions']
    phase_cache = caches['phases']
    status_cache = caches['statuses']
    study_type_cache = caches['study_types']
    funder_cache = caches['funding_sources']
    intervention_cache = caches['interventions']
    organization_cache = caches['organizations']

    print("[INFO] Insertando estudios...")

    estudios_insertados = 0
    errores = 0

    for i, row in df.iterrows():
        try:
            d = transform_row(row)

            if not d.get("nct_number"):
                print(f"  [WARN] Fila {i}: No tiene NCT Number, saltando...")
                errores += 1
                continue

            status_id = None
            if d.get("status"):
                norm_status = normalize_text(d["status"])
                if norm_status and norm_status in status_cache:
                    status_id = status_cache[norm_status]

            study_type_id = None
            if d.get("study_type"):
                norm_study_type = normalize_text(d["study_type"])
                if norm_study_type and norm_study_type in study_type_cache:
                    study_type_id = study_type_cache[norm_study_type]

            condition_id = None
            if d.get("conditions"):
                norm_cond = normalize_text(d["conditions"])
                if norm_cond and norm_cond in cond_cache:
                    condition_id = cond_cache[norm_cond]

            phase_id = None
            if d.get("phases"):
                norm_phase = normalize_text(d["phases"])
                if norm_phase and norm_phase in phase_cache:
                    phase_id = phase_cache[norm_phase]

            funding_source_id = None
            if d.get("funded_bys"):
                norm_funder = normalize_text(d["funded_bys"])
                if norm_funder and norm_funder in funder_cache:
                    funding_source_id = funder_cache[norm_funder]

            intervention_id = None
            if d.get("intervention_name"):
                norm_intervention = normalize_text(d["intervention_name"])
                if norm_intervention and norm_intervention in intervention_cache:
                    intervention_id = intervention_cache[norm_intervention]

            organization_id = None
            if d.get("primary_sponsor"):
                norm_org = normalize_text(d["primary_sponsor"])
                if norm_org and norm_org in organization_cache:
                    organization_id = organization_cache[norm_org]

            sql_estudio = """
                INSERT INTO ct.studies (
                    nct_number, title, acronym, url,
                    status_id, study_type_id,
                    condition_id, phase_id, funding_source_id, intervention_id, organization_id,
                    has_results,
                    gender, age, enrollment,
                    start_date, primary_completion_date, completion_date,
                    first_posted, results_first_posted, last_update_posted,
                    sponsor_collaborators, outcome_measures, study_documents,
                    locations, other_ids, study_designs
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (nct_number) DO UPDATE SET 
                    title = EXCLUDED.title,
                    status_id = EXCLUDED.status_id,
                    study_type_id = EXCLUDED.study_type_id,
                    condition_id = EXCLUDED.condition_id,
                    phase_id = EXCLUDED.phase_id,
                    funding_source_id = EXCLUDED.funding_source_id,
                    intervention_id = EXCLUDED.intervention_id,
                    organization_id = EXCLUDED.organization_id,
                    has_results = EXCLUDED.has_results,
                    updated_at = now()
            """

            valores_estudio = (
                d["nct_number"],
                d.get("title"),
                d.get("acronym"),
                d.get("url"),
                status_id,
                study_type_id,
                condition_id,
                phase_id,
                funding_source_id,
                intervention_id,
                organization_id,
                d.get("has_results", False),
                d.get("gender"),
                d.get("age"),
                d.get("enrollment"),
                d.get("start_date"),
                d.get("primary_completion_date"),
                d.get("completion_date"),
                d.get("first_posted"),
                d.get("results_first_posted"),
                d.get("last_update_posted"),
                d.get("sponsor_collaborators"),
                d.get("outcome_measures"),
                d.get("study_documents"),
                d.get("locations"),
                d.get("other_ids"),
                d.get("study_designs")
            )

            cur.execute(sql_estudio, valores_estudio)

            estudios_insertados += 1

            if estudios_insertados % 100 == 0:
                conn.commit()
                print(f"  [INFO] Procesados {estudios_insertados} estudios...")

        except Exception as e:
            conn.rollback()
            nct_log = row.get('NCT Number', 'Desconocido')
            print(f"  [ERROR] Fila {i} (NCT: {nct_log}): {e}")
            errores += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"[INFO] Carga finalizada. Insertados: {estudios_insertados}, Errores: {errores}")