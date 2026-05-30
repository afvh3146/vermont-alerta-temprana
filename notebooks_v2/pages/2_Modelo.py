"""
Vermont EWS — Página 2: Modelo predictivo
Tabs: Clasificación de riesgo | Predicción T3
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Modelo · Vermont EWS", page_icon="🤖", layout="wide")

# ── Tabs ───────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎯 Clasificación de riesgo", "📈 Predicción T3"])

# ══════════════════════════════════════════════
# TAB 1 — CLASIFICACIÓN
# ══════════════════════════════════════════════
with tab1:
    st.markdown("## Modelos de Machine Learning")
    st.caption(
        "Entrenado en 2024–25 (117 est.) · Evaluado en 2025–26 (149 est.) · "
        "Validación: 5-Fold CV estratificado"
    )
    st.divider()
    st.markdown("### 1. Modelo de clasificación de riesgo")
    st.caption(
        "Predice la categoría de riesgo del estudiante · "
        "Variable objetivo: critical / recovery / no_risk"
    )

    df_clf = pd.DataFrame([
        {"Modelo": "Regresión Logística", "Accuracy": 0.692, "Balanced Acc": 0.597,
         "F1 macro": 0.593, "ROC-AUC": 0.782, "Recall critical": 0.556},
        {"Modelo": "Árbol de Decisión",   "Accuracy": 0.633, "Balanced Acc": 0.544,
         "F1 macro": 0.535, "ROC-AUC": 0.690, "Recall critical": 0.556},
        {"Modelo": "Random Forest",        "Accuracy": 0.701, "Balanced Acc": 0.568,
         "F1 macro": 0.573, "ROC-AUC": 0.868, "Recall critical": 0.389},
        {"Modelo": "Gradient Boosting",    "Accuracy": 0.633, "Balanced Acc": 0.503,
         "F1 macro": 0.502, "ROC-AUC": 0.808, "Recall critical": 0.389},
        {"Modelo": "Voting Ensemble",      "Accuracy": 0.692, "Balanced Acc": 0.583,
         "F1 macro": 0.589, "ROC-AUC": 0.831, "Recall critical": 0.444},
    ])

    df_clf_prod = pd.DataFrame([{
        "Modelo": "✅ Random Forest (umbral 0.30)",
        "Accuracy": "—", "Balanced Acc": "—",
        "F1 macro": 0.663, "ROC-AUC": 0.868, "Recall critical": 0.833
    }])

    st.markdown("#### Comparativa 5 modelos — 5-Fold CV (umbral por defecto 0.50)")
    st.dataframe(df_clf, use_container_width=True, hide_index=True)

    st.markdown("""
    <div style="background:#fff8e1;border-left:4px solid #f39c12;
                padding:10px 14px;border-radius:6px;margin:8px 0">
        <b>Decisión de modelo:</b> Con umbral por defecto, Logística y Árbol 
        tuvieron el mejor Recall critical (0.556) pero Random Forest tuvo el 
        mayor ROC-AUC (0.868). Al optimizar el umbral de RF a <b>0.30</b>, 
        el Recall critical subió a <b>0.833</b> (detecta 15 de 18 críticos) 
        con solo 11 falsas alarmas — superando a todos los modelos.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Modelo seleccionado — RF con umbral 0.30")
    st.dataframe(df_clf_prod, use_container_width=True, hide_index=True)

    st.markdown("#### Variables más determinantes — Clasificador")
    st.caption("¿Qué factores del estudiante predicen mejor el riesgo de no aprobación?")

    imp_clf_data = [
        ("min_nota_T2",            0.1063, "Nota mínima en T2"),
        ("Mathematics_T2",         0.0936, "Nota Matemáticas T2"),
        ("avg_T2",                 0.0847, "Promedio general T2"),
        ("avg_T1",                 0.0776, "Promedio general T1"),
        ("n_bajo_T2",              0.0613, "N° materias bajo 4.0 en T2"),
        ("I_and_S_T1",             0.0504, "Nota I&S T1"),
        ("dispersion_T2",          0.0439, "Dispersión de notas T2"),
        ("I_and_S_T2",             0.0411, "Nota I&S T2"),
        ("min_nota_T1",            0.0390, "Nota mínima en T1"),
        ("Lengua_Castellana_T1",   0.0327, "Nota Lengua Castellana T1"),
        ("n_bajo_T1",              0.0301, "N° materias bajo 4.0 en T1"),
        ("Mathematics_T1",         0.0279, "Nota Matemáticas T1"),
        ("Mandarin_T2",            0.0218, "Nota Mandarin T2"),
        ("delta_materias_bajo",    0.0213, "Cambio en N° materias bajo 4.0"),
        ("English_T1",             0.0191, "Nota English T1"),
    ]
    df_imp_clf = pd.DataFrame(imp_clf_data, columns=["Variable", "Importancia", "Descripción"])

    fig_imp_clf = go.Figure(go.Bar(
        x=df_imp_clf["Importancia"],
        y=df_imp_clf["Variable"],
        orientation="h",
        marker_color="#e74c3c",
        text=df_imp_clf["Importancia"].apply(lambda x: f"{x:.3f}"),
        textposition="outside",
        customdata=df_imp_clf["Descripción"],
        hovertemplate="<b>%{y}</b><br>%{customdata}<br>Importancia: %{x:.4f}<extra></extra>"
    ))
    fig_imp_clf.update_layout(
        height=420,
        xaxis_title="Importancia (Gini)",
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0"),
        margin=dict(l=10, r=80, t=20, b=40)
    )
    st.plotly_chart(fig_imp_clf, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — PREDICCIÓN T3
# ══════════════════════════════════════════════
with tab2:
    st.markdown("### 2. Modelo de predicción de nota T3")
    st.caption(
        "Predice la nota T3 por materia para cada estudiante · "
        "Multi-output: 10 materias simultáneamente · Genera intervalos P10–P90"
    )

    df_reg = pd.DataFrame([
        {"Modelo": "Regresión Lineal",  "MAE": 2.921, "RMSE": 11.807, "R²": -154.868,
         "Nota": "⚠️ Colapso por multicolinealidad"},
        {"Modelo": "Árbol de Decisión", "MAE": 0.740, "RMSE": 1.024,  "R²": -0.016,
         "Nota": ""},
        {"Modelo": "Random Forest",     "MAE": 0.642, "RMSE": 0.874,  "R²": 0.238,
         "Nota": "✅ Seleccionado"},
        {"Modelo": "Gradient Boosting", "MAE": 0.664, "RMSE": 0.912,  "R²": 0.164,
         "Nota": ""},
        {"Modelo": "OLS (statsmodels)", "MAE": 0.438, "RMSE": 0.576,  "R²": 0.666,
         "Nota": "⚠️ Evaluado en train — R² optimista"},
    ])

    st.markdown("#### Comparativa 4 modelos + OLS — 5-Fold CV")
    st.dataframe(df_reg, use_container_width=True, hide_index=True)

    st.markdown("""
    <div style="background:#fff8e1;border-left:4px solid #f39c12;
                padding:10px 14px;border-radius:6px;margin:8px 0">
        <b>Decisión de modelo:</b> Regresión Lineal colapsó por multicolinealidad 
        severa entre features (R²=−154). OLS tiene R² alto (0.666) pero fue 
        evaluado en train — no es comparable. Entre los modelos con CV honesta, 
        <b>Random Forest</b> logró el mejor R² (0.238) y menor MAE (0.642) — 
        equivale a un error promedio de ±0.64 puntos en la escala 1–7.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Variables más determinantes — Regresor T3")
    st.caption("¿Qué factores del estudiante predicen mejor la nota final T3?")

    imp_reg_data = [
        ("avg_T1",                  0.1253, "Promedio general T1"),
        ("Lengua_Castellana_T2",    0.0982, "Nota Lengua Castellana T2"),
        ("Mathematics_T2",          0.0701, "Nota Matemáticas T2"),
        ("I_and_S_T2",              0.0504, "Nota I&S T2"),
        ("English_T1",              0.0497, "Nota English T1"),
        ("ICT_STEM_T1",             0.0393, "Nota ICT/STEM T1"),
        ("dispersion_T2",           0.0305, "Dispersión de notas T2"),
        ("late",                    0.0291, "Llegadas tarde"),
        ("Mandarin_T2",             0.0290, "Nota Mandarin T2"),
        ("Lengua_Castellana_delta", 0.0281, "Tendencia Lengua Castellana T1→T2"),
        ("I_and_S_T1",              0.0279, "Nota I&S T1"),
        ("Mathematics_delta",       0.0257, "Tendencia Matemáticas T1→T2"),
        ("English_T2",              0.0232, "Nota English T2"),
        ("Financial_Maths_T1",      0.0228, "Nota Fin. Maths T1"),
        ("Science_T2",              0.0210, "Nota Science T2"),
    ]
    df_imp_reg = pd.DataFrame(imp_reg_data, columns=["Variable", "Importancia", "Descripción"])

    fig_imp_reg = go.Figure(go.Bar(
        x=df_imp_reg["Importancia"],
        y=df_imp_reg["Variable"],
        orientation="h",
        marker_color="#3498db",
        text=df_imp_reg["Importancia"].apply(lambda x: f"{x:.3f}"),
        textposition="outside",
        customdata=df_imp_reg["Descripción"],
        hovertemplate="<b>%{y}</b><br>%{customdata}<br>Importancia: %{x:.4f}<extra></extra>"
    ))
    fig_imp_reg.update_layout(
        height=420,
        xaxis_title="Importancia (Gini)",
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0"),
        margin=dict(l=10, r=80, t=20, b=40)
    )
    st.plotly_chart(fig_imp_reg, use_container_width=True)
