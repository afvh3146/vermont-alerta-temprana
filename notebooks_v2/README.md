# Vermont School — Early Warning System V2
## Sistema de Alerta Temprana — Middle School

**SI7006/SI6003 — Almacenamiento y Procesamiento de Grandes Datos**  
Universidad EAFIT — Maestría en Ciencia de Datos y Analítica — 2026-1  
**Autor**: Andrés Felipe Velasco Hernández | CC 1107070713

---

## Descripción

Sistema de alerta temprana para estudiantes de Middle School (7°, 8° y 9°) del Vermont School (Medellín). El sistema entrena un modelo predictivo con datos históricos del año lectivo 2024-25 y lo aplica sobre el año en curso (2025-26), cruzando la predicción con notas parciales del tercer trimestre para generar alertas accionables por sección.

---

## Arquitectura del datalake

Implementado en **Databricks Free Edition** sobre Unity Catalog:

    /Volumes/workspace/vermont/
    ├── bronze/
    │   ├── raw/24_25/           ← XLS originales 2024-25
    │   ├── raw/25_26/           ← XLS originales 2025-26
    │   ├── anon/24_25/          ← Datos anonimizados (CSV)
    │   ├── anon/25_26/          ← Datos anonimizados (CSV)
    │   └── prepared/            ← Parquet con asignaturas unificadas
    ├── trusted/
    │   ├── train_dataset/       ← 24-25: T1+T2 features + risk_level target
    │   └── predict_dataset/     ← 25-26: T1+T2 features + T3 parcial
    ├── silver/
    │   ├── eda_*/               ← Resultados EDA con SparkSQL
    │   ├── early_warning_model/ ← Modelo Random Forest entrenado
    │   ├── predictions_25_26/   ← Predicciones sobre año actual
    │   └── early_alerts_25_26/  ← Alertas finales con categorías
    └── privado/                 ← Tabla de mapeo real (nunca sale de Databricks)

---

## Notebooks

| Notebook | Descripción |
|---|---|
| `00_anonymizer` | Anonimiza datos reales → códigos de matrícula. Genera tabla de mapeo privada |
| `01_bronze_preparation` | Agrupa asignaturas por área (Science, I&S) y prepara datos por año en Parquet |
| `02_trusted_features` | Feature engineering — T1+T2 como predictores, risk_level como target |
| `02b_eda_sql` | EDA con SparkSQL — 5 queries + visualizaciones matplotlib |
| `03_predictive_model` | Random Forest con 5-Fold CV entrenado en 24-25, predicción sobre 25-26 |
| `04_early_alert` | Sistema de alertas: predicción + T3 parcial → 6 categorías de alerta |

> ⚠️ El notebook `00_deanonymizer` no se incluye en este repositorio por contener lógica que accede a nombres reales de estudiantes menores de edad.

---

## Pipeline

    XLS Phidias → 00_anonymizer → 01_bronze → 02_trusted → 02b_EDA → 03_model → 04_alerts

---

## Agrupamiento de asignaturas

Para garantizar comparabilidad entre años lectivos con cambios curriculares:

| Grupo | Asignaturas incluidas |
|---|---|
| Science | Integrated Science, Life Science, Physical Science, Biology, Chemistry, Physics |
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

## Modelo

- **Algoritmo**: Random Forest Classifier (SparkML)
- **Entrenamiento**: Datos 2024-25 con T1+T2 como features y nivel de riesgo final como target
- **Evaluación**: 5-Fold Cross-Validation con class weights para balanceo
- **F1-Score (CV)**: 0.7541
- **Predicción**: Aplicado sobre datos 2025-26

---

## Categorías de alerta

| Categoría | Descripción |
|---|---|
| 🔴 CONFIRMED_CRITICAL | Modelo predice crítico + T3 parcial confirma riesgo |
| 🟠 DETERIORATING | Modelo predice recuperación pero T3 muestra deterioro |
| 🟠 RECOVERING | Modelo predice crítico pero T3 muestra mejora |
| 🟡 RECOVERY_ALERT | Modelo predice recuperación + T3 confirma 1-2 materias en riesgo |
| 🔵 MONITOR | Predicción incierta (confianza < 50%) — requiere seguimiento |
| 🟢 ON_TRACK | Sin señales de riesgo |

---

## Resultados 2025-26

| Alerta | Estudiantes |
|---|---|
| 🔴 Confirmed Critical | 15 |
| 🟠 Deteriorating | 3 |
| 🟠 Recovering | 5 |
| 🟡 Recovery Alert | 33 |
| 🔵 Monitor | 5 |
| 🟢 On Track | 88 |
| **Total** | **149** |

---

## Privacidad y anonimización

- Los datos contienen información de menores de edad y **no se publican** en este repositorio
- El pipeline implementa anonimización completa: códigos de matrícula como IDs, secciones recodificadas aleatoriamente, docentes como P01-P20
- La tabla de mapeo real se mantiene exclusivamente en el volume `/privado/` de Databricks
- Para reproducir con datos propios: subir XLS al volume `bronze/raw/` y ejecutar notebooks en orden

---

## Datos

El archivo `datos_anonimizados.zip` contiene los datos de entrada del pipeline, anonimizados por `00_anonymizer`:

    datos_anonimizados.zip
    ├── 24_25/
    │   ├── notas_7A.csv ... notas_9B.csv  ← Notas por sección
    │   ├── asistencia.csv                  ← Asistencia consolidada
    │   └── convivencia.csv                 ← Seguimientos F1 y F2
    └── 25_26/
        ├── notas_7A.csv ... notas_9B.csv
        ├── asistencia.csv
        ├── convivencia_tipo1.csv           ← Seguimientos F1
        └── convivencia_tipo2.csv           ← Seguimientos F2

Para reproducir: descomprime el ZIP, sube los archivos al volume `bronze/anon/` en Databricks y ejecuta los notebooks en orden desde `01_bronze_preparation`.

---

## Trabajo futuro

1. **Features históricas individuales**: prev_year_risk_level, prev_year_avg, is_repeating_grade
2. **Efecto docente**: ajuste por severidad del docente en registro de F1
3. **MLOps**: automatización con Databricks Jobs/Workflows
4. **Dashboard interactivo**: con nombres reales, filtros por sección y actualización automática
5. **Datos 2023-24**: incorporar año adicional de entrenamiento con normalización de escala
6. **Escalabilidad Redcol**: extender pipeline a otros colegios de la red
