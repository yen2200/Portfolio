# Energy demand forecasting in Colombia: ARIMAX and SARIMAX

[English](#english) · [Español](#español)

---

## English

**TL;DR.** I forecast Colombia's daily electricity demand with ARIMAX and SARIMAX using population and temperature from ten departments as external variables. SARIMAX with weekly seasonality gives the best result on the 2018–2023 test period: R² 0.56 and MAPE 4.5 %. Plain ARIMAX does not capture the weekly cycle (R² −0.21).

This is my part of a team master's thesis. Teammates built the Random Forest and LSTM models in the [team repository](https://github.com/adeulofeu/TFM); I built the ARIMAX and SARIMAX models and their diagnostics.

### Data

- Daily national electricity demand (SIN), 2007-01-01 to 2023-12-31: 6,208 records.
- External variables: population and temperature for ten departments (Bogotá, Antioquia, Valle del Cauca, Atlántico, Bolívar, Cundinamarca, Norte de Santander, Santander, Cesar, Meta).
- Source and licence: [to complete: original sources and licence of each series].
- Missing values in unserved demand, exports and imports were filled with the yearly mean; the series was forced to daily frequency with forward fill.

### Approach

1. Exploratory analysis and stationarity check (ADF test): the series is not stationary, so d = 1.
2. Multicollinearity check (VIF below 2 for all external variables).
3. ACF/PACF and a grid search over (p, d, q) comparing AIC, BIC and train and test errors. Selected ARIMAX(1,1,2).
4. Transformations tested on ARIMAX: log and standard scaling.
5. The ACF of the residuals shows a 7-day cycle, so I fitted SARIMAX(1,1,2)(1,1,1,7).
6. Train: 2007–2017 (4,018 days). Test: 2018–2023 (2,191 days).

### Results (test period, 2018–2023)

| Model | Test R² | Test RMSE (% of mean demand) | Test MAE (% of mean demand) |
|-------|---------|------------------------------|-----------------------------|
| ARIMAX(1,1,2) | −0.21 | 8.88 % | 7.62 % |
| ARIMAX(1,1,2), log | −96.10 | 79.39 % | 77.10 % |
| ARIMAX(1,1,2), standard scaling | −4.59 | 21.70 % | 18.97 % |
| **SARIMAX(1,1,2)(1,1,1,7)** | **0.56** | **6.08 %** | **5.01 %** |

SARIMAX test MAPE: 4.48 % (train: 2.35 %).

![Actual vs predicted demand](./results/sarimax_real_vs_prediccion.png)
<!-- To add: export the SARIMAX plot from the notebook and save it at this path. -->

### Limitations

- The test is a single forecast over 2,191 consecutive days. The thesis goal is short-term demand, so a rolling evaluation at 1 and 7 days ahead is still pending and would be the fairer measure.
- The external variables in the test period are observed values. In real use, temperature and population would also need to be forecast.
- The log and scaled ARIMAX results should not be read as proof that those transformations hurt the model. The log fit reported a convergence warning, and scaling should not change an ARIMA in theory, so these numbers probably reflect optimisation problems.
- Residuals are not normally distributed (Jarque–Bera test, p < 0.05), including for SARIMAX.

### Reproduce

- Python 3.11, pandas 2.2.2, scikit-learn 1.6.1, statsmodels 0.14.4.
- Notebook: [`ARIMAX_model.ipynb`](./ARIMAX_model.ipynb).
- Data: [`data/dataset_modelos.csv`](./data/dataset_modelos.csv) [to do: copy the file here and change the notebook URL].

### Next steps

Rolling evaluation at 1 and 7 days, forecasting the external variables, and comparing against the Random Forest and LSTM models from the team repository on the same test protocol.

---

## Español

**Resumen.** Pronostiqué la demanda diaria de electricidad en Colombia con ARIMAX y SARIMAX, usando población y temperatura de diez departamentos como variables externas. SARIMAX con estacionalidad semanal da el mejor resultado en el periodo de prueba 2018–2023: R² de 0,56 y MAPE de 4,5 %. El ARIMAX simple no captura el ciclo semanal (R² −0,21).

Esta es mi parte de un TFM en equipo. Mis compañeros construyeron los modelos de Random Forest y LSTM en el [repositorio del equipo](https://github.com/adeulofeu/TFM); yo construí los modelos ARIMAX y SARIMAX y sus diagnósticos.

### Datos

- Demanda nacional diaria de electricidad (SIN), del 2007-01-01 al 2023-12-31: 6.208 registros.
- Variables externas: población y temperatura de diez departamentos (Bogotá, Antioquia, Valle del Cauca, Atlántico, Bolívar, Cundinamarca, Norte de Santander, Santander, Cesar, Meta).
- Fuente y licencia: [por completar: fuentes originales y licencia de cada serie].
- Los nulos de demanda no atendida, exportaciones e importaciones se rellenaron con el promedio anual; la serie se llevó a frecuencia diaria con relleno hacia adelante.

### Enfoque

1. Análisis exploratorio y prueba de estacionariedad (ADF): la serie no es estacionaria, por eso d = 1.
2. Revisión de multicolinealidad (VIF menor a 2 en todas las variables externas).
3. ACF/PACF y búsqueda de (p, d, q) comparando AIC, BIC y errores en entrenamiento y prueba. Se eligió ARIMAX(1,1,2).
4. Transformaciones probadas en ARIMAX: logarítmica y escalamiento estándar.
5. La ACF de los residuos muestra un ciclo de 7 días, así que ajusté SARIMAX(1,1,2)(1,1,1,7).
6. Entrenamiento: 2007–2017 (4.018 días). Prueba: 2018–2023 (2.191 días).

### Resultados (periodo de prueba, 2018–2023)

| Modelo | R² prueba | RMSE prueba (% de la media) | MAE prueba (% de la media) |
|--------|-----------|-----------------------------|----------------------------|
| ARIMAX(1,1,2) | −0,21 | 8,88 % | 7,62 % |
| ARIMAX(1,1,2), logarítmico | −96,10 | 79,39 % | 77,10 % |
| ARIMAX(1,1,2), escalamiento estándar | −4,59 | 21,70 % | 18,97 % |
| **SARIMAX(1,1,2)(1,1,1,7)** | **0,56** | **6,08 %** | **5,01 %** |

MAPE de prueba del SARIMAX: 4,48 % (entrenamiento: 2,35 %).

### Limitaciones

- La prueba es un único pronóstico de 2.191 días seguidos. El objetivo del TFM es la demanda a corto plazo, así que falta una evaluación con reajuste periódico a 1 y 7 días, que sería la medida más justa.
- Las variables externas del periodo de prueba son valores observados. En un uso real habría que pronosticar también la temperatura y la población.
- Los resultados del ARIMAX logarítmico y escalado no demuestran que esas transformaciones empeoren el modelo. El ajuste logarítmico reportó una advertencia de convergencia y, en teoría, escalar no cambia un ARIMA, así que esas cifras probablemente reflejan problemas de optimización.
- Los residuos no son normales (prueba de Jarque–Bera, p < 0,05), tampoco en SARIMAX.

### Reproducir

- Python 3.11, pandas 2.2.2, scikit-learn 1.6.1, statsmodels 0.14.4.
- Notebook: [`ARIMAX_model.ipynb`](./ARIMAX_model.ipynb).
- Datos: [`data/dataset_modelos.csv`](./data/dataset_modelos.csv) [pendiente: copiar el archivo aquí y cambiar la URL del notebook].

### Próximos pasos

Evaluación con reajuste a 1 y 7 días, pronóstico de las variables externas y comparación con los modelos de Random Forest y LSTM del repositorio del equipo bajo el mismo protocolo de prueba.
