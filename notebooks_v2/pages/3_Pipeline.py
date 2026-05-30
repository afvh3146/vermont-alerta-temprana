"""
Vermont EWS — Página 3: Pipeline
Tabs: Arquitectura | Ciclo de vida del dato | Diccionario de datos
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pipeline · Vermont EWS", page_icon="⚙️", layout="wide")

tab1, tab2, tab3 = st.tabs(["🏗️ Arquitectura", "🔄 Ciclo de vida del dato", "📖 Diccionario de datos"])

# ══════════════════════════════════════════════
# TAB 1 — ARQUITECTURA
# ══════════════════════════════════════════════
with tab1:
    st.markdown("## Arquitectura de referencia")
    st.caption("Patrón Medallion (Bronze → Trusted → Silver) · Databricks Free Edition · PySpark 4.1.0")

    st.markdown("### Flujo del pipeline")
    cols = st.columns([1, 0.3, 1, 0.3, 1, 0.3, 1, 0.3, 1])

    def caja(col, emoji, titulo, detalle, color_borde, color_texto):
        col.markdown(f"""
        <div style="border:2px solid {color_borde};border-radius:10px;
                    padding:14px 8px;text-align:center;min-height:130px">
            <div style="font-size:1.6em">{emoji}</div>
            <div style="font-weight:700;color:{color_texto};margin-top:4px;font-size:0.95em">{titulo}</div>
            <div style="font-size:0.72em;color:#666;margin-top:4px;line-height:1.5">{detalle}</div>
        </div>""", unsafe_allow_html=True)

    def flecha(col):
        col.markdown(
            "<div style='text-align:center;font-size:1.6em;color:#aaa;padding-top:40px'>→</div>",
            unsafe_allow_html=True
        )

    caja(cols[0], "🏫", "Phidias",   "Exportación<br>XLS manual",                "#bdc3c7", "#555")
    flecha(cols[1])
    caja(cols[2], "🥉", "Bronze",    "XLS raw<br>CSV anon<br>Parquet prep",       "#f39c12", "#e67e22")
    flecha(cols[3])
    caja(cols[4], "🥈", "Trusted",   "Dataset train<br>Dataset pred<br>Parquet", "#3498db", "#2980b9")
    flecha(cols[5])
    caja(cols[6], "🥇", "Silver",    "EDA · Modelo<br>Alertas · CSV<br>dashboard","#2ecc71", "#27ae60")
    flecha(cols[7])
    def caja(col, emoji, titulo, detalle, color_borde, color_texto):
        col.markdown(f"""
        <div style="border:2px solid {color_borde};border-radius:10px;
                    padding:14px 8px;text-align:center;min-height:130px">
            <div style="font-size:1.6em">{emoji}</div>
            <div style="font-weight:700;color:{color_texto};margin-top:4px;font-size:0.95em">{titulo}</div>
            <div style="font-size:0.72em;color:#666;margin-top:4px;line-height:1.5">{detalle}</div>
        </div>""", unsafe_allow_html=True)(cols[8], "📊", "Dashboard", "Streamlit<br>Vermont EWS<br>vmt-ews-acad", "#9b59b6", "#8e44ad")

    st.divider()
    st.markdown("### Stack tecnológico")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:16px">
            <div style="font-weight:700;margin-bottom:10px">⚙️ Procesamiento</div>
            <div style="font-size:0.85em;line-height:1.9">
                Databricks Free Edition<br>
                PySpark 4.1.0<br>
                SparkSQL<br>
                Unity Catalog Volumes
            </div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:16px">
            <div style="font-weight:700;margin-bottom:10px">🤖 Modelado</div>
            <div style="font-size:0.85em;line-height:1.9">
                SparkML RandomForestClassifier<br>
                SparkML RandomForestRegressor<br>
                CrossValidator (5-Fold)<br>
                Umbral optimizado (0.30)
            </div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:16px">
            <div style="font-weight:700;margin-bottom:10px">📦 Formatos y salidas</div>
            <div style="font-size:0.85em;line-height:1.9">
                XLS → CSV → Parquet<br>
                Anonimización SHA-256<br>
                GitHub + Streamlit Cloud<br>
                dashboard_data.csv
            </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Zonas del datalake")
    df_zonas = pd.DataFrame([
        {"Zona": "🥉 Bronze / raw",      "Ruta": "bronze/raw/{año}/",      "Formato": "XLS",          "Contenido": "Archivos originales exportados de Phidias"},
        {"Zona": "🥉 Bronze / anon",     "Ruta": "bronze/anon/{año}/",     "Formato": "CSV",          "Contenido": "Datos anonimizados (SHA-256 en student_id, secciones recodificadas)"},
        {"Zona": "🥉 Bronze / prepared", "Ruta": "bronze/prepared/",       "Formato": "Parquet",      "Contenido": "Asignaturas unificadas entre cohortes"},
        {"Zona": "🥈 Trusted",           "Ruta": "trusted/",               "Formato": "Parquet",      "Contenido": "Dataset de entrenamiento (2024-25) y predicción (2025-26)"},
        {"Zona": "🥇 Silver",            "Ruta": "silver/",                "Formato": "Parquet / CSV","Contenido": "EDA, modelo entrenado, alertas, dashboard_data.csv"},
        {"Zona": "🔒 Privado",           "Ruta": "privado/",               "Formato": "CSV",          "Contenido": "Tabla de mapeo real (student_id real ↔ hash) — solo en Databricks"},
    ])
    st.dataframe(df_zonas, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Decisiones de diseño")
    decisiones = [
        ("🔐 SHA-256 y no supresión del ID",
         "Suprimir el ID impediría cruzar datos entre trimestres y años. "
         "SHA-256 pseudonimiza de forma determinista — el mismo estudiante siempre produce "
         "el mismo hash — permitiendo el seguimiento longitudinal sin exponer identidades."),
        ("📦 Parquet y no CSV en Trusted/Silver",
         "Parquet es columnar y comprimido — hasta 10× menos espacio que CSV para datasets "
         "con muchas columnas numéricas. Además preserva tipos de datos (float, int, bool) "
         "sin conversión, eliminando errores de parsing al leer en PySpark."),
        ("🎯 Umbral 0.30 y no 0.50",
         "Con umbral por defecto (0.50), el RF detectaba solo 7 de 18 críticos (Recall=0.389). "
         "Al bajar a 0.30 sube a 15 de 18 (Recall=0.833) con solo 11 falsas alarmas adicionales. "
         "En contexto educativo el costo de no detectar un crítico es mayor que el de sobre-alertar."),
        ("📐 K-Means y no clustering jerárquico",
         "Con 149 estudiantes y variables mixtas, K-Means con K-Prototypes es computacionalmente "
         "eficiente y produce clusters interpretables. El clustering jerárquico no escala bien "
         "con features continuas y categóricas mezcladas, y sus dendrogramas son difíciles "
         "de comunicar a una audiencia no técnica."),
    ]
    for titulo, desc in decisiones:
        st.markdown(f"""
        <div style="background:#f8f9fa;border-left:4px solid #3498db;
                    border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:12px">
            <div style="font-weight:700;margin-bottom:4px">{titulo}</div>
            <div style="font-size:0.87em;color:#444;line-height:1.6">{desc}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — CICLO DE VIDA DEL DATO
# ══════════════════════════════════════════════
with tab2:
    st.markdown("## Ciclo de vida del dato")
    st.caption("Desde la exportación manual en Phidias hasta las alertas en el dashboard")

    pasos = [
        ("1", "#e67e22", "📥 Extracción",
         "Exportación manual de reportes XLS desde Phidias (notas, asistencia, seguimientos). "
         "Se explora viabilidad de conexión vía API RESTful para automatizar en versiones futuras."),
        ("2", "#e74c3c", "🔒 Anonimización",
         "Pseudonimización del student_id real con SHA-256. Recodificación aleatoria de secciones "
         "(A/B → S1/S2) y docentes (P01, P02…). Supresión de texto libre en F2/F3. "
         "El mapeo real se guarda en zona privada de Databricks — nunca sale del entorno."),
        ("3", "#f39c12", "🥉 Bronze",
         "Carga de XLS originales (raw), CSV anonimizados (anon) y Parquet con asignaturas "
         "unificadas entre cohortes (prepared). Normalización de escala de notas si se integran "
         "datos 2023-24 (escala 1-10 → 1-7)."),
        ("4", "#3498db", "🥈 Trusted",
         "Preparación del dataset de entrenamiento (2024-25, 117 estudiantes) y del dataset "
         "de predicción (2025-26, 149 estudiantes). Feature engineering: delta T1→T2 por "
         "asignatura, índice disciplinario ponderado (F1×1 + F2×3), variables de resumen."),
        ("5", "#27ae60", "🥇 Silver — Modelado",
         "Entrenamiento del clasificador de riesgo (RF, umbral 0.30) y del regresor de nota T3 "
         "(RF multi-output). Generación de probabilidades, intervalos P10-P90, categoría de "
         "alerta y perfil de cluster (K-Means). Salida: dashboard_data.csv con 127 columnas."),
        ("6", "#9b59b6", "📊 Visualización",
         "dashboard_data.csv se publica en GitHub y se consume desde Streamlit Cloud. "
         "El dashboard se ejecuta semanalmente durante el trimestre académico. "
         "Sin datos reales en tránsito — solo el CSV anonimizado."),
    ]

    for num, color, titulo, desc in pasos:
        st.markdown(f"""
        <div style="display:flex;gap:16px;margin-bottom:16px;align-items:flex-start">
            <div style="background:{color};color:white;border-radius:50%;
                        min-width:36px;height:36px;display:flex;align-items:center;
                        justify-content:center;font-weight:700;font-size:1.1em;
                        flex-shrink:0">{num}</div>
            <div style="background:#f8f9fa;border-left:4px solid {color};
                        border-radius:0 8px 8px 0;padding:12px 16px;flex:1">
                <div style="font-weight:700;margin-bottom:4px">{titulo}</div>
                <div style="font-size:0.87em;color:#444;line-height:1.6">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Consideraciones de privacidad")
    st.markdown("""
    <div style="background:#fdf2f8;border-left:4px solid #9b59b6;
                padding:14px 16px;border-radius:0 8px 8px 0">
        <div style="font-size:0.87em;color:#444;line-height:1.8">
            • Los datos contienen información sensible de <b>menores de edad</b> — se aplica
            anonimización antes de cualquier exposición fuera de Databricks.<br>
            • El texto libre de seguimientos F2/F3 <b>no se incluye</b> en ningún dataset —
            solo conteos clasificados por tipo.<br>
            • Los diagnósticos LSC se manejan como marcador binario (0/1) —
            sin tipo de diagnóstico.<br>
            • El mapeo real (hash ↔ nombre) solo existe en la zona privada de Databricks
            y <b>nunca se publica</b>.
        </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — DICCIONARIO DE DATOS
# ══════════════════════════════════════════════
with tab3:
    st.markdown("## Diccionario de datos")
    st.caption("127 variables en dashboard_data.csv · agrupadas por categoría")

    grupos = {
        "🪪 Identificación": [
            ("student_id",    "Código del estudiante (hash SHA-256)",         "Phidias → anonimizado"),
            ("grade",         "Grado (7, 8 o 9)",                             "Phidias"),
            ("section_anon",  "Sección recodificada aleatoriamente (S1/S2…)", "Phidias → anonimizado"),
        ],
        "📝 Notas académicas (×10 materias)": [
            ("{MAT}_T1",     "Nota real Trimestre 1",                          "Phidias"),
            ("{MAT}_T2",     "Nota real Trimestre 2",                          "Phidias"),
            ("{MAT}_T3",     "Nota real Trimestre 3 (parcial en curso)",        "Phidias"),
            ("{MAT}_min_T3", "Nota mínima necesaria en T3 para aprobar",        "Derivada · fórmula institucional"),
        ],
        "📊 Resumen académico": [
            ("avg_T1",            "Promedio general del estudiante en T1",     "Derivada"),
            ("avg_T2",            "Promedio general del estudiante en T2",     "Derivada"),
            ("tendencia_general", "Delta promedio T1→T2",                      "Derivada"),
            ("n_bajo_T1",         "N° materias bajo 4.0 en T1",               "Derivada"),
            ("n_bajo_T2",         "N° materias bajo 4.0 en T2",               "Derivada"),
            ("n_bajo_acumulada",  "N° materias con nota acumulada bajo 4.0",   "Derivada"),
            ("n_destacadas_T2",   "N° materias con nota ≥ 6.0 en T2",         "Derivada"),
            ("min_nota_T2",       "Nota mínima individual en T2",              "Derivada"),
        ],
        "🏃 Asistencia": [
            ("pct_asistencia", "Porcentaje de asistencia",     "Phidias"),
            ("total_absences", "Total de ausencias",           "Phidias"),
            ("absence_class",  "Ausencias por clase",          "Phidias"),
            ("late",           "Llegadas tarde",               "Phidias"),
            ("early_leave",    "Salidas anticipadas",          "Phidias"),
        ],
        "⚠️ Convivencia": [
            ("n_f1",                 "N° seguimientos F1 (faltas leves)",  "Phidias"),
            ("n_f2",                 "N° seguimientos F2 (faltas graves)", "Phidias"),
            ("indice_disciplinario", "Índice ponderado: F1×1 + F2×3",      "Derivada"),
        ],
        "🎓 Apoyo al aprendizaje": [
            ("marcador_LSC", "Pertenece al Learning Support Center (0/1)", "Vermont School"),
        ],
        "🤖 Salidas del modelo de clasificación": [
            ("pred_label",         "Etiqueta predicha: no_risk / recovery / critical",                        "Modelo RF"),
            ("proba_critical",     "Probabilidad de ser crítico",                                             "Modelo RF"),
            ("proba_recovery",     "Probabilidad de estar en recuperación",                                   "Modelo RF"),
            ("proba_riesgo",       "Probabilidad combinada de riesgo (critical + recovery)",                  "Modelo RF"),
            ("confianza",          "Confianza de la predicción",                                              "Modelo RF"),
            ("categoria",          "Sin Riesgo / Riesgo Teórico / Riesgo Confirmado / Punto Ciego",          "Derivada · lógica de cuadrante"),
            ("t3_confirma_riesgo", "Flag: T3 parcial confirma riesgo (0/1)",                                 "Derivada"),
        ],
        "🔮 Predicción T3 (×10 materias)": [
            ("{MAT}_T3_pred",           "Nota T3 predicha (modelo regresor RF)",  "Modelo RF"),
            ("{MAT}_T3_p10",            "Percentil 10 — escenario pesimista",     "Modelo RF"),
            ("{MAT}_T3_p90",            "Percentil 90 — escenario optimista",     "Modelo RF"),
            ("{MAT}_T3_amp",            "Amplitud del intervalo P10–P90",         "Derivada"),
            ("{MAT}_T3_pred_confiable", "Flag: predicción confiable (0/1)",       "Derivada"),
            ("incertidumbre_promedio",  "Incertidumbre promedio del regresor",    "Derivada"),
        ],
        "🧩 Clustering": [
            ("cluster", "Número de cluster (K-Means)",                                       "Modelo K-Means"),
            ("perfil",  "Etiqueta del perfil: Rendimiento sólido / Riesgo multidimensional…","Derivada"),
        ],
        "📅 Metadatos": [
            ("modelo",          "Versión del modelo usado",              "Pipeline"),
            ("fecha_ejecucion", "Fecha de ejecución del pipeline",       "Pipeline"),
            ("fecha_corte",     "Fecha de corte de los datos",           "Pipeline"),
            ("fecha_corte_tag", "Etiqueta legible de la fecha de corte", "Pipeline"),
        ],
    }

    for grupo, variables in grupos.items():
        with st.expander(f"{grupo} — {len(variables)} variable(s)", expanded=False):
            df_grupo = pd.DataFrame(variables, columns=["Variable", "Descripción", "Fuente"])
            st.dataframe(df_grupo, use_container_width=True, hide_index=True)
