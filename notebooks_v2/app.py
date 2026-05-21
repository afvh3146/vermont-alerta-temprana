"""
Vermont Early Warning System — Dashboard Streamlit
Andrés Velasco Hernández | EAFIT Maestría CDA 2026-1
Proyecto Integrador: SI7009 + SI7006 + SI7007
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Vermont Early Warning System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_URL = (
    "https://raw.githubusercontent.com/afvh3146/"
    "vermont-alerta-temprana/main/notebooks_v2/dashboard_data.csv"
)

SUBJECTS = [
    "Science", "I_and_S", "Mathematics", "English",
    "Lengua_Castellana", "Mandarin", "Financial_Maths",
    "ICT_STEM", "Physical_Education", "Research_Methodology"
]

SUBJECT_LABELS = {
    "Science": "Science",
    "I_and_S": "I&S",
    "Mathematics": "Mathematics",
    "English": "English",
    "Lengua_Castellana": "Lengua Cast.",
    "Mandarin": "Mandarin",
    "Financial_Maths": "Fin. Maths",
    "ICT_STEM": "ICT/STEM",
    "Physical_Education": "Phys. Ed.",
    "Research_Methodology": "Research"
}

# Colores por categoría de alerta
ALERT_COLORS = {
    "🔴 CONFIRMED_CRITICAL": "#e74c3c",
    "🟠 DETERIORATING":      "#e67e22",
    "🟠 RECOVERING":         "#f39c12",
    "🟡 RECOVERY_ALERT":     "#f1c40f",
    "🔵 MONITOR":            "#3498db",
    "🟢 ON_TRACK":           "#2ecc71",
}

ALERT_ORDER = [
    "🔴 CONFIRMED_CRITICAL",
    "🟠 DETERIORATING",
    "🟠 RECOVERING",
    "🟡 RECOVERY_ALERT",
    "🔵 MONITOR",
    "🟢 ON_TRACK",
]

ALERT_LABELS = {
    "🔴 CONFIRMED_CRITICAL": "Crítico confirmado",
    "🟠 DETERIORATING":      "Deteriorando",
    "🟠 RECOVERING":         "En recuperación",
    "🟡 RECOVERY_ALERT":     "Alerta recuperación",
    "🔵 MONITOR":            "Monitorear",
    "🟢 ON_TRACK":           "En track",
}

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)
    # Extraer letra de sección desde section_anon (ej. "G7SA" → "A")
    df["seccion"] = df["section_anon"].str[-1]  # último caracter: A o B
    df["grado_label"] = df["grade"].astype(str) + "° " + df["seccion"]
    df["alert_category"] = df["alert_category"].fillna("🔵 MONITOR")
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR — FILTROS
# ─────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/"
        "Camponotus_flavomarginatus_ant.jpg/1px-transparent.gif",
        width=1
    )
    st.markdown("## 🏫 Vermont EWS")
    st.markdown("**Early Warning System**")
    st.markdown("Año lectivo 2025–26 | T1 + T2 + T3 parcial")
    st.divider()

    st.markdown("### Filtrar por grupo")

    opciones_grado = ["Todos", "7°", "8°", "9°"]
    grado_sel = st.selectbox("Grado", opciones_grado)

    # Secciones disponibles según grado
    if grado_sel == "Todos":
        df_filtrado = df.copy()
        secciones_disp = ["Todas", "A", "B"]
    else:
        grado_num = int(grado_sel[0])
        df_filtrado = df[df["grade"] == grado_num].copy()
        secciones_disp = ["Todas"] + sorted(df_filtrado["seccion"].unique().tolist())

    seccion_sel = st.selectbox("Sección", secciones_disp)

    if seccion_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["seccion"] == seccion_sel]

    st.divider()
    st.markdown("### Filtrar por categoría")
    cats_sel = st.multiselect(
        "Categorías",
        options=ALERT_ORDER,
        default=ALERT_ORDER,
        format_func=lambda x: ALERT_LABELS.get(x, x)
    )
    if cats_sel:
        df_filtrado = df_filtrado[df_filtrado["alert_category"].isin(cats_sel)]

    st.divider()
    n_total = len(df_filtrado)
    n_criticos = (df_filtrado["alert_category"] == "🔴 CONFIRMED_CRITICAL").sum()
    n_alerta = df_filtrado["alert_category"].isin([
        "🟠 DETERIORATING", "🟠 RECOVERING", "🟡 RECOVERY_ALERT"
    ]).sum()
    st.metric("Estudiantes", n_total)
    st.metric("🔴 Críticos", n_criticos)
    st.metric("⚠️ En alerta", n_alerta)

# ─────────────────────────────────────────────
# TÍTULO PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("# 🏫 Vermont Early Warning System")
grupo_texto = f"{grado_sel}" if grado_sel != "Todos" else "Middle School"
if seccion_sel != "Todas":
    grupo_texto += f" Sección {seccion_sel}"
st.markdown(f"**{grupo_texto}** · {n_total} estudiantes · Año lectivo 2025–26")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Semáforo general",
    "🔍 Detalle por estudiante",
    "📚 Por asignatura",
    "📈 Modelo predictivo"
])

# ══════════════════════════════════════════════
# TAB 1 — SEMÁFORO GENERAL
# ══════════════════════════════════════════════
with tab1:

    # Métricas resumen
    cols = st.columns(6)
    for i, cat in enumerate(ALERT_ORDER):
        n = (df_filtrado["alert_category"] == cat).sum()
        label = ALERT_LABELS[cat]
        emoji = cat.split()[0]
        cols[i].metric(f"{emoji} {label}", n)

    st.divider()

    col_scatter, col_bar = st.columns([3, 2])

    with col_scatter:
        st.markdown("#### Scatter: Promedio acumulado vs. Materias bajo 4.0")
        st.caption("Cada punto es un estudiante. Hover para ver detalles.")

        # Preparar datos scatter
        df_scatter = df_filtrado.copy()
        df_scatter["color"] = df_scatter["alert_category"].map(ALERT_COLORS)
        df_scatter["label"] = df_scatter["alert_category"].map(ALERT_LABELS)
        df_scatter["LSC"] = df_scatter["marcador_LSC"].map({1: "Con LSC", 0: "Sin LSC"})
        df_scatter["hover"] = (
            "ID: " + df_scatter["student_id"].astype(str) +
            "<br>Grado: " + df_scatter["grade"].astype(str) + "° " + df_scatter["seccion"] +
            "<br>Promedio: " + df_scatter["avg_cumulative"].round(2).astype(str) +
            "<br>Materias bajo 4.0: " + df_scatter["n_subjects_below_4"].astype(str) +
            "<br>LSC: " + df_scatter["LSC"] +
            "<br>Confianza modelo: " + (df_scatter["confidence"] * 100).round(0).astype(str) + "%"
        )

        fig_scatter = go.Figure()

        for cat in ALERT_ORDER:
            sub = df_scatter[df_scatter["alert_category"] == cat]
            if sub.empty:
                continue
            fig_scatter.add_trace(go.Scatter(
                x=sub["avg_cumulative"],
                y=sub["n_subjects_below_4"],
                mode="markers",
                name=ALERT_LABELS[cat],
                marker=dict(
                    color=ALERT_COLORS[cat],
                    size=10,
                    line=dict(width=1, color="white"),
                    symbol=sub["marcador_LSC"].map({1: "diamond", 0: "circle"})
                ),
                hovertext=sub["hover"],
                hoverinfo="text"
            ))

        # Líneas de referencia
        fig_scatter.add_hline(y=2.5, line_dash="dash", line_color="gray",
                               annotation_text="3 mat. = pierde el año",
                               annotation_position="right")
        fig_scatter.add_vline(x=4.0, line_dash="dash", line_color="gray",
                               annotation_text="Promedio mínimo",
                               annotation_position="top")

        fig_scatter.update_layout(
            height=400,
            xaxis_title="Promedio acumulado",
            yaxis_title="N° materias bajo 4.0",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=40, r=20, t=40, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        fig_scatter.update_xaxes(range=[1, 7.5], gridcolor="#f0f0f0")
        fig_scatter.update_yaxes(range=[-0.5, 10.5], gridcolor="#f0f0f0", dtick=1)

        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("◆ = estudiante con LSC | ● = sin LSC")

    with col_bar:
        st.markdown("#### Distribución por categoría")

        cat_counts = (
            df_filtrado["alert_category"]
            .value_counts()
            .reindex(ALERT_ORDER)
            .dropna()
            .reset_index()
        )
        cat_counts.columns = ["categoria", "n"]
        cat_counts["label"] = cat_counts["categoria"].map(ALERT_LABELS)
        cat_counts["color"] = cat_counts["categoria"].map(ALERT_COLORS)

        fig_bar = go.Figure(go.Bar(
            x=cat_counts["n"],
            y=cat_counts["label"],
            orientation="h",
            marker_color=cat_counts["color"],
            text=cat_counts["n"],
            textposition="outside"
        ))
        fig_bar.update_layout(
            height=400,
            xaxis_title="N° estudiantes",
            yaxis_title="",
            margin=dict(l=10, r=40, t=20, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        fig_bar.update_xaxes(gridcolor="#f0f0f0")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Distribución por grado si se ve todo
        if grado_sel == "Todos":
            st.markdown("#### Por grado")
            grade_cat = (
                df_filtrado.groupby(["grade", "alert_category"])
                .size().reset_index(name="n")
            )
            grade_cat["label"] = grade_cat["alert_category"].map(ALERT_LABELS)
            grade_cat["color"] = grade_cat["alert_category"].map(ALERT_COLORS)
            grade_cat["grado_str"] = grade_cat["grade"].astype(str) + "°"

            fig_grade = px.bar(
                grade_cat, x="grado_str", y="n",
                color="alert_category",
                color_discrete_map=ALERT_COLORS,
                labels={"grado_str": "Grado", "n": "Estudiantes",
                        "alert_category": "Categoría"},
                height=280
            )
            fig_grade.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=40),
                plot_bgcolor="white", paper_bgcolor="white"
            )
            st.plotly_chart(fig_grade, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — DETALLE POR ESTUDIANTE
# ══════════════════════════════════════════════
with tab2:

    st.markdown("#### Lista de estudiantes — urgentes primero")

    # Tabla principal
    df_tabla = df_filtrado.copy()
    df_tabla["cat_order"] = df_tabla["alert_category"].map(
        {cat: i for i, cat in enumerate(ALERT_ORDER)}
    )
    df_tabla = df_tabla.sort_values("cat_order")

    cols_tabla = [
        "student_id", "grade", "seccion", "alert_category",
        "predicted_risk", "current_risk", "confidence",
        "avg_cumulative", "min_cumulative", "n_subjects_below_4",
        "marcador_LSC", "alert_reason"
    ]
    cols_tabla = [c for c in cols_tabla if c in df_tabla.columns]

    df_show = df_tabla[cols_tabla].copy()
    df_show["alert_category"] = df_show["alert_category"].map(ALERT_LABELS)
    df_show["confidence"] = (df_show["confidence"] * 100).round(0).astype(str) + "%"
    df_show["avg_cumulative"] = df_show["avg_cumulative"].round(2)
    df_show["min_cumulative"] = df_show["min_cumulative"].round(2)
    df_show["marcador_LSC"] = df_show["marcador_LSC"].map({1: "✓ LSC", 0: ""})

    df_show = df_show.rename(columns={
        "student_id":         "ID",
        "grade":              "Grado",
        "seccion":            "Secc.",
        "alert_category":     "Categoría",
        "predicted_risk":     "Pred. modelo",
        "current_risk":       "Estado T3",
        "confidence":         "Confianza",
        "avg_cumulative":     "Prom. acum.",
        "min_cumulative":     "Mín. acum.",
        "n_subjects_below_4": "Mat. < 4.0",
        "marcador_LSC":       "LSC",
        "alert_reason":       "Razón"
    })

    st.dataframe(df_show, use_container_width=True, height=400)

    st.divider()

    # Perfil individual
    st.markdown("#### Perfil individual — radar ABC")
    estudiante_ids = df_filtrado["student_id"].tolist()

    if estudiante_ids:
        sel_id = st.selectbox("Seleccionar estudiante", estudiante_ids)
        row = df_filtrado[df_filtrado["student_id"] == sel_id].iloc[0]

        col_info, col_radar = st.columns([1, 2])

        with col_info:
            cat = row["alert_category"]
            color = ALERT_COLORS.get(cat, "#888")
            st.markdown(f"""
            <div style="background:{color}22; border-left:5px solid {color};
                        padding:16px; border-radius:8px; margin-bottom:12px">
                <b style="color:{color}">{ALERT_LABELS.get(cat, cat)}</b><br>
                <span style="font-size:0.85em">{row.get('alert_reason','')}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**Grado:** {row['grade']}° {row['seccion']}")
            st.markdown(f"**Promedio acumulado:** {row['avg_cumulative']:.2f}")
            st.markdown(f"**Mínimo acumulado:** {row['min_cumulative']:.2f}")
            st.markdown(f"**Materias bajo 4.0:** {int(row['n_subjects_below_4'])}")
            st.markdown(f"**Confianza modelo:** {row['confidence']*100:.0f}%")
            lsc_txt = "✓ Sí" if row.get("marcador_LSC", 0) == 1 else "No"
            st.markdown(f"**LSC:** {lsc_txt}")

            st.divider()
            st.markdown("**Predicción:** " + str(row.get("predicted_risk", "—")))
            st.markdown("**Estado T3:** " + str(row.get("current_risk", "—")))

        with col_radar:
            # Radar con T1, T2, T3 parcial por asignatura
            subs_disponibles = [
                s for s in SUBJECTS
                if not pd.isna(row.get(f"{s}_T1", np.nan))
            ]

            if subs_disponibles:
                labels = [SUBJECT_LABELS[s] for s in subs_disponibles]
                t1_vals  = [row.get(f"{s}_T1", 0) or 0  for s in subs_disponibles]
                t2_vals  = [row.get(f"{s}_T2", 0) or 0  for s in subs_disponibles]
                t3_vals  = [row.get(f"{s}_T3_partial", 0) or 0 for s in subs_disponibles]

                fig_radar = go.Figure()
                for vals, name, color_r in [
                    (t1_vals, "T1", "#3498db"),
                    (t2_vals, "T2", "#9b59b6"),
                    (t3_vals, "T3 parcial", "#e74c3c"),
                ]:
                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals + [vals[0]],
                        theta=labels + [labels[0]],
                        fill="toself",
                        name=name,
                        line_color=color_r,
                        fillcolor=color_r,
                        opacity=0.25
                    ))

                fig_radar.add_trace(go.Scatterpolar(
                    r=[4.0] * (len(labels) + 1),
                    theta=labels + [labels[0]],
                    mode="lines",
                    name="Mín. aprobación",
                    line=dict(color="red", dash="dash", width=1.5),
                    showlegend=True
                ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 7]),
                        angularaxis=dict(tickfont=dict(size=11))
                    ),
                    showlegend=True,
                    height=380,
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        # Tabla de materias con min T3 necesario
        st.markdown("#### Notas por asignatura y T3 mínimo necesario")
        rows_mat = []
        for s in SUBJECTS:
            t1 = row.get(f"{s}_T1", np.nan)
            if pd.isna(t1):
                continue
            rows_mat.append({
                "Materia": SUBJECT_LABELS[s],
                "T1": round(t1, 2) if not pd.isna(t1) else "—",
                "T2": round(row.get(f"{s}_T2", np.nan), 2) if not pd.isna(row.get(f"{s}_T2", np.nan)) else "—",
                "T3 parcial": round(row.get(f"{s}_T3_partial", np.nan), 2) if not pd.isna(row.get(f"{s}_T3_partial", np.nan)) else "—",
                "T3 mín. necesario": round(row.get(f"{s}_min_T3", np.nan), 2) if not pd.isna(row.get(f"{s}_min_T3", np.nan)) else "—",
                "Proyectado": round(row.get(f"{s}_projected", np.nan), 2) if not pd.isna(row.get(f"{s}_projected", np.nan)) else "—",
                "Estado": row.get(f"{s}_T3_status", "—")
            })

        if rows_mat:
            df_mat = pd.DataFrame(rows_mat)
            st.dataframe(df_mat, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 3 — POR ASIGNATURA
# ══════════════════════════════════════════════
with tab3:

    st.markdown("#### Promedio por asignatura (T1, T2, T3 parcial)")

    subs_data = []
    for s in SUBJECTS:
        for t, col_name in [("T1", f"{s}_T1"), ("T2", f"{s}_T2"), ("T3 parcial", f"{s}_T3_partial")]:
            if col_name in df_filtrado.columns:
                vals = df_filtrado[col_name].dropna()
                if not vals.empty:
                    subs_data.append({
                        "Materia": SUBJECT_LABELS[s],
                        "Trimestre": t,
                        "Promedio": round(vals.mean(), 2),
                        "N": len(vals)
                    })

    df_subs = pd.DataFrame(subs_data)
    if not df_subs.empty:
        fig_subs = px.bar(
            df_subs, x="Materia", y="Promedio", color="Trimestre",
            barmode="group",
            color_discrete_map={"T1": "#3498db", "T2": "#9b59b6", "T3 parcial": "#e74c3c"},
            height=400
        )
        fig_subs.add_hline(y=4.0, line_dash="dash", line_color="red",
                            annotation_text="Mín. aprobación (4.0)")
        fig_subs.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(range=[0, 7.5], gridcolor="#f0f0f0"),
            xaxis=dict(tickangle=-30),
            margin=dict(l=40, r=20, t=20, b=80)
        )
        st.plotly_chart(fig_subs, use_container_width=True)

    st.divider()
    st.markdown("#### Materias con más estudiantes bajo 4.0 (T3 parcial)")

    at_risk_counts = []
    for s in SUBJECTS:
        col_t3 = f"{s}_T3_partial"
        if col_t3 in df_filtrado.columns:
            n_bajo = (df_filtrado[col_t3] < 4.0).sum()
            n_total_s = df_filtrado[col_t3].notna().sum()
            if n_total_s > 0:
                at_risk_counts.append({
                    "Materia": SUBJECT_LABELS[s],
                    "N bajo 4.0": int(n_bajo),
                    "% del grupo": round(n_bajo / n_total_s * 100, 1)
                })

    df_risk_sub = pd.DataFrame(at_risk_counts).sort_values("N bajo 4.0", ascending=False)
    if not df_risk_sub.empty:
        fig_risk = go.Figure(go.Bar(
            x=df_risk_sub["N bajo 4.0"],
            y=df_risk_sub["Materia"],
            orientation="h",
            marker_color="#e74c3c",
            text=df_risk_sub["% del grupo"].astype(str) + "%",
            textposition="outside"
        ))
        fig_risk.update_layout(
            height=350,
            xaxis_title="N° estudiantes bajo 4.0",
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(gridcolor="#f0f0f0"),
            margin=dict(l=10, r=60, t=20, b=40)
        )
        st.plotly_chart(fig_risk, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — MODELO PREDICTIVO
# ══════════════════════════════════════════════
with tab4:

    st.markdown("#### Desempeño del modelo — Random Forest")
    st.caption("Entrenado en 2024–25 (117 estudiantes) · Aplicado sobre 2025–26 (149 estudiantes)")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("F1-Score (CV)", "0.75")
    col_m2.metric("Validación", "5-Fold CV")
    col_m3.metric("Train", "117 est.")
    col_m4.metric("Predict", "149 est.")

    st.divider()

    col_pred, col_conf = st.columns(2)

    with col_pred:
        st.markdown("#### Predicción del modelo vs. Estado T3")
        cross = pd.crosstab(
            df_filtrado["predicted_risk"],
            df_filtrado["current_risk"],
            margins=False
        )
        fig_heat = px.imshow(
            cross,
            text_auto=True,
            color_continuous_scale="Blues",
            aspect="auto",
            labels=dict(x="Estado real (T3)", y="Predicción modelo", color="N")
        )
        fig_heat.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_conf:
        st.markdown("#### Distribución de confianza por categoría de alerta")
        df_conf = df_filtrado[["alert_category", "confidence"]].copy()
        df_conf["confidence_pct"] = df_conf["confidence"] * 100
        df_conf["label"] = df_conf["alert_category"].map(ALERT_LABELS)

        fig_conf = px.box(
            df_conf, x="label", y="confidence_pct",
            color="alert_category",
            color_discrete_map={k: ALERT_COLORS[k] for k in ALERT_ORDER},
            labels={"label": "Categoría", "confidence_pct": "Confianza (%)"},
            height=320
        )
        fig_conf.update_layout(
            showlegend=False,
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickangle=-30),
            yaxis=dict(gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=20, b=80)
        )
        fig_conf.add_hline(y=50, line_dash="dash", line_color="gray",
                            annotation_text="50% umbral")
        st.plotly_chart(fig_conf, use_container_width=True)

    st.divider()
    st.markdown("#### Predicción del modelo vs. categoría de alerta final")
    st.caption("La categoría final cruza la predicción con T3 parcial.")

    pred_cat = (
        df_filtrado.groupby(["predicted_risk", "alert_category"])
        .size().reset_index(name="n")
    )
    pred_cat["label"] = pred_cat["alert_category"].map(ALERT_LABELS)

    fig_pred_cat = px.bar(
        pred_cat, x="predicted_risk", y="n",
        color="alert_category",
        color_discrete_map=ALERT_COLORS,
        labels={"predicted_risk": "Predicción modelo", "n": "N° estudiantes",
                "alert_category": "Categoría alerta"},
        height=320,
        barmode="stack"
    )
    fig_pred_cat.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0"),
        margin=dict(l=20, r=20, t=20, b=40)
    )
    st.plotly_chart(fig_pred_cat, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:#999; font-size:0.8em'>"
    "Vermont Early Warning System · EAFIT Maestría CDA 2026-1 · "
    "Andrés Velasco Hernández · Datos anonimizados"
    "</div>",
    unsafe_allow_html=True
)
