# Regression models: predicting exam scores (practice exercise)

[English](#english) · [Español](#español)

---

## English

**TL;DR.** A practice exercise comparing regression models to predict a student's exam score from study hours, sleep, attendance and previous scores. With only 200 rows, simple linear models win: Linear and Ridge regression reach R² 0.85 on the test set, ahead of Random Forest (0.80) and Decision Tree (0.58).

Note: the notebook file name comes from an earlier draft of the exercise and will be renamed.

### Data

- Kaggle dataset [`student-exam-scores-dataset`](https://www.kaggle.com/datasets/mirzayasirabdullah07/student-exam-scores-dataset) (author: mirzayasirabdullah07). Check the dataset page for its licence and origin.
- 200 rows, no missing values, no duplicates.
- Target: `exam_score`. Predictors: `hours_studied`, `sleep_hours`, `attendance_percent`, `previous_scores`.

### Approach

1. Exploratory analysis: distributions, correlation heatmap and boxplots.
2. Standard scaling of the predictors.
3. 80/20 train/test split (160 / 40 rows, `random_state=42`).
4. Seven regression models attempted (six reported, see limitations), compared on R², MAE, RMSE and training time.

### Results (test set, 40 rows)

| Model | R² | MAE | RMSE |
|-------|----|-----|------|
| Linear Regression | 0.85 | 2.32 | 2.80 |
| Ridge Regression | 0.85 | 2.33 | 2.80 |
| Polynomial Regression (degree 2) | 0.82 | 2.63 | 3.11 |
| Random Forest | 0.80 | 2.92 | 3.27 |
| Lasso Regression (alpha = 1) | 0.75 | 3.28 | 3.68 |
| Decision Tree (max depth 17) | 0.58 | 4.01 | 4.72 |

### Known limitations

These are open items I plan to fix; I list them so the results are read with the right caution.

- **Support Vector Regression is not reported.** The SVR model was defined but the wrong object was trained, so its row was a duplicate of the Random Forest. It was removed from the table above.
- **`student_id` is used as a predictor** after stripping its prefix. An identifier should not be a feature.
- **Scaling is applied before the train/test split**, which leaks a little information from the test set.
- **One split of 40 test rows, no cross-validation and no hyperparameter tuning.** Differences of a few points of R² between models may be noise.
- The dataset is small and looks like a teaching dataset, so conclusions do not transfer to real student data.

### Reproduce

Open [`Modelos_de_Regresión_Ventas_Carros.ipynb`](./Modelos_de_Regresi%C3%B3n_Ventas_Carros.ipynb) in Google Colab or Jupyter. It downloads the data with `kagglehub`. Libraries: pandas, numpy, matplotlib, seaborn, scikit-learn.

---

## Español

**Resumen.** Ejercicio de práctica que compara modelos de regresión para predecir la nota de examen de un estudiante a partir de horas de estudio, sueño, asistencia y notas previas. Con solo 200 filas, ganan los modelos lineales: la regresión Lineal y la Ridge llegan a R² de 0,85 en prueba, por encima de Random Forest (0,80) y del Árbol de Decisión (0,58).

Nota: el nombre del archivo del notebook viene de un borrador anterior del ejercicio y se va a renombrar.

### Datos

- Dataset de Kaggle [`student-exam-scores-dataset`](https://www.kaggle.com/datasets/mirzayasirabdullah07/student-exam-scores-dataset) (autor: mirzayasirabdullah07). Revisa en la página del dataset su licencia y origen.
- 200 filas, sin valores nulos ni duplicados.
- Variable objetivo: `exam_score`. Predictoras: `hours_studied`, `sleep_hours`, `attendance_percent`, `previous_scores`.

### Enfoque

1. Análisis exploratorio: distribuciones, mapa de calor de correlaciones y diagramas de caja.
2. Escalamiento estándar de las variables predictoras.
3. División 80/20 en entrenamiento y prueba (160 / 40 filas, `random_state=42`).
4. Siete modelos de regresión probados (seis reportados, ver limitaciones), comparados en R², MAE, RMSE y tiempo de entrenamiento.

### Resultados (conjunto de prueba, 40 filas)

| Modelo | R² | MAE | RMSE |
|--------|----|-----|------|
| Regresión Lineal | 0,85 | 2,32 | 2,80 |
| Regresión Ridge | 0,85 | 2,33 | 2,80 |
| Regresión Polinómica (grado 2) | 0,82 | 2,63 | 3,11 |
| Random Forest | 0,80 | 2,92 | 3,27 |
| Regresión Lasso (alpha = 1) | 0,75 | 3,28 | 3,68 |
| Árbol de Decisión (profundidad máx. 17) | 0,58 | 4,01 | 4,72 |

### Limitaciones conocidas

Son pendientes que planeo corregir; los listo para que los resultados se lean con la cautela adecuada.

- **No se reporta la Regresión de Vectores de Soporte (SVR).** El modelo se definió, pero se entrenó el objeto equivocado y su fila era un duplicado del Random Forest. Se quitó de la tabla.
- **`student_id` se usa como variable predictora** después de quitarle el prefijo. Un identificador no debería ser una variable del modelo.
- **El escalamiento se aplica antes de dividir en entrenamiento y prueba**, lo que filtra un poco de información del conjunto de prueba.
- **Una sola división con 40 filas de prueba, sin validación cruzada ni ajuste de hiperparámetros.** Diferencias de pocos puntos de R² entre modelos pueden ser ruido.
- El dataset es pequeño y parece de enseñanza, así que las conclusiones no se trasladan a datos reales de estudiantes.

### Reproducir

Abre [`Modelos_de_Regresión_Ventas_Carros.ipynb`](./Modelos_de_Regresi%C3%B3n_Ventas_Carros.ipynb) en Google Colab o Jupyter. Descarga los datos con `kagglehub`. Librerías: pandas, numpy, matplotlib, seaborn, scikit-learn.
