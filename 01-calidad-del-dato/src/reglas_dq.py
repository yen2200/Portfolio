"""Reglas de calidad del dato para SECOP II - Contratos Electrónicos (Fase 2).

Cada regla devuelve, por contrato, True (cumple), False (no cumple) o <NA> (no
aplica). El cumplimiento de una regla es cumple / aplicables, y se compara con
la meta de su criticidad.

Los parámetros de negocio están en PARAMETROS y METAS: son decisiones, no
constantes técnicas, y cada una lleva su justificación.

Uso:
    python src/reglas_dq.py
"""

import pathlib
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SNAPSHOT = RAIZ / "data" / "secop2_contratos_2026-10-27_50000.parquet"
FECHA_CORTE = pd.Timestamp("2026-10-27")

PARAMETROS = {
    # Por debajo de este valor (COP) se considera un valor de relleno, no un precio.
    "valor_minimo": 1_000,
    # Días que el inicio puede anteceder a la firma antes de marcarlo inconsistente.
    "tolerancia_inicio_antes_firma_dias": 0,
    # Diferencia admitida entre la duración declarada y la que dan las fechas.
    "tolerancia_duracion_dias": 30,
    # Días que un contrato puede seguir "En ejecución" después de su fecha de fin.
    "dias_gracia_estado_vencido": 90,
    # Un valor es atípico si su log10 supera Q3 + k·IQR dentro de su tipo de contrato.
    "k_iqr_atipicos": 3,
}

# Meta de cumplimiento (%) según la criticidad de la regla.
METAS = {"alta": 99.0, "media": 95.0, "baja": 90.0}

NULOS_DISFRAZADOS = {"", "no definido", "no aplica", "n/a", "na", "null", "sin descripcion",
                     "no especificado", "sin información", "sin informacion"}

DIAS_POR_UNIDAD = {"Dia": 1, "Semana": 7, "Mes": 30.44, "Año": 365.25, "Hora": 1 / 24}


@dataclass(frozen=True)
class Regla:
    id: str
    dimension: str
    descripcion: str
    criticidad: str
    evaluar: Callable[[pd.DataFrame], pd.Series]


# --- Preparación -------------------------------------------------------------

def preparar(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte tipos una sola vez y marca los nulos disfrazados como nulos."""
    p = df.copy()
    for c in p.columns:
        if pd.api.types.is_string_dtype(p[c]):
            s = p[c].str.strip()
            p[c] = s.mask(s.str.lower().isin(NULOS_DISFRAZADOS))
    for c in ["fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato",
              "ultima_actualizacion"]:
        p[c] = pd.to_datetime(p[c], errors="coerce", format="ISO8601")
    for c in ["valor_del_contrato", "valor_pagado", "valor_facturado", "dias_adicionados"]:
        p[c] = pd.to_numeric(p[c], errors="coerce")
    dur = p["duraci_n_del_contrato"].str.extract(r"(?P<n>\d+)\s*(?P<unidad>Dia|Semana|Mes|Año|Hora)")
    p["duracion_declarada_dias"] = pd.to_numeric(dur["n"]) * dur["unidad"].map(DIAS_POR_UNIDAD)
    return p


def _resultado(cumple: pd.Series, aplica: pd.Series | None = None) -> pd.Series:
    r = cumple.astype("boolean")
    if aplica is not None:
        r = r.mask(~aplica.fillna(False).astype(bool))
    return r


# --- Reglas ------------------------------------------------------------------

def completitud(columna: str) -> Callable[[pd.DataFrame], pd.Series]:
    return lambda p: _resultado(p[columna].notna())


def documento_valido(p: pd.DataFrame) -> pd.Series:
    largo = p["documento_proveedor_longitud"]
    digitos = p["documento_proveedor_solo_digitos"].fillna(False)
    tipo = p["tipodocproveedor"]
    cc = tipo == "Cédula de Ciudadanía"
    nit = tipo == "NIT"
    cumple = digitos & ((cc & largo.between(6, 10)) | (nit & largo.between(9, 10)))
    return _resultado(cumple, cc | nit)


def valor_plausible_minimo(p: pd.DataFrame) -> pd.Series:
    no_comodato = p["tipo_de_contrato"] != "Comodato"
    return _resultado(p["valor_del_contrato"] >= PARAMETROS["valor_minimo"], no_comodato)


def forma_canonica(columna: str) -> Callable[[pd.DataFrame], pd.Series]:
    """El valor empieza con mayúscula, como el resto de su dominio."""
    def evaluar(p: pd.DataFrame) -> pd.Series:
        s = p[columna]
        return _resultado(s.str[:1] == s.str[:1].str.upper(), s.notna())
    return evaluar


def fin_despues_de_inicio(p: pd.DataFrame) -> pd.Series:
    ini, fin = p["fecha_de_inicio_del_contrato"], p["fecha_de_fin_del_contrato"]
    return _resultado(fin.dt.normalize() >= ini.dt.normalize(), ini.notna() & fin.notna())


def inicio_despues_de_firma(p: pd.DataFrame) -> pd.Series:
    firma, ini = p["fecha_de_firma"].dt.normalize(), p["fecha_de_inicio_del_contrato"].dt.normalize()
    tolerancia = pd.Timedelta(days=PARAMETROS["tolerancia_inicio_antes_firma_dias"])
    return _resultado(ini >= firma - tolerancia, firma.notna() & ini.notna())


def no_supera_valor(columna: str) -> Callable[[pd.DataFrame], pd.Series]:
    return lambda p: _resultado(p[columna] <= p["valor_del_contrato"],
                                p[columna].notna() & p["valor_del_contrato"].notna())


def cerrado_con_fin_pasado(p: pd.DataFrame) -> pd.Series:
    cerrado = p["estado_contrato"].str.lower().isin(["cerrado", "terminado"])
    return _resultado(p["fecha_de_fin_del_contrato"] <= FECHA_CORTE,
                      cerrado & p["fecha_de_fin_del_contrato"].notna())


def duracion_coherente(p: pd.DataFrame) -> pd.Series:
    """La fuente no siempre corre la fecha de fin con las prórrogas: se aceptan ambas lecturas."""
    por_fechas = (p["fecha_de_fin_del_contrato"] - p["fecha_de_inicio_del_contrato"]).dt.days
    declarada = p["duracion_declarada_dias"]
    con_prorroga = declarada + p["dias_adicionados"].fillna(0)
    tol = PARAMETROS["tolerancia_duracion_dias"]
    cumple = ((por_fechas - declarada).abs() <= tol) | ((por_fechas - con_prorroga).abs() <= tol)
    return _resultado(cumple, por_fechas.notna() & declarada.notna())


def id_unico(p: pd.DataFrame) -> pd.Series:
    return _resultado(~p["id_contrato"].duplicated(keep=False))


def sin_duplicado_negocio(p: pd.DataFrame) -> pd.Series:
    llave = ["nit_entidad", "referencia_del_contrato", "documento_proveedor", "valor_del_contrato"]
    return _resultado(~p.duplicated(llave, keep=False), p[llave].notna().all(axis=1))


def valor_no_atipico(p: pd.DataFrame) -> pd.Series:
    log_valor = np.log10(p["valor_del_contrato"].where(p["valor_del_contrato"] > 0))
    grupo = log_valor.groupby(p["tipo_de_contrato"])
    q1, q3 = grupo.transform("quantile", 0.25), grupo.transform("quantile", 0.75)
    limite = q3 + PARAMETROS["k_iqr_atipicos"] * (q3 - q1)
    return _resultado(log_valor <= limite, log_valor.notna())


def modificado_con_fecha(p: pd.DataFrame) -> pd.Series:
    """`ultima_actualizacion` solo se llena cuando hay una modificación, no en cada carga."""
    return _resultado(p["ultima_actualizacion"].notna(), p["estado_contrato"] == "Modificado")


def estado_al_dia(p: pd.DataFrame) -> pd.Series:
    """Un contrato "En ejecución" cuya fecha de fin ya pasó tiene el estado desactualizado."""
    en_ejecucion = p["estado_contrato"] == "En ejecución"
    vencido_hace = (FECHA_CORTE - p["fecha_de_fin_del_contrato"]).dt.days
    return _resultado(vencido_hace <= PARAMETROS["dias_gracia_estado_vencido"],
                      en_ejecucion & p["fecha_de_fin_del_contrato"].notna())


def proveedor_no_menor(p: pd.DataFrame) -> pd.Series:
    return _resultado(p["tipodocproveedor"] != "Tarjeta de Identidad", p["tipodocproveedor"].notna())


REGLAS = [
    Regla("COMP-01", "Completitud", "Fecha de firma informada", "alta", completitud("fecha_de_firma")),
    Regla("COMP-02", "Completitud", "Fecha de inicio informada", "alta", completitud("fecha_de_inicio_del_contrato")),
    Regla("COMP-03", "Completitud", "Fecha de fin informada", "alta", completitud("fecha_de_fin_del_contrato")),
    Regla("COMP-04", "Completitud", "Tipo de documento del proveedor informado", "alta", completitud("tipodocproveedor")),
    Regla("COMP-05", "Completitud", "Documento del proveedor informado", "alta", completitud("documento_proveedor")),
    Regla("COMP-06", "Completitud", "Objeto del contrato informado", "alta", completitud("objeto_del_contrato")),
    Regla("COMP-07", "Completitud", "Departamento informado", "media", completitud("departamento")),
    Regla("COMP-08", "Completitud", "Ciudad informada", "media", completitud("ciudad")),
    Regla("COMP-09", "Completitud", "Supervisor del contrato informado", "media",
          lambda p: _resultado(p["n_mero_de_documento_supervisor_informado"])),
    Regla("COMP-10", "Completitud", "Contrato modificado con fecha de la modificación", "media", modificado_con_fecha),
    Regla("VAL-01", "Validez", "Documento del proveedor con formato válido para su tipo (CC 6-10 dígitos, NIT 9-10)", "alta", documento_valido),
    Regla("VAL-02", "Validez", "Valor del contrato no es de relleno (≥ valor mínimo, salvo comodato)", "alta", valor_plausible_minimo),
    Regla("VAL-03", "Validez", "Estado del contrato en forma canónica (mayúscula inicial)", "baja", forma_canonica("estado_contrato")),
    Regla("VAL-04", "Validez", "Sector en forma canónica (mayúscula inicial)", "baja", forma_canonica("sector")),
    Regla("CONS-01", "Consistencia", "Fecha de fin no anterior a la de inicio", "alta", fin_despues_de_inicio),
    Regla("CONS-02", "Consistencia", "Inicio no anterior a la firma", "media", inicio_despues_de_firma),
    Regla("CONS-03", "Consistencia", "Valor pagado no supera el valor del contrato", "alta", no_supera_valor("valor_pagado")),
    Regla("CONS-04", "Consistencia", "Valor facturado no supera el valor del contrato", "alta", no_supera_valor("valor_facturado")),
    Regla("CONS-05", "Consistencia", "Contrato cerrado o terminado con fecha de fin ya cumplida", "media", cerrado_con_fin_pasado),
    Regla("CONS-06", "Consistencia", "Duración declarada (más días adicionados) coherente con las fechas", "baja", duracion_coherente),
    Regla("UNI-01", "Unicidad", "id_contrato único", "alta", id_unico),
    Regla("UNI-02", "Unicidad", "Sin duplicado de negocio (entidad, referencia, proveedor, valor)", "media", sin_duplicado_negocio),
    Regla("EXA-01", "Exactitud", "Valor no atípico para su tipo de contrato (aproximación a exactitud)", "baja", valor_no_atipico),
    Regla("OPO-01", "Oportunidad", "Estado al día: no sigue \"En ejecución\" meses después de su fecha de fin", "media", estado_al_dia),
    Regla("NEG-01", "Validez", "Proveedor no identificado con Tarjeta de Identidad (menor de edad)", "alta", proveedor_no_menor),
]


# --- Ejecución ---------------------------------------------------------------

def evaluar(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (matriz contrato × regla, resumen por regla)."""
    p = preparar(df)
    matriz = pd.DataFrame({r.id: r.evaluar(p) for r in REGLAS}, index=df.index)
    filas = []
    for r in REGLAS:
        res = matriz[r.id]
        aplicables, cumplen = int(res.notna().sum()), int(res.sum())
        pct = cumplen / aplicables * 100 if aplicables else np.nan
        meta = METAS[r.criticidad]
        filas.append({
            "id": r.id, "dimension": r.dimension, "descripcion": r.descripcion,
            "criticidad": r.criticidad, "aplicables": aplicables,
            "incumplen": aplicables - cumplen, "cumplimiento_%": round(pct, 2),
            "meta_%": meta, "estado": "cumple" if pct >= meta else "no cumple",
        })
    return matriz, pd.DataFrame(filas)


if __name__ == "__main__":
    _, resumen = evaluar(pd.read_parquet(SNAPSHOT))
    destino = RAIZ / "outputs" / "02_resultado_reglas.csv"
    resumen.to_csv(destino, index=False)
    with pd.option_context("display.max_colwidth", 60, "display.width", 200):
        print(resumen.drop(columns="descripcion").to_string(index=False))
    print(f"\nGuardado en {destino.relative_to(RAIZ)}")
