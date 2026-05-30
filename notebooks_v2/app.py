"""
Vermont Early Warning System — Inicio
Andrés Velasco Hernández | EAFIT Maestría CDA 2026-1
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── Navegación multipágina ─────────────────────────────────────
pg = st.navigation([
    st.Page("app.py",                    title="🏫 Inicio",         default=True),
    st.Page("pages/1_Visualizacion.py",  title="📊 Visualización"),
    st.Page("pages/2_Modelo.py",         title="🤖 Modelo"),
    st.Page("pages/3_Pipeline.py",       title="⚙️ Pipeline"),
    st.Page("pages/4_Decisiones.py",     title="🎯 Decisiones"),
])
pg.run()

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

ALERT_ORDER  = ["Riesgo Confirmado","Punto Ciego","Riesgo Teórico","Sin Riesgo"]
ALERT_COLORS = {"Riesgo Confirmado":"#e74c3c","Punto Ciego":"#e67e22",
                "Riesgo Teórico":"#3498db","Sin Riesgo":"#2ecc71"}
ALERT_EMOJI  = {"Riesgo Confirmado":"🔴","Punto Ciego":"🟠",
                "Riesgo Teórico":"🔵","Sin Riesgo":"🟢"}
ALERT_DESC   = {
    "Riesgo Confirmado": "Modelo y T3 parcial coinciden. Intervención urgente.",
    "Punto Ciego":       "T3 muestra riesgo pero el modelo no lo detectó.",
    "Riesgo Teórico":    "Modelo detecta riesgo pero T3 aún no lo confirma.",
    "Sin Riesgo":        "Sin señales de riesgo. Seguimiento rutinario.",
}
GRADO_LABEL = {7:"7°", 8:"8°", 9:"9°"}
PAGES = {
    "📊 Visualización": "Semáforo general, detalle por estudiante y análisis por asignatura.",
    "🤖 Modelo":        "Comparativa de modelos ML, feature importance y predicción T3.",
    "⚙️ Pipeline":      "Arquitectura de datos, ciclo de vida y flujo del pipeline.",
    "🎯 Decisiones":    "Análisis aclaratorio para toma de decisiones de intervención.",
}

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)
    df["seccion"] = df["section_anon"].str[-1]
    df["categoria"] = df["categoria"].fillna("Riesgo Teórico")
    df["grado_str"] = df["grade"].map(GRADO_LABEL)
    return df

df = load_data()

with st.sidebar:
    st.markdown("## 🏫 Vermont EWS")
    st.markdown("**Early Warning System**")
    st.markdown("Año lectivo 2025–26")
    st.divider()
    for page, desc in PAGES.items():
        st.markdown(f"**{page}**")
        st.caption(desc)

st.markdown("# 🏫 Vermont Early Warning System")
st.markdown("Sistema de alerta temprana · Middle School · Vermont School Medellín · 2025–26")
fecha = df["fecha_corte"].iloc[0] if "fecha_corte" in df.columns else "Mayo 2026"
st.caption(f"Último corte: {fecha} · {len(df)} estudiantes analizados")
st.divider()

st.markdown("### Estado actual del Middle School")
cols = st.columns(4)
for i, cat in enumerate(ALERT_ORDER):
    n   = (df["categoria"] == cat).sum()
    pct = round(n / len(df) * 100, 1)
    c   = ALERT_COLORS[cat]
    cols[i].markdown(f"""
    <div style="background:{c}15;border-left:5px solid {c};
                padding:14px 16px;border-radius:8px;min-height:110px">
        <div style="font-size:2.2em;font-weight:800;color:{c}">{n}</div>
        <div style="font-size:1em;color:{c}">{ALERT_EMOJI[cat]} {cat}</div>
        <div style="font-size:0.78em;color:#888">{pct}% del total</div>
        <div style="font-size:0.75em;color:#666;margin-top:6px">{ALERT_DESC[cat]}</div>
    </div>""", unsafe_allow_html=True)

st.divider()
st.markdown("### Distribución por grado")

grade_cat = df.groupby(["grado_str","categoria"]).size().reset_index(name="n")
fig = go.Figure()
for cat in ALERT_ORDER:
    sub = grade_cat[grade_cat["categoria"] == cat]
    if sub.empty: continue
    fig.add_trace(go.Bar(
        name=f"{ALERT_EMOJI[cat]} {cat}",
        x=sub["grado_str"], y=sub["n"],
        marker_color=ALERT_COLORS[cat],
        text=sub["n"], textposition="inside"
    ))
fig.update_layout(
    barmode="stack", height=300,
    xaxis=dict(categoryorder="array", categoryarray=["7°","8°","9°"]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=40,r=20,t=50,b=40),
    yaxis=dict(gridcolor="#f0f0f0")
)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("### ¿Qué encontrarás en cada sección?")
col1, col2 = st.columns(2)
items = list(PAGES.items())
for col, pair in [(col1, items[:2]), (col2, items[2:])]:
    with col:
        for page, desc in pair:
            st.markdown(f"""
            <div style="background:#f8f9fa;border-radius:8px;
                        padding:14px 16px;margin-bottom:12px">
                <div style="font-size:1.1em;font-weight:700">{page}</div>
                <div style="font-size:0.85em;color:#555;margin-top:4px">{desc}</div>
            </div>""", unsafe_allow_html=True)

st.divider()
st.caption("Vermont EWS · Andrés Velasco Hernández · EAFIT MCDA 2026-1 · SI7006/SI7007/SI7009")
