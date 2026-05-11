from datetime import datetime
from db import get_connection


def parse_date(texto):
    """
    Normaliza fechas del csv
    """
    if not texto or str(texto).lower() in ["nan", "n/a", ""]:
        return None
    formatos = ["%B %d, %Y", "%B %Y", "%b-%y", "%m/%d/%Y", "%Y-%m-%d"]
    for f in formatos:
        try:
            return datetime.strptime(texto.strip(), f).date()
        except:
            continue
    return None


def normalize_text(text):
    """
    Normaliza el texto y nulos
    """
    if not text:
        return None

    # Convertir a string y limpiar
    text = str(text).lower().strip()

    # Detectar 'nan' y otros nulos
    if text in ['nan', 'null', 'none', 'n/a', '']:
        return None

    # Si después de limpiar queda vacío, retornar None
    if not text:
        return None

    return text

def populate_lookups(df):
    """
    Recorre el DF una vez para extraer valores únicos y normalizados,
    luego hace un insert en las lookup/tablas maestras
    """
    print("[INFO] Extrayendo valores únicos para catálogos...")

    # Sets para valores únicos (solo las tablas que existen)
    condiciones_unicas = set()
    fases_unicas = set()
    statuses_unicas = set()
    study_types_unicas = set()
    funders_unicas = set()
    interventions_unicas = set()
    organizations_unicas = set()

    for i, row in df.iterrows():
        d = transform_row(row)

        if d.get("conditions"):
            norm_cond = normalize_text(d["conditions"])
            if norm_cond:
                condiciones_unicas.add(norm_cond)

        if d.get("phases"):
            norm_fase = normalize_text(d["phases"])
            if norm_fase:
                fases_unicas.add(norm_fase)

        if d.get("funded_bys"):
            norm_funder = normalize_text(d["funded_bys"])
            if norm_funder:
                funders_unicas.add(norm_funder)

        if d.get("intervention_name"):
            norm_intervention = normalize_text(d["intervention_name"])
            if norm_intervention:
                interventions_unicas.add(norm_intervention)

        if d.get("primary_sponsor"):
            norm_org = normalize_text(d["primary_sponsor"])
            if norm_org:
                organizations_unicas.add(norm_org)

        if d.get("status"):
            norm_status = normalize_text(d["status"])
            if norm_status:
                statuses_unicas.add(norm_status)

        if d.get("study_type"):
            norm_study_type = normalize_text(d["study_type"])
            if norm_study_type:
                study_types_unicas.add(norm_study_type)

    conn = get_connection()
    cur = conn.cursor()

    try:
        if condiciones_unicas:
            cur.executemany(
                "INSERT INTO ct.conditions (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                [(c,) for c in condiciones_unicas]
            )
            print(f"  ✓ {len(condiciones_unicas)} condiciones")

        if fases_unicas:
            cur.executemany(
                "INSERT INTO ct.phases (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                [(f,) for f in fases_unicas]
            )
            print(f"  ✓ {len(fases_unicas)} fases")

        if statuses_unicas:
            cur.executemany(
                "INSERT INTO ct.statuses (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                [(s,) for s in statuses_unicas]
            )
            print(f"  ✓ {len(statuses_unicas)} statuses")

        if study_types_unicas:
            cur.executemany(
                "INSERT INTO ct.study_types (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                [(st,) for st in study_types_unicas]
            )
            print(f"  ✓ {len(study_types_unicas)} study types")

        if funders_unicas:
            cur.executemany(
                "INSERT INTO ct.funding_sources (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                [(f,) for f in funders_unicas]
            )
            print(f"  ✓ {len(funders_unicas)} funding sources")

        # Interventions
        if interventions_unicas:
            cur.executemany(
                "INSERT INTO ct.interventions (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                [(i,) for i in interventions_unicas]
            )
            print(f"  ✓ {len(interventions_unicas)} interventions")

        if organizations_unicas:
            cur.executemany(
                "INSERT INTO ct.organizations (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                [(o,) for o in organizations_unicas]
            )
            print(f"  ✓ {len(organizations_unicas)} organizations")

        conn.commit()
        print(f"[INFO] Lookups prepoblados exitosamente")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Al poblar lookups masivamente: {e}")
    finally:
        cur.close()
        conn.close()


def get_lookup_dicts(cur):
    def fetch_dict(table, id_col, name_col='name'):
        cur.execute(f"SELECT {name_col}, {id_col} FROM {table}")
        return {name: id for name, id in cur.fetchall()}

    return {
        'conditions': fetch_dict('ct.conditions', 'condition_id'),
        'phases': fetch_dict('ct.phases', 'phase_id'),
        'statuses': fetch_dict('ct.statuses', 'status_id'),
        'study_types': fetch_dict('ct.study_types', 'study_type_id'),
        'funding_sources': fetch_dict('ct.funding_sources', 'funding_source_id'),
        'interventions': fetch_dict('ct.interventions', 'intervention_id'),
        'organizations': fetch_dict('ct.organizations', 'organization_id')
    }


def transform_row(row):
    """
    Mapeo y tratamiento ajustado de cada una de las columnas del csv
    """
    nct = str(row.get("NCT Number", "")).strip()

    phases_raw = str(row.get("Phases") or "")
    if phases_raw.lower() in ['nan', 'null', 'none', '']:
        phases_raw = None

    conditions_raw = str(row.get("Conditions") or "")
    if conditions_raw.lower() in ['nan', 'null', 'none', '']:
        conditions_raw = None

    funded_bys_raw = str(row.get("Funded Bys") or "")
    if funded_bys_raw.lower() in ['nan', 'null', 'none', '']:
        funded_bys_raw = None

    intervencion_raw = str(row.get("Interventions") or "")
    inter_type = None
    inter_name = None
    if intervencion_raw and intervencion_raw.lower() not in ['nan', 'null', 'none', '']:
        if ":" in intervencion_raw:
            partes = intervencion_raw.split(":", 1)
            inter_type = partes[0].strip()
            inter_name = partes[1].strip()
        else:
            inter_type = "Other"
            inter_name = intervencion_raw.strip()

    # 4. Sponsor principal
    sponsors_raw = str(row.get("Sponsor/Collaborators") or "")
    primary_sponsor = None
    if sponsors_raw and sponsors_raw.lower() not in ['nan', 'null', 'none', '']:
        primary_sponsor = sponsors_raw.split("|")[0].strip()

    study_results_raw = str(row.get("Study Results") or "")
    has_results = study_results_raw.lower() == "has results" or study_results_raw.lower() == "yes"

    outcome_measures = row.get("Outcome Measures")
    if outcome_measures and str(outcome_measures).lower() in ['nan', 'null', 'none', '']:
        outcome_measures = None

    study_documents = row.get("Study Documents")
    if study_documents and str(study_documents).lower() in ['nan', 'null', 'none', '']:
        study_documents = None

    locations = row.get("Locations")
    if locations and str(locations).lower() in ['nan', 'null', 'none', '']:
        locations = None

    enrollment = None
    enrollment_raw = row.get("Enrollment")
    if enrollment_raw and str(enrollment_raw).isdigit():
        enrollment = int(enrollment_raw)

    return {
        "nct_number": nct,
        "title": row.get("Title"),
        "acronym": row.get("Acronym"),
        "url": row.get("URL"),
        "outcome_measures": outcome_measures,
        "study_documents": study_documents,
        "sponsor_collaborators": sponsors_raw if sponsors_raw else None,
        "primary_sponsor": primary_sponsor,
        "gender": row.get("Gender"),
        "age": row.get("Age"),
        "enrollment": enrollment,
        "start_date": parse_date(row.get("Start Date")),
        "primary_completion_date": parse_date(row.get("Primary Completion Date")),
        "completion_date": parse_date(row.get("Completion Date")),
        "first_posted": parse_date(row.get("First Posted")),
        "results_first_posted": parse_date(row.get("Results First Posted")),
        "last_update_posted": parse_date(row.get("Last Update Posted")),
        "other_ids": row.get("Other IDs"),
        "locations": locations,
        "conditions": conditions_raw,
        "phases": phases_raw,
        "funded_bys": funded_bys_raw,
        "intervention_type": inter_type,
        "intervention_name": inter_name,
        "status": row.get("Status"),
        "study_type": row.get("Study Type"),
        "has_results": has_results
    }