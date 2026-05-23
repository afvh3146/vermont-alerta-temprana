"""
Vermont Early Warning System — Dashboard Streamlit
Andrés Velasco Hernández | EAFIT Maestría CDA 2026-1
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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

ALERT_DESC = {
    "Riesgo Confirmado": "Modelo y T3 parcial coinciden. Intervención urgente.",
    "Punto Ciego":       "T3 muestra riesgo pero el modelo no lo detectó. Revisar con urgencia.",
    "Riesgo Teórico":    "Modelo detecta riesgo pero T3 aún no lo confirma. Monitoreo activo.",
    "Sin Riesgo":        "Sin señales de riesgo. Seguimiento rutinario.",
}

ALERT_ACCION = {
    "Riesgo Confirmado": "Intervención urgente",
    "Punto Ciego":       "Revisar con urgencia — no detectado por modelo",
    "Riesgo Teórico":    "Monitoreo activo",
    "Sin Riesgo":        "Seguimiento rutinario",
}

GRADO_MAP = {"X": 7, "Y": 8, "Z": 9}
GRADO_LABEL = {7: "X", 8: "Y", 9: "Z"}

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)
    df["seccion"] = df["section_anon"].str[-1]
    df["grado_label"] = df["grade"].map(GRADO_LABEL) + " " + df["seccion"]
    df["categoria"] = df["categoria"].fillna("Riesgo Teórico")
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏫 Vermont EWS")
    st.markdown("**Early Warning System**")
    st.markdown("Año lectivo 2025–26 · T1 + T2 + T3 parcial")
    st.divider()

    st.markdown("### LSC")
    solo_lsc = st.checkbox("Mostrar solo estudiantes LSC")

    st.divider()

    st.markdown("### Categorías")
    cats_activas = []
    for cat in ALERT_ORDER:
        checked = st.checkbox(
            f"{ALERT_EMOJI[cat]} {cat}",
            value=True,
            key=f"cb_{cat}"
        )
        if checked:
            cats_activas.append(cat)

    st.divider()
    metrics_placeholder = st.empty()

# ─────────────────────────────────────────────
# TÍTULO + SELECTOR DE GRADO
# ─────────────────────────────────────────────
st.markdown("# 🏫 Vermont Early Warning System")

col_grado, col_seccion = st.columns([2, 1])
with col_grado:
    grado_sel = st.radio(
        "Grado",
        ["Todos", "X", "Y", "Z"],
        horizontal=True,
        label_visibility="collapsed"
    )
with col_seccion:
    if grado_sel == "Todos":
        seccion_sel = st.selectbox("Sección", ["Todas", "A", "B"],
                                    label_visibility="collapsed")
    else:
        grado_num = GRADO_MAP[grado_sel]
        secciones_disp = ["Todas"] + sorted(
            df[df["grade"] == grado_num]["seccion"].unique().tolist()
        )
        seccion_sel = st.selectbox("Sección", secciones_disp,
                                    label_visibility="collapsed")

# ─────────────────────────────────────────────
# FILTROS GLOBALES
# ─────────────────────────────────────────────
if grado_sel == "Todos":
    df_g = df.copy()
else:
    df_g = df[df["grade"] == GRADO_MAP[grado_sel]].copy()

if seccion_sel != "Todas":
    df_g = df_g[df_g["seccion"] == seccion_sel]

if solo_lsc:
    df_g = df_g[df_g["marcador_LSC"] == 1]

df_filtrado = df_g[df_g["categoria"].isin(cats_activas)] if cats_activas else df_g.copy()

n_total    = len(df_filtrado)
n_criticos = (df_filtrado["categoria"] == "Riesgo Confirmado").sum()
n_ciegos   = (df_filtrado["categoria"] == "Punto Ciego").sum()

with metrics_placeholder:
    st.metric("Estudiantes", n_total)
    st.metric("🔴 Riesgo confirmado", n_criticos)
    st.metric("🟠 Punto ciego", n_ciegos)

grupo_texto = grado_sel if grado_sel != "Todos" else "Middle School"
if seccion_sel != "Todas":
    grupo_texto += f" · Sección {seccion_sel}"
if solo_lsc:
    grupo_texto += " · Solo LSC"
st.markdown(f"**{grupo_texto}** · {n_total} estudiantes · Año lectivo 2025–26")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
cat_highlight = "Ninguna"

def get_color(cat):
    if cat_highlight == "Ninguna":
        return ALERT_COLORS[cat]
    return ALERT_COLORS[cat] if cat == cat_highlight else "#cccccc"

def get_opacity(cat):
    if cat_highlight == "Ninguna":
        return 0.85
    return 0.92 if cat == cat_highlight else 0.2

def build_hover(row):
    lines = [
        f"<b>ID: {row['student_id']}</b>",
        f"Grado: {row['grado_label']}",
        f"Categoría: {ALERT_EMOJI.get(row['categoria'],'')} {row['categoria']}",
        f"Prob. riesgo (crítico): {row['proba_critical']*100:.0f}%",
        f"LSC: {'✓ Sí' if row.get('marcador_LSC', 0) == 1 else 'No'}",
        "──────────────",
        "<b>Materias con nota acumulada bajo 4.0:</b>"
    ]
    tiene_bajas = False
    for s in SUBJECTS:
        t1 = row.get(f"{s}_T1", np.nan)
        t2 = row.get(f"{s}_T2", np.nan)
        t3 = row.get(f"{s}_T3", np.nan)
        if not any(pd.isna([t1, t2, t3])):
            acum = t1*0.30 + t2*0.30 + t3*0.40
            if acum < 4.0:
                lines.append(f"  ⚠️ {SUBJECT_LABELS[s]}: acum {acum:.2f}")
                tiene_bajas = True
    if not tiene_bajas:
        lines.append("  ✓ Ninguna")
    return "<br>".join(lines)

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
# TAB 1
# ══════════════════════════════════════════════
with tab1:

    cols_m = st.columns(4)
    for i, cat in enumerate(ALERT_ORDER):
        n = (df_filtrado["categoria"] == cat).sum()
        pct = round(n / n_total * 100, 1) if n_total > 0 else 0
        color = get_color(cat)
        desc  = ALERT_DESC[cat]
        cols_m[i].markdown(f"""
        <div style="margin-bottom:8px">
            <span style="font-size:1.8em; font-weight:700; color:{color}">{n}</span>
            <span style="font-size:1em; color:{color}; margin-left:6px">
                {ALERT_EMOJI[cat]} {cat}
            </span>
            <span style="font-size:0.9em; color:#999; margin-left:6px">{pct}%</span><br>
            <span style="font-size:0.78em; color:#666; line-height:1.3">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    col_titulo, col_contraste = st.columns([3, 1])
    with col_titulo:
        st.markdown("#### Probabilidad de riesgo vs. Materias en bajo rendimiento")
    with col_contraste:
        cat_highlight = st.selectbox(
            "Destacar",
            ["Ninguna"] + ALERT_ORDER,
            label_visibility="collapsed",
            help="Resalta una categoría; el resto queda en gris"
        )

    df_sc = df_filtrado.copy()
    df_sc["hover_text"] = df_sc.apply(build_hover, axis=1)

    fig_sc = go.Figure()
    for cat in ALERT_ORDER:
        sub = df_sc[df_sc["categoria"] == cat]
        if sub.empty:
            continue
        color   = get_color(cat)
        opacity = get_opacity(cat)
        size    = 13 if (cat_highlight == "Ninguna" or cat == cat_highlight) else 9
        symbols  = sub["marcador_LSC"].map({1: "diamond", 0: "circle"})
        border_w = sub["marcador_LSC"].map({1: 2.5, 0: 0.8})
        border_c = sub["marcador_LSC"].map({1: "#000000", 0: "white"})
        sizes    = sub["marcador_LSC"].map({1: size + 3, 0: size})
        fig_sc.add_trace(go.Scatter(
            x=sub["proba_critical"],
            y=sub["n_bajo_acumulada"],
            mode="markers",
            name=f"{ALERT_EMOJI[cat]} {cat}",
            marker=dict(
                color=color, size=sizes, symbol=symbols,
                line=dict(width=border_w, color=border_c),
                opacity=opacity
            ),
            hovertext=sub["hover_text"],
            hoverinfo="text",
            showlegend=True
        ))

    fig_sc.add_vline(x=0.30, line_dash="dash", line_color="#e74c3c", line_width=1.5,
                     annotation_text="Umbral de riesgo (0.30)",
                     annotation_position="top right",
                     annotation_font_color="#e74c3c", annotation_font_size=11)
    fig_sc.add_hline(y=2.5, line_dash="dash", line_color="#888", line_width=1.5,
                     annotation_text="3 materias = pierde el año",
                     annotation_position="right", annotation_font_size=11)
    fig_sc.add_annotation(x=0.15, y=9.3, text="🟠 Punto ciego",
        showarrow=False, font=dict(color="#e67e22", size=11), opacity=0.8)
    fig_sc.add_annotation(x=0.75, y=9.3, text="🔴 Riesgo confirmado",
        showarrow=False, font=dict(color="#e74c3c", size=11), opacity=0.8)
    fig_sc.add_annotation(x=0.15, y=0.3, text="🟢 Sin riesgo",
        showarrow=False, font=dict(color="#27ae60", size=11), opacity=0.8)
    fig_sc.add_annotation(x=0.75, y=0.3, text="🔵 Riesgo teórico",
        showarrow=False, font=dict(color="#3498db", size=11), opacity=0.8)
    fig_sc.update_layout(
        height=520,
        xaxis_title="Probabilidad de riesgo (modelo)",
        yaxis_title="N° materias en bajo rendimiento",
        xaxis=dict(range=[-0.02, 1.02], gridcolor="#f0f0f0",
                   tickformat=".0%",
                   tickvals=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]),
        yaxis=dict(range=[-0.5, 10.5], gridcolor="#f0f0f0", dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=12)),
        margin=dict(l=50, r=20, t=60, b=50),
        plot_bgcolor="white", paper_bgcolor="white",
        hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#ddd")
    )
    st.plotly_chart(fig_sc, use_container_width=True)
    st.caption("◆ = estudiante con LSC (borde negro) · ● = sin LSC")

    col_bar, col_sec = st.columns(2)
    with col_bar:
        st.markdown("#### Distribución por categoría")
        cat_counts = (
            df_filtrado["categoria"].value_counts()
            .reindex(ALERT_ORDER).dropna().reset_index()
        )
        cat_counts.columns = ["categoria", "n"]
        fig_bar = go.Figure(go.Bar(
            x=cat_counts["n"],
            y=[f"{ALERT_EMOJI[c]} {c}" for c in cat_counts["categoria"]],
            orientation="h",
            marker_color=[get_color(c) for c in cat_counts["categoria"]],
            text=cat_counts["n"], textposition="outside"
        ))
        fig_bar.update_layout(
            height=240, xaxis_title="N° estudiantes",
            margin=dict(l=10, r=40, t=10, b=30),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(gridcolor="#f0f0f0")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_sec:
        if seccion_sel == "Todas" and grado_sel != "Todos":
            st.markdown("#### Por sección")
            sec_cat = (
                df_filtrado.groupby(["seccion", "categoria"])
                .size().reset_index(name="n")
            )
            fig_sec = px.bar(
                sec_cat, x="seccion", y="n", color="categoria",
                color_discrete_map={c: get_color(c) for c in ALERT_ORDER},
                labels={"seccion": "Sección", "n": "Estudiantes", "categoria": "Categoría"},
                height=240
            )
            fig_sec.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=40),
                plot_bgcolor="white", paper_bgcolor="white"
            )
            st.plotly_chart(fig_sec, use_container_width=True)
        elif grado_sel == "Todos":
            st.markdown("#### Por grado")
            grade_cat = (
                df_filtrado.groupby(["grade", "categoria"])
                .size().reset_index(name="n")
            )
            grade_cat["grado_str"] = grade_cat["grade"].map(GRADO_LABEL)
            fig_grade = px.bar(
                grade_cat, x="grado_str", y="n", color="categoria",
                color_discrete_map={c: get_color(c) for c in ALERT_ORDER},
                labels={"grado_str": "Grado", "n": "Estudiantes", "categoria": "Categoría"},
                height=240,
                category_orders={"grado_str": ["X", "Y", "Z"]}
            )
            fig_grade.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=40),
                plot_bgcolor="white", paper_bgcolor="white"
            )
            st.plotly_chart(fig_grade, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════
with tab2:

    st.markdown("#### Lista de estudiantes — urgentes primero · Haz clic en una fila para ver el perfil")

    df_tabla = df_filtrado.copy()
    df_tabla["cat_order"] = df_tabla["categoria"].map(
        {cat: i for i, cat in enumerate(ALERT_ORDER)}
    )
    df_tabla = df_tabla.sort_values("cat_order").reset_index(drop=True)

    cols_show = [
        "student_id", "grade", "seccion", "categoria",
        "pred_label", "avg_T1", "avg_T2",
        "n_bajo_acumulada", "marcador_LSC",
        "perfil", "n_f1", "n_f2", "total_absences"
    ]
    cols_show = [c for c in cols_show if c in df_tabla.columns]
    df_show = df_tabla[cols_show].copy()
    df_show["avg_T1"] = df_show["avg_T1"].round(2)
    df_show["avg_T2"] = df_show["avg_T2"].round(2)
    df_show["grade"] = df_show["grade"].map(GRADO_LABEL)
    df_show["marcador_LSC"] = df_show["marcador_LSC"].map({1: "✓", 0: ""})
    df_show["categoria"] = df_show["categoria"].apply(
        lambda x: f"{ALERT_EMOJI.get(x,'')} {x}"
    )
    df_show = df_show.rename(columns={
        "student_id":       "ID",
        "grade":            "Grado",
        "seccion":          "Secc.",
        "categoria":        "Categoría",
        "pred_label":       "Pred. modelo",
        "avg_T1":           "Prom. T1",
        "avg_T2":           "Prom. T2",
        "n_bajo_acumulada": "Mat. < 4.0",
        "marcador_LSC":     "LSC",
        "perfil":           "Perfil",
        "n_f1":             "F1",
        "n_f2":             "F2",
        "total_absences":   "Ausencias"
    })

    selection = st.dataframe(
        df_show,
        use_container_width=True,
        height=380,
        on_select="rerun",
        selection_mode="single-row"
    )

    selected_rows = selection.selection.rows
    if selected_rows:
        idx = selected_rows[0]
        row = df_tabla.iloc[idx]

        st.divider()
        cat   = row["categoria"]
        color = ALERT_COLORS.get(cat, "#888")
        st.markdown(f"""
        <div style="background:{color}22; border-left:5px solid {color};
                    padding:12px 16px; border-radius:8px; margin-bottom:16px">
            <b style="color:{color}">{ALERT_EMOJI.get(cat,'')} {cat}</b>
            <span style="font-size:0.85em; color:#444; margin-left:12px">
                {ALERT_ACCION.get(cat,'')}
            </span>
        </div>
        """, unsafe_allow_html=True)

        col_radar, col_mat = st.columns([1, 1])

        with col_radar:
            grade = int(row.get("grade", 9))
            if grade == 9:
                materias_ingles = {
                    "Science", "Mathematics", "Financial_Maths",
                    "ICT_STEM", "English", "Research_Methodology"
                }
            else:
                materias_ingles = {
                    "Science", "Mathematics", "Financial_Maths",
                    "ICT_STEM", "I_and_S", "English"
                }

            SUBJECTS_RADAR_9 = [
                "Science", "Mathematics", "Financial_Maths", "ICT_STEM",
                "I_and_S", "Research_Methodology", "English", "Mandarin",
                "Lengua_Castellana", "Physical_Education"
            ]
            SUBJECTS_RADAR_78 = [
                "Science", "Mathematics", "Financial_Maths", "ICT_STEM",
                "I_and_S", "English", "Mandarin",
                "Lengua_Castellana", "Physical_Education"
            ]
            subjects_orden = SUBJECTS_RADAR_9 if grade == 9 else SUBJECTS_RADAR_78
            subs_disp = [s for s in subjects_orden
                         if not pd.isna(row.get(f"{s}_T1", np.nan))]

            if subs_disp:
                highlight_ingles = st.checkbox(
                    "Resaltar materias en inglés",
                    value=False,
                    key=f"ing_{idx}"
                )

                labels  = [SUBJECT_LABELS[s] for s in subs_disp]
                t3a_v   = [row.get(f"{s}_T3", 0) or 0 for s in subs_disp]
                t3p_v   = [row.get(f"{s}_T3_pred", 0) or 0 for s in subs_disp]

                COLOR_ACTIVO = "#27ae60"
                COLOR_PRED   = "#a8d5b5"
                COLOR_MIN    = "#c0392b"

                t3a_plot = [
                    v * 0.12 if (highlight_ingles and s not in materias_ingles) else v
                    for v, s in zip(t3a_v, subs_disp)
                ]
                t3p_plot = [
                    v * 0.12 if (highlight_ingles and s not in materias_ingles) else v
                    for v, s in zip(t3p_v, subs_disp)
                ]

                fig_radar = go.Figure()

                fig_radar.add_trace(go.Scatterpolar(
                    r=[4.0] * (len(labels) + 1),
                    theta=labels + [labels[0]],
                    mode='lines', name='Mínimo (4.0)',
                    line=dict(color=COLOR_MIN, dash='dash', width=1.5),
                    showlegend=True, hoverinfo='skip'
                ))

                fig_radar.add_trace(go.Scatterpolar(
                    r=t3a_plot + [t3a_plot[0]],
                    theta=labels + [labels[0]],
                    fill='toself',
                    fillcolor='rgba(39,174,96,0.15)',
                    name='T3 actual',
                    line=dict(color=COLOR_ACTIVO, width=2.5),
                    showlegend=True,
                    hovertemplate='<b>%{theta}</b><br>T3 actual: %{r:.2f}<extra></extra>'
                ))

                fig_radar.add_trace(go.Scatterpolar(
                    r=t3p_plot + [t3p_plot[0]],
                    theta=labels + [labels[0]],
                    fill='toself',
                    fillcolor='rgba(168,213,181,0.15)',
                    name='T3 predicho',
                    line=dict(color=COLOR_PRED, dash='dot', width=2),
                    showlegend=True,
                    hovertemplate='<b>%{theta}</b><br>T3 pred: %{r:.2f}<extra></extra>'
                ))

                # Labels coloreados por contraste
                annotations = []
                n_subs = len(subs_disp)
                for i, (s, lbl) in enumerate(zip(subs_disp, labels)):
                    angle_deg = 90 - (360 / n_subs) * i
                    angle_rad = np.radians(angle_deg)
                    x = 0.5 + 0.44 * np.cos(angle_rad)
                    y = 0.5 + 0.44 * np.sin(angle_rad)
                    es_ingles = s in materias_ingles
                    color_lbl = "#333" if (not highlight_ingles or es_ingles) else "#cccccc"
                    bold = highlight_ingles and es_ingles
                    annotations.append(dict(
                        x=x, y=y,
                        xref='paper', yref='paper',
                        text=f"<b>{lbl}</b>" if bold else lbl,
                        showarrow=False,
                        font=dict(size=10, color=color_lbl),
                        xanchor='center', yanchor='middle'
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, range=[0, 7],
                            tickvals=[1,2,3,4,5,6,7],
                            tickfont=dict(size=9, color='#aaa'),
                            gridcolor='#ebebeb', linecolor='#ddd'
                        ),
                        angularaxis=dict(
                            tickfont=dict(size=1, color='rgba(0,0,0,0)'),
                            gridcolor='#ebebeb', linecolor='#ddd'
                        )
                    ),
                    annotations=annotations,
                    showlegend=True,
                    legend=dict(orientation='h', y=-0.18, font=dict(size=10)),
                    height=420,
                    margin=dict(l=60, r=60, t=40, b=80),
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        with col_mat:
            st.markdown("**Notas por materia**")
            rows_mat = []
            for s in SUBJECTS:
                t1 = row.get(f"{s}_T1", np.nan)
                if pd.isna(t1):
                    continue
                t2      = row.get(f"{s}_T2", np.nan)
                t3_pred = row.get(f"{s}_T3_pred", np.nan)
                t3_p10  = row.get(f"{s}_T3_p10", np.nan)
                t3_p90  = row.get(f"{s}_T3_p90", np.nan)
                min_t3  = row.get(f"{s}_min_T3", np.nan)
                t3_real = row.get(f"{s}_T3", np.nan)

                if not pd.isna(t3_pred) and not pd.isna(t3_p10) and not pd.isna(t3_p90):
                    amp = (t3_p90 - t3_p10) / 2
                    t3_pred_str = f"{t3_pred:.2f} ± {amp:.2f}"
                elif not pd.isna(t3_pred):
                    t3_pred_str = f"{t3_pred:.2f}"
                else:
                    t3_pred_str = "—"

                estado = ""
                if not pd.isna(t3_real) and t3_real < 4.0:
                    estado = "⚠️"
                elif not pd.isna(t3_pred) and t3_pred < 4.0:
                    estado = "🔸"

                rows_mat.append({
                    "":              estado,
                    "Materia":       SUBJECT_LABELS[s],
                    "T1":            round(t1, 2),
                    "T2":            round(t2, 2) if not pd.isna(t2) else "—",
                    "T3 actual":     round(t3_real, 2) if not pd.isna(t3_real) else "—",
                    "T3 pred. ±":    t3_pred_str,
                    "T3 mín.":       round(min_t3, 2) if not pd.isna(min_t3) else "—",
                })
            if rows_mat:
                st.dataframe(pd.DataFrame(rows_mat), use_container_width=True,
                             hide_index=True, height=360)
            st.caption("⚠️ T3 actual bajo 4.0 · 🔸 T3 predicho bajo 4.0")
    else:
        st.info("Haz clic en una fila de la tabla para ver el perfil del estudiante.")

# ══════════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════════
with tab3:

    st.markdown("#### Promedio del grupo por asignatura")
    st.caption("Selecciona los trimestres que quieres ver")

    col_t1, col_t2, col_t3p, col_t3a = st.columns(4)
    with col_t1:
        show_t1 = st.checkbox("T1", value=True)
    with col_t2:
        show_t2 = st.checkbox("T2", value=True)
    with col_t3p:
        show_t3p = st.checkbox("T3 predicho", value=True)
    with col_t3a:
        show_t3a = st.checkbox("T3 actual", value=True)

    subs_data = []
    for s in SUBJECTS:
        label = SUBJECT_LABELS[s]
        for show, t, col, color, solid in [
            (show_t1,  "T1",          f"{s}_T1",      "#5dade2", True),
            (show_t2,  "T2",          f"{s}_T2",      "#1a5276", True),
            (show_t3p, "T3 predicho", f"{s}_T3_pred", "#27ae60", False),
            (show_t3a, "T3 actual",   f"{s}_T3",      "#27ae60", True),
        ]:
            if col in df_filtrado.columns:
                vals = df_filtrado[col].dropna()
                if not vals.empty:
                    subs_data.append({
                        "Materia":   label,
                        "Trimestre": t,
                        "Promedio":  round(vals.mean(), 2),
                        "Activo":    show,
                        "Color":     color,
                        "Sólido":    solid,
                    })

    if subs_data:
        df_subs = pd.DataFrame(subs_data)
        trimestres_config = [
            ("T1",          "#5dade2", True),
            ("T2",          "#1a5276", True),
            ("T3 predicho", "#27ae60", False),
            ("T3 actual",   "#27ae60", True),
        ]
        show_map = {
            "T1":          show_t1,
            "T2":          show_t2,
            "T3 predicho": show_t3p,
            "T3 actual":   show_t3a,
        }

        fig_subs = go.Figure()
        for t, color, solid in trimestres_config:
            sub = df_subs[df_subs["Trimestre"] == t]
            if sub.empty:
                continue
            activo     = show_map[t]
            color_real = color if activo else "#cccccc"
            opac       = 0.9 if activo else 0.3

            if solid:
                fig_subs.add_trace(go.Bar(
                    name=t, x=sub["Materia"], y=sub["Promedio"],
                    marker_color=color_real, opacity=opac,
                    text=sub["Promedio"].astype(str),
                    textposition="outside", textfont=dict(size=9),
                ))
            else:
                fig_subs.add_trace(go.Bar(
                    name=t, x=sub["Materia"], y=sub["Promedio"],
                    marker=dict(
                        color=color_real, opacity=opac,
                        pattern=dict(shape="/", size=6, solidity=0.4,
                                     fgcolor=color_real, bgcolor="white")
                    ),
                    text=sub["Promedio"].astype(str),
                    textposition="outside", textfont=dict(size=9),
                ))

        fig_subs.add_hline(y=4.0, line_dash="dash", line_color="red", line_width=1.5,
                            annotation_text="Mín. aprobación (4.0)",
                            annotation_font_color="red", annotation_font_size=11)
        fig_subs.update_layout(
            height=460, barmode="group",
            xaxis_title="Materia", yaxis_title="Promedio",
            yaxis=dict(range=[0, 7.8], gridcolor="#f0f0f0"),
            xaxis=dict(tickangle=-30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=40, r=20, t=50, b=80)
        )
        st.plotly_chart(fig_subs, use_container_width=True)

    st.divider()

    st.markdown("#### Materias con promedio acumulado bajo el mínimo")
    st.caption("Promedio acumulado = T1×0.30 + T2×0.30 + T3×0.40 · Solo muestra materias en riesgo o cerca (< 4.5)")

    resumen_rows = []
    for s in SUBJECTS:
        col_t1s = f"{s}_T1"
        col_t2s = f"{s}_T2"
        col_t3s = f"{s}_T3"
        col_t3p = f"{s}_T3_pred"
        if not all(c in df_filtrado.columns for c in [col_t1s, col_t2s, col_t3s]):
            continue
        df_sub = df_filtrado[[col_t1s, col_t2s, col_t3s]].dropna()
        if df_sub.empty:
            continue
        df_sub = df_sub.copy()
        df_sub["acum"] = df_sub[col_t1s]*0.30 + df_sub[col_t2s]*0.30 + df_sub[col_t3s]*0.40
        prom_acum = round(df_sub["acum"].mean(), 2)
        prom_t3p  = round(df_filtrado[col_t3p].mean(), 2) if col_t3p in df_filtrado.columns else None
        resumen_rows.append({
            "Materia":         SUBJECT_LABELS[s],
            "Prom. acumulado": prom_acum,
            "Prom. T3 pred.":  prom_t3p,
        })

    df_res = pd.DataFrame(resumen_rows)
    df_res_show = df_res[df_res["Prom. acumulado"] < 4.5].sort_values("Prom. acumulado")

    if not df_res_show.empty:
        fig_horiz = go.Figure()
        fig_horiz.add_trace(go.Bar(
            name="Promedio acumulado",
            y=df_res_show["Materia"],
            x=df_res_show["Prom. acumulado"],
            orientation="h",
            marker_color=["#e74c3c" if v < 4.0 else "#f39c12"
                          for v in df_res_show["Prom. acumulado"]],
            text=df_res_show["Prom. acumulado"].astype(str),
            textposition="outside"
        ))
        fig_horiz.add_trace(go.Scatter(
            name="T3 predicho (grupo)",
            y=df_res_show["Materia"],
            x=df_res_show["Prom. T3 pred."],
            mode="markers",
            marker=dict(color="#3498db", size=12, symbol="diamond",
                        line=dict(width=1.5, color="white"))
        ))
        fig_horiz.add_vline(x=4.0, line_dash="dash", line_color="red", line_width=1.5,
                             annotation_text="4.0 mínimo",
                             annotation_font_color="red",
                             annotation_position="top right")
        fig_horiz.update_layout(
            height=max(200, len(df_res_show) * 55 + 80),
            xaxis_title="Promedio acumulado",
            xaxis=dict(range=[0, 7.5], gridcolor="#f0f0f0"),
            yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=80, t=40, b=40)
        )
        st.plotly_chart(fig_horiz, use_container_width=True)
        st.caption("🔴 Bajo mínimo · 🟠 Cerca del mínimo (< 4.5) · ◆ T3 predicho del grupo")
    else:
        st.success("Ninguna materia tiene promedio acumulado bajo o cerca del mínimo en el grupo seleccionado.")

# ══════════════════════════════════════════════
# TAB 4
# ══════════════════════════════════════════════
with tab4:

    st.markdown("#### Desempeño del modelo — Random Forest optimizado")
    st.caption("Entrenado en 2024–25 (117 est.) · Umbral: 0.30 · Aplicado sobre 2025–26 (149 est.)")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modelo", "Random Forest")
    c2.metric("Umbral", "0.30")
    c3.metric("Train", "117 est.")
    c4.metric("Predict", "149 est.")

    st.divider()

    col_pred, col_conf = st.columns(2)
    with col_pred:
        st.markdown("#### Predicción del modelo vs. categoría final")
        pred_cat = (
            df_filtrado.groupby(["pred_label", "categoria"])
            .size().reset_index(name="n")
        )
        fig_pc = px.bar(
            pred_cat, x="pred_label", y="n", color="categoria",
            color_discrete_map={c: get_color(c) for c in ALERT_ORDER},
            labels={"pred_label": "Predicción modelo",
                    "n": "N° estudiantes", "categoria": "Categoría final"},
            height=340, barmode="stack"
        )
        fig_pc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_pc, use_container_width=True)

    with col_conf:
        st.markdown("#### Confianza del modelo por categoría")
        df_conf = df_filtrado[["categoria", "confianza"]].copy()
        df_conf["confianza_pct"] = df_conf["confianza"] * 100
        fig_conf = px.box(
            df_conf, x="categoria", y="confianza_pct", color="categoria",
            color_discrete_map={c: get_color(c) for c in ALERT_ORDER},
            labels={"categoria": "Categoría", "confianza_pct": "Confianza (%)"},
            height=340
        )
        fig_conf.update_layout(
            showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickangle=-20), yaxis=dict(gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=20, b=80)
        )
        fig_conf.add_hline(y=50, line_dash="dash", line_color="gray",
                            annotation_text="50% umbral")
        st.plotly_chart(fig_conf, use_container_width=True)

    if "incertidumbre_promedio" in df_filtrado.columns:
        st.divider()
        st.markdown("#### Estudiantes con mayor incertidumbre del modelo")
        st.caption("Más difíciles de clasificar — requieren revisión directa.")
        df_inc = df_filtrado[[
            "student_id", "grade", "seccion",
            "categoria", "confianza", "incertidumbre_promedio"
        ]].copy()
        df_inc = df_inc.sort_values("incertidumbre_promedio", ascending=False)
        df_inc["confianza"] = (df_inc["confianza"] * 100).round(0).astype(str) + "%"
        df_inc["incertidumbre_promedio"] = df_inc["incertidumbre_promedio"].round(3)
        df_inc["grade"] = df_inc["grade"].map(GRADO_LABEL)
        df_inc["categoria"] = df_inc["categoria"].apply(
            lambda x: f"{ALERT_EMOJI.get(x,'')} {x}"
        )
        df_inc = df_inc.rename(columns={
            "student_id": "ID", "grade": "Grado", "seccion": "Secc.",
            "categoria": "Categoría", "confianza": "Confianza",
            "incertidumbre_promedio": "Incertidumbre T3"
        })
        st.dataframe(df_inc.head(20), use_container_width=True, hide_index=True)

st.divider()
st.markdown(
    "<div style='text-align:center; color:#999; font-size:0.8em'>"
    "Vermont Early Warning System · EAFIT Maestría CDA 2026-1 · "
    "Andrés Velasco Hernández · Datos anonimizados"
    "</div>",
    unsafe_allow_html=True
)
