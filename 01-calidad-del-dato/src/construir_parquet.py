"""Convierte el snapshot CSV en un Parquet liviano y sin datos personales.

- Las columnas de personas (representante legal, ordenadores, supervisor, cuenta
  bancaria) se reemplazan por una bandera `<columna>_informado` (True/False),
  suficiente para medir completitud sin publicar el dato.
- Si el proveedor no es una empresa (NIT), su nombre se elimina y su documento se
  reemplaza por un seudónimo (HMAC-SHA256 con una sal local que no se publica).
  Se conservan la longitud y si el documento es solo dígitos, para poder medir
  validez y unicidad.

Uso:
    python src/construir_parquet.py data/secop2_contratos_2026-10-27_50000.csv
"""

import hashlib
import hmac
import pathlib
import secrets
import sys

import pandas as pd

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
SAL = DATA_DIR / ".sal"

COLUMNAS_PERSONALES = [
    "nombre_representante_legal",
    "nacionalidad_representante_legal",
    "domicilio_representante_legal",
    "tipo_de_identificaci_n_representante_legal",
    "identificaci_n_representante_legal",
    "g_nero_representante_legal",
    "nombre_del_banco",
    "tipo_de_cuenta",
    "n_mero_de_cuenta",
    "nombre_ordenador_del_gasto",
    "tipo_de_documento_ordenador_del_gasto",
    "n_mero_de_documento_ordenador_del_gasto",
    "nombre_supervisor",
    "tipo_de_documento_supervisor",
    "n_mero_de_documento_supervisor",
    "nombre_ordenador_de_pago",
    "tipo_de_documento_ordenador_de_pago",
    "n_mero_de_documento_ordenador_de_pago",
]

# Textos que la fuente usa en lugar de un nulo real.
NULOS_DISFRAZADOS = {"", "no definido", "no aplica", "n/a", "na", "sin descripcion", "null"}


def leer_sal() -> bytes:
    if not SAL.exists():
        SAL.write_text(secrets.token_hex(32))
    return SAL.read_text().strip().encode()


def informado(serie: pd.Series) -> pd.Series:
    return ~serie.str.strip().str.lower().isin(NULOS_DISFRAZADOS)


def construir(csv_path: pathlib.Path) -> pathlib.Path:
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    sal = leer_sal()

    for col in COLUMNAS_PERSONALES:
        df[f"{col}_informado"] = informado(df[col])
    df = df.drop(columns=COLUMNAS_PERSONALES)

    doc = df["documento_proveedor"].str.strip()
    persona = df["tipodocproveedor"] != "NIT"
    df["documento_proveedor_longitud"] = doc.str.len()
    df["documento_proveedor_solo_digitos"] = doc.str.fullmatch(r"\d+")
    df.loc[persona, "documento_proveedor"] = doc[persona].map(
        lambda d: hmac.new(sal, d.encode(), hashlib.sha256).hexdigest()[:16] if d else ""
    )
    df.loc[persona, "proveedor_adjudicado"] = "[persona natural]"

    destino = csv_path.with_suffix(".parquet")
    df.to_parquet(destino, compression="zstd", index=False)
    return destino


if __name__ == "__main__":
    print(f"Parquet guardado en {construir(pathlib.Path(sys.argv[1]))}")
