"""Pruebas de las reglas con contratos de juguete: cada caso fija un cumple, un no cumple y un no aplica."""

import sys
import pathlib

import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import reglas_dq as r  # noqa: E402


def contratos(**columnas) -> pd.DataFrame:
    """Un DataFrame con todas las columnas que usan las reglas; las no dadas quedan en blanco."""
    n = len(next(iter(columnas.values())))
    base = {c: [""] * n for c in [
        "fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato",
        "ultima_actualizacion", "valor_del_contrato", "valor_pagado", "valor_facturado",
        "dias_adicionados", "duraci_n_del_contrato", "tipodocproveedor", "documento_proveedor",
        "tipo_de_contrato", "estado_contrato", "id_contrato",
    ]}
    base.update(columnas)
    df = pd.DataFrame(base).astype("string")
    for c, v in columnas.items():
        if not isinstance(v[0], str):
            df[c] = v
    return df


def evaluar(regla_id: str, df: pd.DataFrame) -> list:
    regla = next(x for x in r.REGLAS if x.id == regla_id)
    return [None if pd.isna(v) else bool(v) for v in regla.evaluar(r.preparar(df))]


def test_nulo_disfrazado_cuenta_como_faltante():
    df = contratos(fecha_de_firma=["2024-01-01", "No definido", ""])
    assert evaluar("COMP-01", df) == [True, False, False]


def test_documento_valido_segun_tipo():
    df = contratos(
        tipodocproveedor=["Cédula de Ciudadanía", "Cédula de Ciudadanía", "NIT", "Pasaporte"],
        documento_proveedor=["x", "x", "x", "x"],
        documento_proveedor_longitud=[10, 12, 9, 8],
        documento_proveedor_solo_digitos=[True, True, True, False],
    )
    assert evaluar("VAL-01", df) == [True, False, True, None]


def test_valor_de_relleno_salvo_comodato():
    df = contratos(valor_del_contrato=["1", "5000000", "0"],
                   tipo_de_contrato=["Obra", "Obra", "Comodato"])
    assert evaluar("VAL-02", df) == [False, True, None]


def test_inicio_antes_de_firma():
    df = contratos(fecha_de_firma=["2024-03-10T15:00:00", "2024-03-10T15:00:00", ""],
                   fecha_de_inicio_del_contrato=["2024-03-10T08:00:00", "2024-03-01", "2024-03-01"])
    # Mismo día cuenta como cumple aunque la hora de inicio sea anterior.
    assert evaluar("CONS-02", df) == [True, False, None]


def test_duracion_acepta_fecha_fin_con_o_sin_prorroga():
    df = contratos(
        fecha_de_inicio_del_contrato=["2024-01-01"] * 3,
        fecha_de_fin_del_contrato=["2024-01-31", "2024-03-01", "2024-12-31"],
        duraci_n_del_contrato=["30 Dia(s)", "30 Dia(s)", "30 Dia(s)"],
        dias_adicionados=["0", "30", "0"],
    )
    assert evaluar("CONS-06", df) == [True, True, False]


def test_estado_en_ejecucion_vencido():
    df = contratos(estado_contrato=["En ejecución", "En ejecución", "Cerrado"],
                   fecha_de_fin_del_contrato=["2026-10-01", "2024-01-01", "2024-01-01"])
    assert evaluar("OPO-01", df) == [True, False, None]


@pytest.mark.parametrize("estado, esperado", [("Cerrado", True), ("terminado", False)])
def test_forma_canonica(estado, esperado):
    assert evaluar("VAL-03", contratos(estado_contrato=[estado])) == [esperado]
