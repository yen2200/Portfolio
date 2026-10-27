# Data quality assessment: SECOP II public contracts

[English](#english) · [Español](#español)

---

## English

**Status: in progress.** This README describes the plan. Results will be added as each phase is finished.

**Goal.** Measure the quality of a real, messy public dataset across standard data quality dimensions, combine the results into a DQ Score, and propose a phased improvement plan, the same way a data quality programme would run inside an organisation.

### Data

- **Source:** [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h) (dataset `jbjy-vk9h`), published by Colombia Compra Eficiente on datos.gov.co.
- **Licence:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Any data derived from it in this folder is shared under the same licence.
- **Size:** about 5.7 million contracts and 95 columns.
- **Snapshot:** `data/secop2_contratos_2026-10-27_50000.parquet`, 50,000 contracts downloaded on 27 Oct 2026. The source reloads the whole dataset every day (every row gets a new internal id and contract values keep changing), so the API cannot return the same sample twice. The frozen Parquet is what makes the results reproducible; `id_contrato` lets you look up the same contracts again later.
- **Personal data:** 18 columns about people (legal representative, spending and payment officers, supervisor, bank account) are replaced by a `<column>_informado` true/false flag. When the supplier is a person rather than a company (85% of the sample), the name is removed and the ID number is replaced by a pseudonym (salted HMAC), keeping its length and whether it is digits only. Free-text fields such as `objeto_del_contrato` are kept as published and may still mention names.

### Approach

| Phase | Output | Content |
|---|---|---|
| 1. Profiling | `notebooks/01_perfilado.ipynb` | Types, nulls, cardinality, ranges and distributions |
| 2. Rules by dimension | `src/` | Completeness, uniqueness, validity, consistency, accuracy and timeliness rules |
| 3. DQ Score | `notebooks/02_dq_score.ipynb` | Score per rule, per dimension and overall, with weights and thresholds |
| 4. Improvement plan | This README | Quick wins, medium-term and structural actions with target KPIs |

### Reproduce

The analysis reads the Parquet in `data/`. To build a new snapshot from the live source:

```bash
pip install pandas pyarrow
python src/descargar_snapshot.py --filas 50000
python src/construir_parquet.py data/secop2_contratos_<fecha>_50000.csv
```

---

## Español

**Estado: en curso.** Este README describe el plan. Los resultados se agregan al cerrar cada fase.

**Objetivo.** Medir la calidad de un dataset público real y desordenado según las dimensiones estándar de calidad del dato, consolidar el resultado en un DQ Score y proponer un plan de mejora por fases, como se haría en un programa de calidad del dato dentro de una organización.

### Datos

- **Fuente:** [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h) (dataset `jbjy-vk9h`), publicado por Colombia Compra Eficiente en datos.gov.co.
- **Licencia:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Los datos derivados en esta carpeta se comparten bajo la misma licencia.
- **Tamaño:** cerca de 5,7 millones de contratos y 95 columnas.
- **Snapshot:** `data/secop2_contratos_2026-10-27_50000.parquet`, 50.000 contratos descargados el 27 de octubre de 2026. La fuente recarga el dataset completo cada día (cada fila recibe un id interno nuevo y los valores de los contratos siguen cambiando), así que la API no puede devolver dos veces la misma muestra. El Parquet congelado es lo que hace reproducibles los resultados; `id_contrato` permite volver a consultar los mismos contratos más adelante.
- **Datos personales:** 18 columnas sobre personas (representante legal, ordenadores del gasto y del pago, supervisor, cuenta bancaria) se reemplazan por una bandera `<columna>_informado` verdadero/falso. Cuando el proveedor es una persona y no una empresa (85 % de la muestra), se elimina el nombre y el documento se reemplaza por un seudónimo (HMAC con sal), conservando su longitud y si es solo dígitos. Los campos de texto libre como `objeto_del_contrato` se dejan como se publicaron y pueden mencionar nombres.

### Enfoque

| Fase | Entregable | Contenido |
|---|---|---|
| 1. Perfilado | `notebooks/01_perfilado.ipynb` | Tipos, nulos, cardinalidad, rangos y distribuciones |
| 2. Reglas por dimensión | `src/` | Reglas de completitud, unicidad, validez, consistencia, exactitud y oportunidad |
| 3. DQ Score | `notebooks/02_dq_score.ipynb` | Puntaje por regla, por dimensión y global, con pesos y umbrales |
| 4. Plan de mejora | Este README | Acciones rápidas, de mediano plazo y estructurales, con KPI objetivo |

### Reproducir

El análisis lee el Parquet de `data/`. Para generar un snapshot nuevo desde la fuente:

```bash
pip install pandas pyarrow
python src/descargar_snapshot.py --filas 50000
python src/construir_parquet.py data/secop2_contratos_<fecha>_50000.csv
```
