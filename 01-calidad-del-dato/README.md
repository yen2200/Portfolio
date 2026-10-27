# Data quality assessment: SECOP II public contracts

[English](#english) · [Español](#español)

---

## English

**Status: in progress.** This README describes the plan. Results will be added as each phase is finished.

**Goal.** Measure the quality of a real, messy public dataset across standard data quality dimensions, combine the results into a DQ Score, and propose a phased improvement plan, the same way a data quality programme would run inside an organisation.

### Data

- **Source:** [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h) (dataset `jbjy-vk9h`), published by Colombia Compra Eficiente on datos.gov.co.
- **Licence:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Any data derived from it in this folder is shared under the same licence.
- **Size:** about 5.7 million contracts and 95 columns. The analysis uses a fixed snapshot so the results can be reproduced (see below).

### Approach

| Phase | Output | Content |
|---|---|---|
| 1. Profiling | `notebooks/01_perfilado.ipynb` | Types, nulls, cardinality, ranges and distributions |
| 2. Rules by dimension | `src/` | Completeness, uniqueness, validity, consistency, accuracy and timeliness rules |
| 3. DQ Score | `notebooks/02_dq_score.ipynb` | Score per rule, per dimension and overall, with weights and thresholds |
| 4. Improvement plan | This README | Quick wins, medium-term and structural actions with target KPIs |

### Reproduce

```bash
python src/descargar_snapshot.py --filas 100000
```

---

## Español

**Estado: en curso.** Este README describe el plan. Los resultados se agregan al cerrar cada fase.

**Objetivo.** Medir la calidad de un dataset público real y desordenado según las dimensiones estándar de calidad del dato, consolidar el resultado en un DQ Score y proponer un plan de mejora por fases, como se haría en un programa de calidad del dato dentro de una organización.

### Datos

- **Fuente:** [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h) (dataset `jbjy-vk9h`), publicado por Colombia Compra Eficiente en datos.gov.co.
- **Licencia:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Los datos derivados en esta carpeta se comparten bajo la misma licencia.
- **Tamaño:** cerca de 5,7 millones de contratos y 95 columnas. El análisis usa un snapshot fijo para que los resultados sean reproducibles (ver abajo).

### Enfoque

| Fase | Entregable | Contenido |
|---|---|---|
| 1. Perfilado | `notebooks/01_perfilado.ipynb` | Tipos, nulos, cardinalidad, rangos y distribuciones |
| 2. Reglas por dimensión | `src/` | Reglas de completitud, unicidad, validez, consistencia, exactitud y oportunidad |
| 3. DQ Score | `notebooks/02_dq_score.ipynb` | Puntaje por regla, por dimensión y global, con pesos y umbrales |
| 4. Plan de mejora | Este README | Acciones rápidas, de mediano plazo y estructurales, con KPI objetivo |

### Reproducir

```bash
python src/descargar_snapshot.py --filas 100000
```
