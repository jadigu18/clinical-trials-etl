import os
from db import get_connection
import pandas as pd
from constants import clinical_csv


def load_staging(df):
    if df is None:
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_sql = os.path.join(base_dir, "sql", "insert", "staging_insert.sql")

    if not os.path.exists(ruta_sql):
        print(f"Error: Archivo no encontrado en {ruta_sql}")
        return

    with open(ruta_sql, "r", encoding="utf-8") as f:
        sql_query = f.read()

    clinical_csv = clinical_csv

    registros = []
    for _, row in df.iterrows():
        fila_limpia = []
        for valor in row:
            if pd.isna(valor) or valor is None:
                fila_limpia.append(None)
            else:
                if isinstance(valor, str) and valor.lower() in ['nan', 'null', 'none']:
                    fila_limpia.append(None)
                else:
                    fila_limpia.append(valor)

        registros.append(tuple(fila_limpia + [clinical_csv]))

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.executemany(sql_query, registros)
        conn.commit()
        print(f"[INFO] Datos cargados en tabla stg.")
    except Exception as e:
        print(f"[ERROR] Al cargar staging: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()