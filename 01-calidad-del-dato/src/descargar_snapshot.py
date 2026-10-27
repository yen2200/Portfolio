"""Descarga un snapshot reproducible de SECOP II - Contratos Electrónicos.

Fuente: https://www.datos.gov.co/d/jbjy-vk9h (Colombia Compra Eficiente),
licencia CC BY-SA 4.0. Usa la API SODA de datos.gov.co, ordenando por el id
interno del registro para que el mismo límite devuelva siempre las mismas filas
mientras el dataset no se reprocese.

Uso:
    python src/descargar_snapshot.py --filas 50000
"""

import argparse
import datetime as dt
import json
import pathlib
import urllib.parse
import urllib.request

DATASET_ID = "jbjy-vk9h"
BASE_URL = f"https://www.datos.gov.co/resource/{DATASET_ID}.csv"
PAGINA = 50_000
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


def descargar(filas: int) -> pathlib.Path:
    DATA_DIR.mkdir(exist_ok=True)
    fecha = dt.date.today().isoformat()
    destino = DATA_DIR / f"secop2_contratos_{fecha}_{filas}.csv"

    with destino.open("wb") as salida:
        for offset in range(0, filas, PAGINA):
            params = {
                "$limit": min(PAGINA, filas - offset),
                "$offset": offset,
                "$order": ":id",
            }
            url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
            with urllib.request.urlopen(url, timeout=120) as resp:
                bloque = resp.read()
            # La API repite el encabezado en cada página: se conserva solo el primero.
            if offset > 0:
                bloque = bloque.split(b"\n", 1)[1]
            salida.write(bloque)
            print(f"  filas {offset:,}–{offset + params['$limit']:,} descargadas")

    meta = {
        "dataset_id": DATASET_ID,
        "fuente": f"https://www.datos.gov.co/d/{DATASET_ID}",
        "licencia": "CC BY-SA 4.0",
        "fecha_descarga": fecha,
        "filas_solicitadas": filas,
        "orden": ":id",
    }
    destino.with_suffix(".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return destino


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--filas", type=int, default=50_000)
    args = parser.parse_args()
    print(f"Snapshot guardado en {descargar(args.filas)}")
