import pandas as pd
import os


def load_csv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base_dir, "data", "COVID clinical trials.csv")

    if not os.path.exists(ruta):
        print(f"Error: Archivo no encontrado en {ruta}")
        return None

    df = pd.read_csv(ruta, sep=",", dtype=str,
                     na_values=['', 'nan', 'NULL', 'N/A', 'null', 'NaN', 'none', 'None', '#N/A'])
    df.columns = [c.strip() for c in df.columns]
    df = df.where(pd.notna(df), None)

    print(f"[INFO] CSV correctamente cargado: {len(df)} filas.")
    return df