import os
import time
import psycopg2


def get_connection(max_retries=10, delay=2):
    host = os.environ.get('DB_HOST', 'localhost')

    for attempt in range(max_retries):
        try:
            return psycopg2.connect(
                host=host,
                port=5432,
                user='admin',
                password='admin',
                database='clinical'
            )
        except psycopg2.OperationalError as e:
            print(f"Intento {attempt + 1}/{max_retries} falló: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise


def run_all_migrations():
    folder = "sql/create"

    if not os.path.exists(folder):
        print(f"Error: No existe la carpeta {folder}")
        return

    scripts = sorted([f for f in os.listdir(folder) if f.endswith(".sql")])
    print(f"[INFO] Ejecutando {len(scripts)} scripts")

    with get_connection() as conn:
        with conn.cursor() as cur:
            for s in scripts:
                file_path = os.path.join(folder, s)
                print(f"[INFO] Ejecutando {s}")
                with open(file_path, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
                conn.commit()