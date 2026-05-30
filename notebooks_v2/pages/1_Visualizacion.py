"""
Vermont EWS — Página 1: Visualización
Tabs: Semáforo general | Detalle por estudiante | Por asignatura
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Visualización · Vermont EWS", page_icon="📊", layout="wide")

# ── Constantes ────────────────────────────────────────────────────────────────
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
    "Science": "Science", "I_and_S": "I&S",
    "Mathematics": "Mathematics", "English": "English",
    "Lengua_Castellana": "Lengua Cast.", "Mandarin": "Mandarin",
    "Financial_Maths": "Fin. Maths", "ICT_STEM": "ICT/STEM",
    "Physical_Education": "Phys. Ed.", "Research_Methodology": "Research"
}
ALERT_ORDER  = ["Riesgo Confirmado", "Punto Ciego", "Riesgo Teórico", "Sin Riesgo"]
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
    "Riesgo Confirmado": "Intervención urgente",
    "Punto Ciego":       "Revisar con urgencia — no detectado por modelo",
    "Riesgo Teórico":    "Monitoreo activo",
    "Sin Riesgo":        "Seguimiento rutinario",
}
GRADO_MAP   = {"X": 7, "Y": 8, "Z": 9}
GRADO_LABEL = {7: "7°", 8: "8°", 9: "9°"}

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)
    df["seccion"] = df["section_anon"].str[-1]
    df["grado_str"] = df["grade"].map(GRADO_LABEL)
    df["categoria"] = df["categoria"].fillna("Riesgo Teórico")
    return df

df = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Visualización")
    st.divider()

    st.markdown("**Filtrar por grado**")
    grado_sel = st.radio("Grado", ["Todos", "X", "Y", "Z"], horizontal=True,
                         label_visibility="collapsed")

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
    st.markdown("**Filtrar categorías**")
    cats_sel = st.multiselect(
        "Categorías visibles", ALERT_ORDER, default=ALERT_ORDER,
        label_visibility="collapsed"
    )
    df_g = df_g[df_g["categoria"].isin(cats_sel)]

    st.divider()
    lsc_sel = st.checkbox("Solo estudiantes LSC", value=False)
    if lsc_sel and "marcador_LSC" in df_g.columns:
        df_g = df_g[df_g["marcador_LSC"] == 1]

    st.divider()
    n_total = len(df_g)
    n_riesgo = df_g["categoria"].isin(["Riesgo Confirmado", "Punto Ciego"]).sum()
    st.metric("Estudiantes visibles", n_total)
    st.metric("Con riesgo activo", n_riesgo)

# ── Header ─────────────────────────────────────────────────────────────────────
label_grado = f"Grado {grado_sel}" if grado_sel != "Todos" else "Todos los grados"
label_sec   = f" · Sección {seccion_sel}" if seccion_sel != "Todas" else ""
st.markdown(f"# 📊 Visualización · {label_grado}{label_sec}")
fecha = df["fecha_corte"].iloc[0] if "fecha_corte" in df.columns else "Mayo 2026"
st.caption(f"Corte: {fecha} · {n_total} estudiantes · {n_riesgo} con riesgo activo")
st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🚦 Semáforo general", "👤 Detalle por estudiante", "📚 Por asignatura"])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — SEMÁFORO GENERAL
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Mapa de riesgo por cuadrante")
    st.caption("Eje X: promedio T2 · Eje Y: promedio T1 · Color: categoría de alerta · Tamaño: índice disciplinario")

    if df_g.empty:
        st.info("No hay estudiantes con los filtros seleccionados.")
    else:
        # Scatter cuadrantes
        fig_scatter = go.Figure()
        for cat in ALERT_ORDER:
            sub = df_g[df_g["categoria"] == cat]
            if sub.empty:
                continue
            sizes = 10 + sub["indice_disciplinario"].fillna(0).clip(0, 20) * 2 \
                if "indice_disciplinario" in sub.columns else 14

            hover_text = (
                sub["student_id"].astype(str) + "<br>" +
                "Grado: " + sub["grado_str"].fillna("") + " · Sec: " + sub["seccion"].fillna("") + "<br>" +
                "Avg T1: " + sub["avg_T1"].round(2).astype(str) + "<br>" +
                "Avg T2: " + sub["avg_T2"].round(2).astype(str) + "<br>" +
                "Categoría: " + cat
            )

            fig_scatter.add_trace(go.Scatter(
                x=sub["avg_T2"], y=sub["avg_T1"],
                mode="markers",
                name=f"{ALERT_EMOJI[cat]} {cat}",
                marker=dict(color=ALERT_COLORS[cat], size=sizes, opacity=0.8,
                            line=dict(width=1, color="white")),
                text=hover_text, hovertemplate="%{text}<extra></extra>"
            ))

        # Líneas de umbral (nota mínima = 4.0)
        fig_scatter.add_hline(y=4.0, line_dash="dash", line_color="#aaa",
                              annotation_text="Mínimo T1", annotation_position="left")
        fig_scatter.add_vline(x=4.0, line_dash="dash", line_color="#aaa",
                              annotation_text="Mínimo T2", annotation_position="top")

        fig_scatter.update_layout(
            height=420, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Promedio T2", range=[1, 7.2], gridcolor="#f0f0f0"),
            yaxis=dict(title="Promedio T1", range=[1, 7.2], gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=50, r=20, t=50, b=50)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Barras de conteo por categoría
        st.markdown("### Conteo por categoría de alerta")
        cat_counts = df_g["categoria"].value_counts().reindex(ALERT_ORDER, fill_value=0)
        fig_bar = go.Figure()
        for cat in ALERT_ORDER:
            fig_bar.add_trace(go.Bar(
                x=[cat], y=[cat_counts[cat]],
                name=cat,
                marker_color=ALERT_COLORS[cat],
                text=[cat_counts[cat]], textposition="outside",
                showlegend=False
            ))
        fig_bar.update_layout(
            height=300, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title=""), yaxis=dict(title="Estudiantes", gridcolor="#f0f0f0"),
            margin=dict(l=40, r=20, t=30, b=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Tabla resumen por categoría
        st.markdown("### Resumen por categoría")
        resumen = []
        for cat in ALERT_ORDER:
            sub = df_g[df_g["categoria"] == cat]
            if sub.empty:
                continue
            resumen.append({
                "Categoría": f"{ALERT_EMOJI[cat]} {cat}",
                "N": len(sub),
                "% del grupo": f"{round(len(sub)/len(df_g)*100,1)}%",
                "Avg T2 promedio": round(sub["avg_T2"].mean(), 2) if "avg_T2" in sub else "—",
                "Acción sugerida": ALERT_ACCION[cat]
            })
        if resumen:
            st.dataframe(pd.DataFrame(resumen), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2 — DETALLE POR ESTUDIANTE
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Seleccionar estudiante")

    if df_g.empty:
        st.info("No hay estudiantes con los filtros seleccionados.")
    else:
        # Selector: ordenado por riesgo descendente
        cat_order_map = {c: i for i, c in enumerate(ALERT_ORDER)}
        df_sorted = df_g.copy()
        df_sorted["_ord"] = df_sorted["categoria"].map(cat_order_map)
        df_sorted = df_sorted.sort_values("_ord")

        opciones = {
            row["student_id"]: (
                f"{ALERT_EMOJI.get(row['categoria'], '⚪')} {row['student_id']} · "
                f"Grado {row.get('grado_str','?')} Sec {row.get('seccion','?')} · "
                f"{row['categoria']}"
            )
            for _, row in df_sorted.iterrows()
        }
        sel_id = st.selectbox("Estudiante", list(opciones.keys()),
                              format_func=lambda x: opciones[x])

        row = df_g[df_g["student_id"] == sel_id].iloc[0]
        cat = row["categoria"]
        color = ALERT_COLORS.get(cat, "#aaa")

        st.divider()

        # Ficha de resumen
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"""
        <div style="background:{color}15;border-left:5px solid {color};
                    padding:12px;border-radius:8px;text-align:center">
            <div style="font-size:1.8em">{ALERT_EMOJI.get(cat,'⚪')}</div>
            <div style="font-size:0.85em;color:{color};font-weight:700">{cat}</div>
        </div>""", unsafe_allow_html=True)

        c2.metric("Promedio T1", f"{row.get('avg_T1', '—'):.2f}" if pd.notna(row.get("avg_T1")) else "—")
        c3.metric("Promedio T2", f"{row.get('avg_T2', '—'):.2f}" if pd.notna(row.get("avg_T2")) else "—",
                  delta=f"{row.get('tendencia_general', 0):.2f}" if pd.notna(row.get("tendencia_general")) else None)
        c4.metric("Asistencia", f"{row.get('pct_asistencia', '—'):.1f}%" if pd.notna(row.get("pct_asistencia")) else "—")

        st.markdown("&nbsp;")
        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.markdown("**Indicadores complementarios**")
            indicadores = []
            if pd.notna(row.get("n_f1")): indicadores.append({"Indicador": "Seguimientos F1", "Valor": int(row["n_f1"])})
            if pd.notna(row.get("n_f2")): indicadores.append({"Indicador": "Seguimientos F2", "Valor": int(row["n_f2"])})
            if pd.notna(row.get("indice_disciplinario")): indicadores.append({"Indicador": "Índice disciplinario", "Valor": round(row["indice_disciplinario"], 2)})
            if pd.notna(row.get("total_absences")): indicadores.append({"Indicador": "Ausencias totales", "Valor": int(row["total_absences"])})
            if pd.notna(row.get("late")): indicadores.append({"Indicador": "Llegadas tarde", "Valor": int(row["late"])})
            lsc_val = "Sí" if row.get("marcador_LSC") == 1 else "No"
            indicadores.append({"Indicador": "Marcador LSC", "Valor": lsc_val})
            if pd.notna(row.get("perfil")): indicadores.append({"Indicador": "Perfil cluster", "Valor": row["perfil"]})
            if pd.notna(row.get("pred_label")): indicadores.append({"Indicador": "Predicción modelo", "Valor": row["pred_label"]})
            if pd.notna(row.get("proba_critical")): indicadores.append({"Indicador": "P(crítico)", "Valor": f"{row['proba_critical']:.2%}"})

            st.dataframe(pd.DataFrame(indicadores), use_container_width=True, hide_index=True)

        with col_b:
            # Radar de notas por asignatura (T1 vs T2)
            avail_subjects = [s for s in SUBJECTS if f"{s}_T1" in row.index and f"{s}_T2" in row.index]
            if avail_subjects:
                labels = [SUBJECT_LABELS.get(s, s) for s in avail_subjects]
                vals_T1 = [row.get(f"{s}_T1", 0) or 0 for s in avail_subjects]
                vals_T2 = [row.get(f"{s}_T2", 0) or 0 for s in avail_subjects]

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals_T1 + [vals_T1[0]], theta=labels + [labels[0]],
                    fill="toself", name="T1",
                    line_color="#3498db", fillcolor="rgba(52,152,219,0.15)"
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals_T2 + [vals_T2[0]], theta=labels + [labels[0]],
                    fill="toself", name="T2",
                    line_color="#e67e22", fillcolor="rgba(230,126,34,0.15)"
                ))
                # Línea de mínimo
                fig_radar.add_trace(go.Scatterpolar(
                    r=[4.0] * (len(labels) + 1), theta=labels + [labels[0]],
                    mode="lines", name="Mínimo (4.0)",
                    line=dict(color="#e74c3c", dash="dash", width=1.5)
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(range=[0, 7], tickvals=[1,2,3,4,5,6,7])),
                    showlegend=True, height=380,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15),
                    margin=dict(l=40, r=40, t=40, b=60)
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        # Tabla de notas por asignatura
        st.markdown("**Notas por asignatura**")
        notas_rows = []
        for s in SUBJECTS:
            t1 = row.get(f"{s}_T1")
            t2 = row.get(f"{s}_T2")
            t3 = row.get(f"{s}_T3")
            min_t3 = row.get(f"{s}_min_T3")
            if pd.isna(t1) and pd.isna(t2):
                continue
            delta = round(t2 - t1, 2) if pd.notna(t1) and pd.notna(t2) else None
            trend = ("↑" if delta > 0 else "↓" if delta < 0 else "=") if delta is not None else "—"
            notas_rows.append({
                "Asignatura": SUBJECT_LABELS.get(s, s),
                "T1": f"{t1:.2f}" if pd.notna(t1) else "—",
                "T2": f"{t2:.2f}" if pd.notna(t2) else "—",
                "Δ T1→T2": f"{delta:+.2f} {trend}" if delta is not None else "—",
                "T3 real": f"{t3:.2f}" if pd.notna(t3) else "—",
                "Mín T3": f"{min_t3:.2f}" if pd.notna(min_t3) else "—",
                "Bajo mínimo": "⚠️" if pd.notna(t2) and t2 < 4.0 else ""
            })
        if notas_rows:
            st.dataframe(pd.DataFrame(notas_rows), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3 — POR ASIGNATURA
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Promedios por asignatura")
    st.caption("Promedio grupal en T1 y T2. La línea roja marca el mínimo de aprobación (4.0).")

    if df_g.empty:
        st.info("No hay estudiantes con los filtros seleccionados.")
    else:
        avail = [s for s in SUBJECTS if f"{s}_T1" in df_g.columns and f"{s}_T2" in df_g.columns]
        labels = [SUBJECT_LABELS.get(s, s) for s in avail]
        avg_T1 = [df_g[f"{s}_T1"].mean() for s in avail]
        avg_T2 = [df_g[f"{s}_T2"].mean() for s in avail]

        fig_subj = go.Figure()
        fig_subj.add_trace(go.Bar(
            name="Promedio T1", x=labels, y=avg_T1,
            marker_color="#3498db", text=[f"{v:.2f}" for v in avg_T1],
            textposition="outside"
        ))
        fig_subj.add_trace(go.Bar(
            name="Promedio T2", x=labels, y=avg_T2,
            marker_color="#e67e22", text=[f"{v:.2f}" for v in avg_T2],
            textposition="outside"
        ))
        fig_subj.add_hline(y=4.0, line_dash="dash", line_color="#e74c3c",
                           annotation_text="Mínimo 4.0", annotation_position="right")
        fig_subj.update_layout(
            barmode="group", height=420,
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="", tickangle=-30, gridcolor="#f0f0f0"),
            yaxis=dict(title="Nota promedio", range=[0, 7.8], gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=50, r=50, t=50, b=90)
        )
        st.plotly_chart(fig_subj, use_container_width=True)

        # Mapa de calor: promedio T2 por asignatura × categoría
        st.markdown("### Promedio T2 por asignatura y categoría de alerta")
        st.caption("Permite ver en qué asignaturas cada grupo de riesgo tiene mayor dificultad.")

        heatmap_rows = []
        for cat in ALERT_ORDER:
            sub = df_g[df_g["categoria"] == cat]
            if sub.empty:
                continue
            row_data = {"Categoría": f"{ALERT_EMOJI[cat]} {cat}"}
            for s in avail:
                col = f"{s}_T2"
                row_data[SUBJECT_LABELS.get(s, s)] = round(sub[col].mean(), 2) if col in sub.columns else None
            heatmap_rows.append(row_data)

        if heatmap_rows:
            df_heat = pd.DataFrame(heatmap_rows).set_index("Categoría")
            fig_heat = go.Figure(go.Heatmap(
                z=df_heat.values,
                x=df_heat.columns.tolist(),
                y=df_heat.index.tolist(),
                colorscale=[[0, "#e74c3c"], [0.5, "#f39c12"], [1, "#2ecc71"]],
                zmin=1, zmax=7,
                text=df_heat.values.round(2),
                texttemplate="%{text}",
                hovertemplate="Categoría: %{y}<br>Asignatura: %{x}<br>Promedio T2: %{z:.2f}<extra></extra>"
            ))
            fig_heat.update_layout(
                height=280,
                xaxis=dict(tickangle=-30),
                margin=dict(l=160, r=20, t=30, b=90)
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        # Tabla: materias con más estudiantes bajo mínimo en T2
        st.markdown("### Materias con más estudiantes bajo el mínimo en T2")
        bajo_min = []
        for s in avail:
            col = f"{s}_T2"
            if col not in df_g.columns:
                continue
            n_bajo = (df_g[col] < 4.0).sum()
            pct    = round(n_bajo / len(df_g) * 100, 1)
            avg    = round(df_g[col].mean(), 2)
            bajo_min.append({
                "Asignatura": SUBJECT_LABELS.get(s, s),
                "Bajo mínimo (T2)": n_bajo,
                "% del grupo": f"{pct}%",
                "Promedio T2": avg
            })
        bajo_min_df = pd.DataFrame(bajo_min).sort_values("Bajo mínimo (T2)", ascending=False)
        st.dataframe(bajo_min_df, use_container_width=True, hide_index=True)
