"""
Vermont EWS — Página 4: Decisiones
Tabs: ¿Dónde está el riesgo? | ¿A quién intervengo esta semana?
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Decisiones · Vermont EWS", page_icon="🎯", layout="wide")

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
    "Science": "Science", "I_and_S": "I&S", "Mathematics": "Mathematics",
    "English": "English", "Lengua_Castellana": "Lengua Cast.",
    "Mandarin": "Mandarin", "Financial_Maths": "Fin. Maths",
    "ICT_STEM": "ICT/STEM", "Physical_Education": "Phys. Ed.",
    "Research_Methodology": "Research"
}
ALERT_ORDER  = ["Riesgo Confirmado", "Punto Ciego", "Riesgo Teórico", "Sin Riesgo"]
ALERT_COLORS = {
    "Riesgo Confirmado": "#e74c3c", "Punto Ciego": "#e67e22",
    "Riesgo Teórico":    "#3498db", "Sin Riesgo":  "#2ecc71",
}
ALERT_EMOJI = {
    "Riesgo Confirmado": "🔴", "Punto Ciego": "🟠",
    "Riesgo Teórico":    "🔵", "Sin Riesgo":  "🟢",
}
GRADO_MAP   = {"X": 7, "Y": 8, "Z": 9}
GRADO_LABEL = {7: "X", 8: "Y", 9: "Z"}

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)
    df["seccion"]   = df["section_anon"].str[-1]
    df["grado_str"] = df["grade"].map(GRADO_LABEL)
    df["grado_label"] = df["grado_str"] + " " + df["seccion"]
    df["categoria"] = df["categoria"].fillna("Riesgo Teórico")
    return df

df = load_data()

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Decisiones")
    st.divider()
    st.markdown("**Filtrar por grado**")
    grado_sel = st.radio("Grado", ["Todos", "X", "Y", "Z"],
                         horizontal=True, label_visibility="collapsed")
    if grado_sel == "Todos":
        df_g = df.copy()
        st.markdown("**Filtrar por sección**")
        seccion_sel = st.selectbox("Sección", ["Todas", "A", "B"],
                                   label_visibility="collapsed")
    else:
        grado_num = GRADO_MAP[grado_sel]
        df_g = df[df["grade"] == grado_num].copy()
        secciones_disp = ["Todas"] + sorted(
            df[df["grade"] == grado_num]["seccion"].unique().tolist()
        )
        st.markdown("**Filtrar por sección**")
        seccion_sel = st.selectbox("Sección", secciones_disp,
                                   label_visibility="collapsed")
    if seccion_sel != "Todas":
        df_g = df_g[df_g["seccion"] == seccion_sel]

    st.divider()
    n_total  = len(df_g)
    n_riesgo = df_g["categoria"].isin(["Riesgo Confirmado", "Punto Ciego"]).sum()
    st.metric("Estudiantes", n_total)
    st.metric("Con riesgo activo", n_riesgo)

grupo_texto = grado_sel if grado_sel != "Todos" else "Middle School"
if seccion_sel != "Todas":
    grupo_texto += f" · Sección {seccion_sel}"

st.markdown("# 🎯 Decisiones")
st.markdown(f"**{grupo_texto}** · {n_total} estudiantes")
st.divider()

tab1, tab2 = st.tabs(["📍 ¿Dónde está el riesgo?", "📋 ¿A quién intervengo esta semana?"])

# ══════════════════════════════════════════════
# TAB 1 — ¿DÓNDE ESTÁ EL RIESGO?
# ══════════════════════════════════════════════
with tab1:

    st.markdown("### Materias detonantes vs. acumuladoras")
    st.caption(
        "**Detonante:** materia con más estudiantes bajo 4.0 en T3 real. "
        "**Acumuladora:** materia cuyo promedio acumulado (T1×0.30 + T2×0.30 + T3×0.40) "
        "está bajo 4.0."
    )

    avail = [s for s in SUBJECTS
             if f"{s}_T3" in df_g.columns and f"{s}_T1" in df_g.columns and f"{s}_T2" in df_g.columns]

    det_rows = []
    for s in avail:
        # Detonante: bajo 4.0 en T3 real
        df_t3 = df_g[f"{s}_T3"].dropna()
        n_bajo_t3 = (df_t3 < 4.0).sum()

        # Acumuladora: nota acumulada bajo 4.0
        df_sub = df_g[[f"{s}_T1", f"{s}_T2", f"{s}_T3"]].dropna()
        if not df_sub.empty:
            acum = df_sub[f"{s}_T1"]*0.30 + df_sub[f"{s}_T2"]*0.30 + df_sub[f"{s}_T3"]*0.40
            n_acum_riesgo = (acum < 4.0).sum()
            prom_acum = round(acum.mean(), 2)
        else:
            n_acum_riesgo = 0
            prom_acum = None

        pct_t3 = round(n_bajo_t3 / len(df_g) * 100, 1) if len(df_g) > 0 else 0

        det_rows.append({
            "Materia":         SUBJECT_LABELS[s],
            "Bajo 4.0 en T3":  n_bajo_t3,
            "% grupo":         f"{pct_t3}%",
            "Acum. en riesgo": n_acum_riesgo,
            "Prom. acumulado": prom_acum,
        })

    df_det = pd.DataFrame(det_rows).sort_values("Bajo 4.0 en T3", ascending=False)

    if df_det.empty:
        st.info("No hay datos de T3 disponibles para el grupo seleccionado.")
    else:
        fig_det = go.Figure()
        fig_det.add_trace(go.Bar(
            name="Bajo 4.0 en T3 (detonante)",
            x=df_det["Materia"],
            y=df_det["Bajo 4.0 en T3"],
            marker_color="#e74c3c",
            text=df_det["Bajo 4.0 en T3"],
            textposition="outside"
        ))
        fig_det.add_trace(go.Bar(
            name="Acumulado en riesgo",
            x=df_det["Materia"],
            y=df_det["Acum. en riesgo"],
            marker_color="#f39c12",
            text=df_det["Acum. en riesgo"],
            textposition="outside"
        ))
        fig_det.update_layout(
            barmode="group", height=380,
            xaxis=dict(tickangle=-30, gridcolor="#f0f0f0"),
            yaxis=dict(title="N° estudiantes", gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=40, r=20, t=50, b=90)
        )
        st.plotly_chart(fig_det, use_container_width=True)

        st.markdown("**Detalle por materia**")
        st.dataframe(df_det, use_container_width=True, hide_index=True)

    st.divider()

    # ── Comparativa por sección ───────────────
    st.markdown("### N° estudiantes en riesgo por sección")
    st.caption("Categorías de riesgo activo: Riesgo Confirmado + Punto Ciego")

    if grado_sel == "Todos":
        # Mostrar por grado cuando no hay filtro de grado
        riesgo_grado = (
            df_g[df_g["categoria"].isin(["Riesgo Confirmado", "Punto Ciego"])]
            .groupby(["grado_str", "categoria"])
            .size().reset_index(name="n")
        )
        fig_sec = go.Figure()
        for cat in ["Riesgo Confirmado", "Punto Ciego"]:
            sub = riesgo_grado[riesgo_grado["categoria"] == cat]
            if sub.empty:
                continue
            fig_sec.add_trace(go.Bar(
                name=f"{ALERT_EMOJI[cat]} {cat}",
                x=sub["grado_str"], y=sub["n"],
                marker_color=ALERT_COLORS[cat],
                text=sub["n"], textposition="outside"
            ))
        fig_sec.update_layout(
            barmode="group", height=320,
            xaxis=dict(title="Grado", categoryorder="array",
                       categoryarray=["X", "Y", "Z"]),
            yaxis=dict(title="N° estudiantes", gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=40, r=20, t=50, b=50)
        )
        st.plotly_chart(fig_sec, use_container_width=True)
    else:
        secciones = sorted(df_g["seccion"].unique().tolist())
        if len(secciones) < 2:
            st.info("Solo hay una sección disponible para este filtro.")
        else:
            riesgo_sec = (
                df_g[df_g["categoria"].isin(["Riesgo Confirmado", "Punto Ciego"])]
                .groupby(["seccion", "categoria"])
                .size().reset_index(name="n")
            )
            fig_sec = go.Figure()
            for cat in ["Riesgo Confirmado", "Punto Ciego"]:
                sub = riesgo_sec[riesgo_sec["categoria"] == cat]
                if sub.empty:
                    continue
                fig_sec.add_trace(go.Bar(
                    name=f"{ALERT_EMOJI[cat]} {cat}",
                    x=sub["seccion"], y=sub["n"],
                    marker_color=ALERT_COLORS[cat],
                    text=sub["n"], textposition="outside"
                ))
            fig_sec.update_layout(
                barmode="group", height=320,
                xaxis=dict(title="Sección"),
                yaxis=dict(title="N° estudiantes", gridcolor="#f0f0f0"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=40, r=20, t=50, b=50)
            )
            st.plotly_chart(fig_sec, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — ¿A QUIÉN INTERVENGO ESTA SEMANA?
# ══════════════════════════════════════════════
with tab2:

    st.markdown("### Curva de ganancia acumulada")
    st.caption(
        "¿Cuántos estudiantes en riesgo real capturo si intervengo solo los N más prioritarios? "
        "El modelo ordena por probabilidad de riesgo — la curva muestra la eficiencia de esa priorización."
    )

    df_gain = df_g.copy()
    df_gain["es_riesgo"] = df_gain["categoria"].isin(
        ["Riesgo Confirmado", "Punto Ciego"]
    ).astype(int)
    df_gain = df_gain.sort_values("proba_critical", ascending=False).reset_index(drop=True)
    df_gain["rank"]       = df_gain.index + 1
    df_gain["gain"]       = df_gain["es_riesgo"].cumsum()
    df_gain["gain_pct"]   = df_gain["gain"] / df_gain["es_riesgo"].sum() * 100

    total_riesgo = df_gain["es_riesgo"].sum()

    fig_gain = go.Figure()
    fig_gain.add_trace(go.Scatter(
        x=df_gain["rank"], y=df_gain["gain_pct"],
        mode="lines", name="Modelo (RF)",
        line=dict(color="#e74c3c", width=2.5)
    ))
    fig_gain.add_trace(go.Scatter(
        x=[0, len(df_gain)], y=[0, 100],
        mode="lines", name="Baseline aleatorio",
        line=dict(color="#aaa", dash="dash", width=1.5)
    ))
    fig_gain.add_trace(go.Scatter(
        x=[0, total_riesgo, len(df_gain)], y=[0, 100, 100],
        mode="lines", name="Modelo perfecto",
        line=dict(color="#2ecc71", dash="dot", width=1.5)
    ))
    fig_gain.update_layout(
        height=400,
        xaxis=dict(title="N° estudiantes intervenidos", gridcolor="#f0f0f0"),
        yaxis=dict(title="% estudiantes en riesgo capturados",
                   range=[0, 105], gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=50)
    )
    st.plotly_chart(fig_gain, use_container_width=True)

    st.divider()

    st.markdown("### Lista priorizada de intervención")
    st.caption("Ajusta cuántos estudiantes puedes atender esta semana.")

    max_est  = min(40, len(df_g))
    capacidad = st.slider(
        "Capacidad de intervención (N estudiantes)",
        min_value=1, max_value=max_est, value=min(15, max_est),
        help="Arrastra para ajustar cuántos estudiantes priorizarás esta semana"
    )

    capturados  = df_gain.head(capacidad)["es_riesgo"].sum()
    pct_captura = round(capturados / total_riesgo * 100, 1) if total_riesgo > 0 else 0

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Estudiantes a intervenir", capacidad)
    col_b.metric("En riesgo real capturados", capturados)
    col_c.metric("% del riesgo total cubierto", f"{pct_captura}%")

    st.markdown("&nbsp;")

    df_prior = df_gain.head(capacidad).copy()
    cols_show = ["rank", "student_id", "grado_label", "categoria",
                 "proba_critical", "n_bajo_acumulada", "marcador_LSC"]
    cols_show = [c for c in cols_show if c in df_prior.columns]
    df_prior_show = df_prior[cols_show].copy()
    df_prior_show["categoria"] = df_prior_show["categoria"].apply(
        lambda x: f"{ALERT_EMOJI.get(x,'')} {x}"
    )
    df_prior_show["proba_critical"] = df_prior_show["proba_critical"].apply(
        lambda x: f"{x:.0%}"
    )
    df_prior_show["marcador_LSC"] = df_prior_show["marcador_LSC"].map({1: "✓", 0: ""})
    df_prior_show = df_prior_show.rename(columns={
        "rank":            "Prioridad",
        "student_id":      "ID",
        "grado_label":     "Grado",
        "categoria":       "Categoría",
        "proba_critical":  "P(crítico)",
        "n_bajo_acumulada":"Mat. < 4.0",
        "marcador_LSC":    "LSC"
    })

    st.markdown(f"**Top {capacidad} estudiantes a intervenir — ordenados por riesgo**")
    st.dataframe(df_prior_show, use_container_width=True, hide_index=True, height=420)
    st.caption("Ordenado por probabilidad de riesgo crítico (modelo RF, umbral 0.30)")
