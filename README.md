# vermont-alerta-temprana
Sistema de alerta temprana para estudiantes de Middle School - Vermont School

# Vermont School — Sistema de Alerta Temprana

**SI7006/SI6003 — Almacenamiento y Procesamiento de Grandes Datos**  
Universidad EAFIT — Maestría en Ciencia de Datos y Analítica — 2026-1  
**Autor**: Andrés Felipe Velasco Hernández

---

## Descripción del proyecto

Sistema de alerta temprana para identificar estudiantes de Middle School (7°, 8° y 9°) en riesgo de bajo rendimiento académico en el Vermont School (Medellín). El sistema procesa datos exportados del sistema de gestión académica **Phidias** y los transforma en alertas accionables para directores de grupo.

### Niveles de riesgo

| Nivel | Criterio | Consecuencia |
|-------|----------|--------------|
| 🟢 Sin riesgo | 0 asignaturas bajo 4.0 | — |
| 🟡 Riesgo recuperación | 1-2 asignaturas bajo 4.0 | Puede ir a recuperación |
| 🔴 Riesgo crítico | 3+ asignaturas bajo 4.0 | Pierde el año automáticamente |

---

## Arquitectura

Pipeline batch implementado en **Databricks** con datalake en tres zonas:

```
Phidias (XLS)
     │
     ▼
┌─────────────────────────────────────────────┐
│  BRONZE  /Volumes/workspace/vermont/bronze/ │  ← Datos originales sin modificar
└─────────────────────────────────────────────┘
     │  PySpark (Notebook 02)
     ▼
┌─────────────────────────────────────────────┐
│ TRUSTED  /Volumes/workspace/vermont/trusted/│  ← Datos limpios y anonimizados (Parquet)
└─────────────────────────────────────────────┘
     │  SparkSQL + SparkML (Notebooks 03-04)
     ▼
┌─────────────────────────────────────────────┐
│  SILVER  /Volumes/workspace/vermont/silver/ │  ← Resultados EDA + modelo + predicciones
└─────────────────────────────────────────────┘
     │  Plotly (Notebook 05)
     ▼
   Dashboard de alertas
```

---

## Estructura del repositorio

```
vermont-alerta-temprana/
├── README.md
├── notebooks/
│   ├── 01_bronze_ingesta.ipynb        # Ingesta y verificación de archivos XLS
│   ├── 02_trusted_preparacion.ipynb   # Limpieza, anonimización y Parquet
│   ├── 03_silver_eda.ipynb            # EDA con SparkSQL
│   ├── 04_silver_modelo.ipynb         # Modelo Random Forest con SparkML
│   └── 05_aplicacion_dashboard.ipynb  # Visualizaciones con Plotly
└── data/
    └── muestra_anonimizada.csv        # Muestra de 20 estudiantes anonimizados
```

> **Nota**: El notebook `06_alerta_real.ipynb` no se incluye en este repositorio por contener datos reales de estudiantes menores de edad.

---

## Datos

### Fuentes
Los datos provienen del sistema Phidias de Vermont School (exportación manual en formato XLS):

| Archivo | Contenido | Registros |
|---------|-----------|-----------|
| `report.xls` | Notas por trimestre (6 secciones) | 149 estudiantes |
| `exported.xls` | Asistencia consolidada | 149 estudiantes |
| `Consolidado_seguimiento.xls` | Seguimientos Tipo I (F1) | 943 registros |
| `Consolidado_seguimiento (1).xls` | Seguimientos Tipo II (F2) | 23 registros |

### Privacidad y anonimización
- Los datos contienen información de menores de edad y **no se publican** en este repositorio
- El pipeline implementa anonimización completa: códigos de matrícula como IDs, secciones recodificadas (G7SA/G7SB), docentes como P01-P20
- La tabla de mapeo real se mantiene exclusivamente en el entorno Databricks privado

---

## Cómo reproducir

### Requisitos
- Cuenta Databricks (Free Edition o superior)
- PySpark 4.1.0+
- Librerías: `lxml`, `plotly`, `pandas`, `numpy`, `scikit-learn`

### Pasos

1. **Configurar el datalake** en Databricks Unity Catalog:
```
workspace.vermont.bronze   (Volume)
workspace.vermont.trusted  (Volume)
workspace.vermont.silver   (Volume)
```

2. **Subir los datos** al volume Bronze:
```
/Volumes/workspace/vermont/bronze/report.xls
/Volumes/workspace/vermont/bronze/exported.xls
/Volumes/workspace/vermont/bronze/Consolidado_seguimiento.xls
/Volumes/workspace/vermont/bronze/Consolidado_seguimiento (1).xls
```

3. **Ejecutar los notebooks en orden**:
```
01 → 02 → 03 → 04 → 05
```

4. **Configurar variable de anonimización** en Notebook 02:
```python
MODO_ANONIMO = True   # Para uso académico (datos anonimizados)
MODO_ANONIMO = False  # Para uso real en Vermont (datos reales)
```

---

## Resultados principales

| Métrica | Valor |
|---------|-------|
| Total estudiantes analizados | 149 |
| Estudiantes sin riesgo | 81 (54.4%) |
| Estudiantes riesgo recuperación | 49 (32.9%) |
| Estudiantes riesgo crítico | 19 (12.8%) |
| F1-Score modelo (CV k=5) | 0.8804 |
| Asignatura más crítica | Mathematics (38 est. bajo 4.0) |
| Variable más predictiva | nota_min_acumulada (importancia: 0.50) |

---

## Modelo de Machine Learning

**Algoritmo**: Random Forest Classifier (SparkML)  
**Estrategias implementadas**:
- Class weights para balanceo de clases desbalanceadas (13% crítico vs 54% sin riesgo)
- 5-Fold Cross-Validation para evaluación robusta con dataset pequeño
- Grid search de hiperparámetros (numTrees × maxDepth)

**Mejores hiperparámetros**: numTrees=50, maxDepth=3

---

## Trabajo futuro

1. **Datos históricos**: Incorporar 2023-24 y 2024-25 para entrenar el modelo con resultados conocidos y hacer predicciones genuinamente tempranas
2. **Escalabilidad Redcol**: Extender el pipeline a otros colegios de la red con partición por institución
3. **Efecto docente**: Ajuste por severidad del docente en registro de seguimientos
4. **API Phidias**: Migrar de exportación manual a ingesta directa via API RESTful

---

## Limitación actual

El modelo actual se entrena y evalúa sobre el mismo año lectivo (2025-26), lo que implica que describe condiciones ya conocidas. La arquitectura está diseñada para operar con datos históricos como conjunto de entrenamiento, lo que constituye el siguiente paso del proyecto.

---

## Referencias

- Databricks Documentation: https://docs.databricks.com
- Apache Spark MLlib: https://spark.apache.org/docs/latest/ml-guide.html
- CRISP-DM Methodology: Chapman et al. (2000)
