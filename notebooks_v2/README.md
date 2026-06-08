# Vermont Early Warning System (V-EWS)

Sistema de alerta temprana académica para estudiantes de Middle School — Vermont School Medellín.

Proyecto Integrador 1 · Maestría en Ciencia de Datos y Analítica · EAFIT 2026-1

**Dashboard:** [vmt-ews-acad.streamlit.app](https://vmt-ews-acad.streamlit.app)

---

## Descripción

V-EWS predice riesgo académico en T3 antes de que finalice el año escolar, combinando un clasificador Random Forest, un regresor multi-output y clustering K-Means sobre datos de notas, asistencia y convivencia de ~149 estudiantes de grados 7.°, 8.° y 9.°.

El sistema entrena con datos históricos 2024-25 y aplica los modelos sobre 2025-26, cruzando la predicción con notas parciales de T3 para generar alertas accionables por estudiante.

---

## Arquitectura del datalake

Implementado en Databricks Free Edition sobre Unity Catalog Volumes:

| Capa | Ruta | Contenido |
|---|---|---|
| Bronze | `bronze/raw/{año}/` | XLS originales Phidias |
| Bronze | `bronze/anon/{año}/` | Datos anonimizados CSV |
| Bronze | `bronze/prepared/` | Parquet con asignaturas unificadas |
| Trusted | `trusted/train_dataset/` | Features 2024-25 + target |
| Trusted | `trusted/predict_dataset/` | Features 2025-26 + T3 parcial |
| Silver | `silver/models/` | Modelos persistidos |
| Silver | `silver/early_alerts_v2/` | Alertas con categorías |
| Gold | `dashboard_data.csv` | Exportación para Streamlit |
| Privado | `privado/` | Tabla de mapeo real — nunca sale de Databricks |

---

## Notebooks

| Notebook | Descripción |
|---|---|
| `00_anonymizer` | Anonimización SHA-256 — genera códigos SN-XXX y tabla de mapeo privada |
| `01_bronze_preparation` | Ingesta y unificación de asignaturas por área en Parquet |
| `02_trusted_features` | Feature engineering — T1+T2 como predictores, risk\_level como target |
| `02b_eda_sql` | EDA con SparkSQL — solo lectura, sin modificar Silver |
| `03_predictive_model` | Entrenamiento completo con comparativa de modelos |
| `03_predictive_model_v2` | Versión de producción — umbral 0,30, clustering K=3 |
| `03_apply_model` | Aplicación sin reentrenamiento — usado por el Workflow |
| `04_early_alert` | Categorías de alerta → Silver → Gold |

> ⚠️ El notebook de desanonimización no se incluye por contener lógica que accede a nombres reales de menores de edad.

---

## Modelos

| Componente | Algoritmo | Métrica clave |
|---|---|---|
| Clasificación | Random Forest (umbral=0,30) | Recall crítico=0,889 · AUC=0,913 |
| Regresión T3 | RF Multi-output (150 árboles) | MAE=0,642 · R²=0,238 |
| Clustering | K-Means K=3 | Silhouette=0,251 |

---

## Categorías de alerta

| Categoría | Condición | Acción |
|---|---|---|
| 🔴 Riesgo Confirmado | Modelo detecta riesgo + T3 confirma ≥3 materias bajo 4,0 | Intervención urgente |
| 🟠 Punto Ciego | T3 muestra riesgo pero modelo no lo detectó | Revisar con urgencia |
| 🔵 Riesgo Teórico | Modelo detecta riesgo pero T3 aún no confirma | Monitoreo activo |
| 🟢 Sin Riesgo | Sin señales en modelo ni en T3 | Seguimiento rutinario |

---

## Agrupamiento de asignaturas

Para garantizar comparabilidad entre años con cambios curriculares:

| Grupo | Asignaturas incluidas |
|---|---|
| Science | Integrated Science, Life Science, Physical Science, Biology |
| I&S | Individuals and Societies, Ciencias Políticas |
| Mathematics | Mathematics |
| English | English |
| Lengua Castellana | Lengua Castellana |
| Mandarin | Mandarín |
| Financial Maths | Financial Maths |
| ICT/STEM | ICT/STEM |
| Physical Education | Educación Física |
| Research Methodology | Research Methodology |

---

## Privacidad

Los datos contienen información de menores de edad y no se publican en este repositorio. El pipeline implementa anonimización completa: códigos SN-XXX como IDs, secciones recodificadas aleatoriamente, docentes como P01–P20. La tabla de mapeo real se mantiene exclusivamente en `/privado/` en Databricks.

Para reproducir con datos propios: subir XLS al volume `bronze/raw/` y ejecutar notebooks en orden.

---

## Trabajo futuro

1. Features históricas individuales: `prev_year_risk_level`, `prev_year_avg`, `is_repeating_grade`
2. Efecto docente: ajuste por severidad en registros F1
3. MLOps: automatización con Databricks Jobs/Workflows
4. Dashboard operacional con nombres reales y filtros por sección
5. Integrar datos 2023-24 con normalización de escala 1-10 → 1-7
6. Escalabilidad: replicar en otros colegios de la red Cognita

---

## Autor

Andrés Felipe Velasco Hernández  
Director Académico Middle School · Vermont School Medellín  
Maestría en Ciencia de Datos y Analítica · EAFIT 2026-1
