"""
Vermont Early Warning System — Dashboard Streamlit
Andrés Felipe Velasco Hernández | EAFIT Maestría CDA 2026-1
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
    "Science":              "Science",
    "I_and_S":              "I&S",
    "Mathematics":          "Mathematics",
    "English":              "English",
    "Lengua_Castellana":    "Lengua Cast.",
    "Mandarin":             "Mandarin",
    "Financial_Maths":      "Fin. Maths",
    "ICT_STEM":             "ICT/STEM",
    "Physical_Education":   "Phys. Ed.",
    "Research_Methodology": "Research"
}

# 4 categorías definitivas
ALERT_ORDER = [
    "Riesgo Confirmado",
    "Punto Ciego",
    "Riesgo Teórico",
    "Sin Riesgo",
]

ALERT_COLORS = {
    "Riesgo Confirmado": "#e74c3c",
    "Punto Ciego":       "#e67e22",
    "Riesgo Teórico":    "#3498db",
    "Sin Riesgo":        "#2ecc71",
}

ALERT_EMOJI = {
    "Riesgo Confirmado": "🔴",
    "Punto Ciego":       "🟠",
    "Riesgo Teórico":    "🔵",
    "Sin Riesgo":        "🟢",
}

ALERT_ACCION = {
    "Riesgo Confirmado": "Intervención urgente — modelo y T3 alineados",
    "Punto Ciego":       "Urgente — modelo no detectó pero T3 confirma riesgo",
    "Riesgo Teórico":    "Monitoreo activo — modelo detecta riesgo, T3 no confirma aún",
    "Sin Riesgo":        "Seguimiento rutinario",
}

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)
    df["seccion"] = df["section_anon"].str[-1]
    df["grado_label"] = df["grade"].astype(str) + "° " + df["seccion"]
    df["categoria"] = df["categoria"].fillna("Riesgo Teórico")
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR — FILTROS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏫 Vermont EWS")
    st.markdown("**Early Warning System**")
    st.markdown("Año lectivo 2025–26 · T1 + T2 + T3 parcial")
    st.divider()

    st.markdown("### Filtrar por grupo")
    grado_sel = st.selectbox("Grado", ["Todos", "7°", "8°", "9°"])

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
        format_func=lambda x: f"{ALERT_EMOJI[x]} {x}"
    )
    if cats_sel:
        df_filtrado = df_filtrado[df_filtrado["categoria"].isin(cats_sel)]

    st.divider()
    n_total    = len(df_filtrado)
    n_criticos = (df_filtrado["categoria"] == "Riesgo Confirmado").sum()
    n_ciegos   = (df_filtrado["categoria"] == "Punto Ciego").sum()
    st.metric("Estudiantes", n_total)
    st.metric("🔴 Riesgo confirmado", n_criticos)
    st.metric("🟠 Punto ciego", n_ciegos)

# ─────────────────────────────────────────────
# TÍTULO
# ─────────────────────────────────────────────
st.markdown("# 🏫 Vermont Early Warning System")
grupo_texto = grado_sel if grado_sel != "Todos" else "Middle School"
if seccion_sel != "Todas":
    grupo_texto += f" · Sección {seccion_sel}"
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
    cols = st.columns(4)
    for i, cat in enumerate(ALERT_ORDER):
        n = (df_filtrado["categoria"] == cat).sum()
        cols[i].metric(f"{ALERT_EMOJI[cat]} {cat}", n)

    st.divider()

    col_scatter, col_bar = st.columns([3, 2])

    with col_scatter:
        st.markdown("#### Promedio T2 vs. Materias bajo 4.0")
        st.caption("Cada punto es un estudiante. Hover para ver detalles.")

        df_sc = df_filtrado.copy()
        df_sc["LSC_sym"] = df_sc["marcador_LSC"].map({1: "diamond", 0: "circle"})
        df_sc["hover"] = (
            "ID: " + df_sc["student_id"].astype(str) +
            "<br>Grado: " + df_sc["grado_label"] +
            "<br>Promedio T2: " + df_sc["avg_T2"].round(2).astype(str) +
            "<br>Materias bajo 4.0: " + df_sc["n_bajo_acumulada"].astype(str) +
            "<br>Tendencia: " + df_sc["tendencia_general"].round(2).astype(str) +
            "<br>LSC: " + df_sc["marcador_LSC"].map({1: "Sí", 0: "No"}) +
            "<br>Confianza: " + (df_sc["confianza"] * 100).round(0).astype(str) + "%" +
            "<br>T3 confirma: " + df_sc["t3_confirma_riesgo"].astype(str)
        )

        fig_sc = go.Figure()
        for cat in ALERT_ORDER:
            sub = df_sc[df_sc["categoria"] == cat]
            if sub.empty:
                continue
            fig_sc.add_trace(go.Scatter(
                x=sub["avg_T2"],
                y=sub["n_bajo_acumulada"],
                mode="markers",
                name=f"{ALERT_EMOJI[cat]} {cat}",
                marker=dict(
                    color=ALERT_COLORS[cat],
                    size=10,
                    line=dict(width=1, color="white"),
                    symbol=sub["LSC_sym"]
                ),
                hovertext=sub["hover"],
                hoverinfo="text"
            ))

        fig_sc.add_hline(y=2.5, line_dash="dash", line_color="gray",
                         annotation_text="3 mat. = pierde el año",
                         annotation_position="right")
        fig_sc.add_vline(x=4.0, line_dash="dash", line_color="gray",
                         annotation_text="Promedio mínimo",
                         annotation_position="top")

        fig_sc.update_layout(
            height=420,
            xaxis_title="Promedio acumulado T2",
            yaxis_title="N° materias bajo 4.0",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=40, r=20, t=40, b=40),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        fig_sc.update_xaxes(range=[1, 7.5], gridcolor="#f0f0f0")
        fig_sc.update_yaxes(range=[-0.5, 10.5], gridcolor="#f0f0f0", dtick=1)
        st.plotly_chart(fig_sc, use_container_width=True)
        st.caption("◆ = estudiante con LSC | ● = sin LSC")

    with col_bar:
        st.markdown("#### Distribución por categoría")
        cat_counts = (
            df_filtrado["categoria"]
            .value_counts()
            .reindex(ALERT_ORDER)
            .dropna()
            .reset_index()
        )
        cat_counts.columns = ["categoria", "n"]

        fig_bar = go.Figure(go.Bar(
            x=cat_counts["n"],
            y=[f"{ALERT_EMOJI[c]} {c}" for c in cat_counts["categoria"]],
            orientation="h",
            marker_color=[ALERT_COLORS[c] for c in cat_counts["categoria"]],
            text=cat_counts["n"],
            textposition="outside"
        ))
        fig_bar.update_layout(
            height=280,
            xaxis_title="N° estudiantes",
            margin=dict(l=10, r=40, t=20, b=40),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        fig_bar.update_xaxes(gridcolor="#f0f0f0")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Por grado si se ve todo
        if grado_sel == "Todos":
            st.markdown("#### Por grado")
            grade_cat = (
                df_filtrado.groupby(["grade", "categoria"])
                .size().reset_index(name="n")
            )
            grade_cat["grado_str"] = grade_cat["grade"].astype(str) + "°"
            fig_grade = px.bar(
                grade_cat, x="grado_str", y="n",
                color="categoria",
                color_discrete_map=ALERT_COLORS,
                labels={"grado_str": "Grado", "n": "Estudiantes",
                        "categoria": "Categoría"},
                height=260
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

    df_tabla = df_filtrado.copy()
    df_tabla["cat_order"] = df_tabla["categoria"].map(
        {cat: i for i, cat in enumerate(ALERT_ORDER)}
    )
    df_tabla = df_tabla.sort_values("cat_order")

    cols_show = [
        "student_id", "grade", "seccion", "categoria",
        "pred_label", "confianza", "avg_T1", "avg_T2",
        "tendencia_general", "n_bajo_acumulada",
        "t3_confirma_riesgo", "marcador_LSC",
        "perfil", "n_f1", "n_f2", "total_absences"
    ]
    cols_show = [c for c in cols_show if c in df_tabla.columns]
    df_show = df_tabla[cols_show].copy()
    df_show["confianza"] = (df_show["confianza"] * 100).round(0).astype(str) + "%"
    df_show["avg_T1"] = df_show["avg_T1"].round(2)
    df_show["avg_T2"] = df_show["avg_T2"].round(2)
    df_show["tendencia_general"] = df_show["tendencia_general"].round(2)
    df_show["marcador_LSC"] = df_show["marcador_LSC"].map({1: "✓", 0: ""})
    df_show["categoria"] = df_show["categoria"].apply(
        lambda x: f"{ALERT_EMOJI.get(x,'')} {x}"
    )

    df_show = df_show.rename(columns={
        "student_id":        "ID",
        "grade":             "Grado",
        "seccion":           "Secc.",
        "categoria":         "Categoría",
        "pred_label":        "Pred. modelo",
        "confianza":         "Confianza",
        "avg_T1":            "Prom. T1",
        "avg_T2":            "Prom. T2",
        "tendencia_general": "Tendencia",
        "n_bajo_acumulada":  "Mat. < 4.0",
        "t3_confirma_riesgo":"T3 confirma",
        "marcador_LSC":      "LSC",
        "perfil":            "Perfil",
        "n_f1":              "F1",
        "n_f2":              "F2",
        "total_absences":    "Ausencias"
    })
    st.dataframe(df_show, use_container_width=True, height=380)

    st.divider()
    st.markdown("#### Perfil individual")

    ids_disponibles = df_filtrado["student_id"].tolist()
    if ids_disponibles:
        sel_id = st.selectbox("Seleccionar estudiante", ids_disponibles)
        row = df_filtrado[df_filtrado["student_id"] == sel_id].iloc[0]

        col_info, col_radar = st.columns([1, 2])

        with col_info:
            cat = row["categoria"]
            color = ALERT_COLORS.get(cat, "#888")
            accion = ALERT_ACCION.get(cat, "")
            st.markdown(f"""
            <div style="background:{color}22; border-left:5px solid {color};
                        padding:16px; border-radius:8px; margin-bottom:12px">
                <b style="color:{color}">{ALERT_EMOJI.get(cat,'')} {cat}</b><br>
                <span style="font-size:0.85em">{accion}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**Grado:** {row['grade']}° {row['seccion']}")
            st.markdown(f"**Promedio T1:** {row['avg_T1']:.2f}")
            st.markdown(f"**Promedio T2:** {row['avg_T2']:.2f}")
            st.markdown(f"**Tendencia:** {row['tendencia_general']:+.2f}")
            st.markdown(f"**Materias bajo 4.0:** {int(row['n_bajo_acumulada'])}")
            st.markdown(f"**Confianza modelo:** {row['confianza']*100:.0f}%")
            st.markdown(f"**T3 confirma riesgo:** {'Sí' if row['t3_confirma_riesgo'] else 'No'}")
            lsc = "✓ Sí" if row.get("marcador_LSC", 0) == 1 else "No"
            st.markdown(f"**LSC:** {lsc}")
            if pd.notna(row.get("perfil")):
                st.markdown(f"**Perfil cluster:** {row['perfil']}")
            st.markdown(f"**F1 / F2:** {int(row.get('n_f1',0))} / {int(row.get('n_f2',0))}")
            st.markdown(f"**Ausencias:** {int(row.get('total_absences',0))}")

        with col_radar:
            subs_disp = [s for s in SUBJECTS
                         if not pd.isna(row.get(f"{s}_T1", np.nan))]
            if subs_disp:
                labels = [SUBJECT_LABELS[s] for s in subs_disp]
                t1_v = [row.get(f"{s}_T1", 0) or 0 for s in subs_disp]
                t2_v = [row.get(f"{s}_T2", 0) or 0 for s in subs_disp]
                t3_v = [row.get(f"{s}_T3_pred", 0) or 0 for s in subs_disp]

                fig_radar = go.Figure()
                for vals, name, clr in [
                    (t1_v, "T1 real",    "#3498db"),
                    (t2_v, "T2 real",    "#9b59b6"),
                    (t3_v, "T3 pred.",   "#e74c3c"),
                ]:
                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals + [vals[0]],
                        theta=labels + [labels[0]],
                        fill="toself", name=name,
                        line_color=clr, fillcolor=clr, opacity=0.25
                    ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=[4.0] * (len(labels) + 1),
                    theta=labels + [labels[0]],
                    mode="lines", name="Mín. aprobación",
                    line=dict(color="red", dash="dash", width=1.5)
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 7])),
                    showlegend=True, height=380,
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        # Tabla por materia
        st.markdown("#### Notas y predicción T3 por materia")
        rows_mat = []
        for s in SUBJECTS:
            t1 = row.get(f"{s}_T1", np.nan)
            if pd.isna(t1):
                continue
            t3_pred = row.get(f"{s}_T3_pred", np.nan)
            t3_p10  = row.get(f"{s}_T3_p10", np.nan)
            t3_p90  = row.get(f"{s}_T3_p90", np.nan)
            min_t3  = row.get(f"{s}_min_T3", np.nan)
            t3_real = row.get(f"{s}_T3", np.nan)

            intervalo = (
                f"[{t3_p10:.1f} – {t3_p90:.1f}]"
                if not pd.isna(t3_p10) else "—"
            )
            rows_mat.append({
                "Materia":        SUBJECT_LABELS[s],
                "T1":             round(t1, 2),
                "T2":             round(row.get(f"{s}_T2", np.nan), 2) if not pd.isna(row.get(f"{s}_T2", np.nan)) else "—",
                "T3 parcial":     round(t3_real, 2) if not pd.isna(t3_real) else "—",
                "T3 predicho":    round(t3_pred, 2) if not pd.isna(t3_pred) else "—",
                "IC [P10–P90]":   intervalo,
                "T3 mín. necesario": round(min_t3, 2) if not pd.isna(min_t3) else "—",
            })
        if rows_mat:
            st.dataframe(pd.DataFrame(rows_mat), use_container_width=True,
                         hide_index=True)

# ══════════════════════════════════════════════
# TAB 3 — POR ASIGNATURA
# ══════════════════════════════════════════════
with tab3:

    st.markdown("#### Promedio por asignatura (T1, T2, T3 predicho)")
    subs_data = []
    for s in SUBJECTS:
        for t, col in [("T1", f"{s}_T1"), ("T2", f"{s}_T2"),
                       ("T3 pred.", f"{s}_T3_pred")]:
            if col in df_filtrado.columns:
                vals = df_filtrado[col].dropna()
                if not vals.empty:
                    subs_data.append({
                        "Materia": SUBJECT_LABELS[s],
                        "Trimestre": t,
                        "Promedio": round(vals.mean(), 2)
                    })

    if subs_data:
        fig_subs = px.bar(
            pd.DataFrame(subs_data), x="Materia", y="Promedio",
            color="Trimestre", barmode="group",
            color_discrete_map={"T1": "#3498db", "T2": "#9b59b6",
                                 "T3 pred.": "#e74c3c"},
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
    st.markdown("#### Materias con más estudiantes en riesgo (T3 predicho < 4.0)")
    riesgo_rows = []
    for s in SUBJECTS:
        col = f"{s}_T3_pred"
        if col in df_filtrado.columns:
            n_bajo = (df_filtrado[col] < 4.0).sum()
            n_tot  = df_filtrado[col].notna().sum()
            if n_tot > 0:
                riesgo_rows.append({
                    "Materia": SUBJECT_LABELS[s],
                    "N bajo 4.0": int(n_bajo),
                    "% del grupo": round(n_bajo / n_tot * 100, 1)
                })

    df_riesgo = pd.DataFrame(riesgo_rows).sort_values("N bajo 4.0",
                                                        ascending=False)
    if not df_riesgo.empty:
        fig_riesgo = go.Figure(go.Bar(
            x=df_riesgo["N bajo 4.0"],
            y=df_riesgo["Materia"],
            orientation="h",
            marker_color="#e74c3c",
            text=df_riesgo["% del grupo"].astype(str) + "%",
            textposition="outside"
        ))
        fig_riesgo.update_layout(
            height=360,
            xaxis_title="N° estudiantes con T3 predicho < 4.0",
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(gridcolor="#f0f0f0"),
            margin=dict(l=10, r=60, t=20, b=40)
        )
        st.plotly_chart(fig_riesgo, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — MODELO PREDICTIVO
# ══════════════════════════════════════════════
with tab4:

    st.markdown("#### Desempeño del modelo — Random Forest optimizado")
    st.caption("Entrenado en 2024–25 (117 est.) · Umbral producción: 0.30 · Aplicado sobre 2025–26 (149 est.)")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modelo", "Random Forest")
    c2.metric("Umbral", "0.30")
    c3.metric("Train", "117 est.")
    c4.metric("Predict", "149 est.")

    st.divider()

    col_pred, col_conf = st.columns(2)

    with col_pred:
        st.markdown("#### Predicción del modelo vs. categoría final")
        st.caption("La categoría final cruza predicción del modelo con T3 parcial.")
        pred_cat = (
            df_filtrado.groupby(["pred_label", "categoria"])
            .size().reset_index(name="n")
        )
        fig_pc = px.bar(
            pred_cat, x="pred_label", y="n",
            color="categoria",
            color_discrete_map=ALERT_COLORS,
            labels={"pred_label": "Predicción modelo",
                    "n": "N° estudiantes",
                    "categoria": "Categoría final"},
            height=340, barmode="stack"
        )
        fig_pc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_pc, use_container_width=True)

    with col_conf:
        st.markdown("#### Distribución de confianza por categoría")
        df_conf = df_filtrado[["categoria", "confianza"]].copy()
        df_conf["confianza_pct"] = df_conf["confianza"] * 100

        fig_conf = px.box(
            df_conf, x="categoria", y="confianza_pct",
            color="categoria",
            color_discrete_map=ALERT_COLORS,
            labels={"categoria": "Categoría",
                    "confianza_pct": "Confianza (%)"},
            height=340
        )
        fig_conf.update_layout(
            showlegend=False,
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickangle=-20),
            yaxis=dict(gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=20, b=80)
        )
        fig_conf.add_hline(y=50, line_dash="dash", line_color="gray",
                            annotation_text="50% umbral")
        st.plotly_chart(fig_conf, use_container_width=True)

    st.divider()
    st.markdown("#### Incertidumbre del modelo por estudiante")
    st.caption("Mayor incertidumbre = más difícil de clasificar. Estos estudiantes requieren revisión directa.")

    if "incertidumbre_promedio" in df_filtrado.columns:
        df_inc = df_filtrado[["student_id", "grade", "seccion",
                               "categoria", "confianza",
                               "incertidumbre_promedio"]].copy()
        df_inc = df_inc.sort_values("incertidumbre_promedio", ascending=False)
        df_inc["confianza"] = (df_inc["confianza"] * 100).round(0).astype(str) + "%"
        df_inc["incertidumbre_promedio"] = df_inc["incertidumbre_promedio"].round(3)
        df_inc["categoria"] = df_inc["categoria"].apply(
            lambda x: f"{ALERT_EMOJI.get(x,'')} {x}"
        )
        df_inc = df_inc.rename(columns={
            "student_id":            "ID",
            "grade":                 "Grado",
            "seccion":               "Secc.",
            "categoria":             "Categoría",
            "confianza":             "Confianza",
            "incertidumbre_promedio":"Incertidumbre T3"
        })
        st.dataframe(df_inc.head(20), use_container_width=True,
                     hide_index=True)

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
