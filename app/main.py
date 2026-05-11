from db import run_all_migrations
from etl import load_csv
from load_staging import load_staging
from load_ct import load_ct


def run() -> None:
    print("=" * 50)
    print("  ETL — ClinicalTrials.gov")
    print("=" * 50)

    print("\n[0/3] Creando tablas y esquemas en PostgresSQL...")
    run_all_migrations()

    print("\n[1/3] Leyendo CSV...")
    df = load_csv()

    print("\n[2/3] Cargando staging...")
    load_staging(df)

    print("\n[3/3] Cargando schema ct...")
    load_ct(df)

    print("\n" + "=" * 50)
    print("  Pipeline correctamente ejecutado")
    print("=" * 50)


if __name__ == "__main__":
    run()
