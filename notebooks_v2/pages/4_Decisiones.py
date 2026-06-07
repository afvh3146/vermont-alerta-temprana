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

IMPORTANCIA_MODELO = {
    "Mathematics":          0.0936 + 0.0279,
    "I_and_S":              0.0504 + 0.0411,
    "Lengua_Castellana":    0.0327 + 0.0000,
    "English":              0.0191 + 0.0000,
    "Mandarin":             0.0218 + 0.0000,
    "Science":              0.0000,
    "Financial_Maths":      0.0000,
    "ICT_STEM":             0.0000,
    "Physical_Education":   0.0000,
    "Research_Methodology": 0.0000,
}

MATERIAS_INGLES = {
    "Science", "I_and_S", "Mathematics", "English",
    "Financial_Maths", "ICT_STEM", "Research_Methodology"
}

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)
    df["seccion"]     = df["section_anon"].str[-1]
    df["grado_str"]   = df["grade"].map(GRADO_LABEL)
    df["grado_label"] = df["grado_str"] + " " + df["seccion"]
    df["categoria"]   = df["categoria"].fillna("Riesgo Teórico")
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

    st.markdown("### Materias críticas — estudiantes bajo 4.0 en T3")
    st.caption(
        "Selecciona las categorías para ver cuántos estudiantes de cada grupo "
        "tienen bajo rendimiento por materia"
    )

    avail = [s for s in SUBJECTS
             if f"{s}_T3" in df_g.columns and f"{s}_T1" in df_g.columns
             and f"{s}_T2" in df_g.columns]

    MATERIAS_INGLES = {
        "Science", "I_and_S", "Mathematics", "English",
        "Financial_Maths", "ICT_STEM", "Research_Methodology"
    }
    IMPORTANCIA_MODELO = {
        "Mathematics":          round(0.0936 + 0.0279, 4),
        "I_and_S":              round(0.0504 + 0.0411, 4),
        "Lengua_Castellana":    0.0327,
        "English":              0.0191,
        "Mandarin":             0.0218,
        "Science":              0.0,
        "Financial_Maths":      0.0,
        "ICT_STEM":             0.0,
        "Physical_Education":   0.0,
        "Research_Methodology": 0.0,
    }

    # ── Checkboxes de categoría ───────────────
    st.markdown("**Mostrar estudiantes de:**")
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        show_confirmado = st.checkbox(
            f"{ALERT_EMOJI['Riesgo Confirmado']} Confirmado", value=True,
            key="mat_confirmado"
        )
    with col_c2:
        show_ciego = st.checkbox(
            f"{ALERT_EMOJI['Punto Ciego']} Punto Ciego", value=True,
            key="mat_ciego"
        )
    with col_c3:
        show_teorico = st.checkbox(
            f"{ALERT_EMOJI['Riesgo Teórico']} Teórico", value=True,
            key="mat_teorico"
        )
    with col_c4:
        show_sinriesgo = st.checkbox(
            f"{ALERT_EMOJI['Sin Riesgo']} Sin Riesgo", value=False,
            key="mat_sinriesgo"
        )

    cats_activas = []
    if show_confirmado: cats_activas.append("Riesgo Confirmado")
    if show_ciego:      cats_activas.append("Punto Ciego")
    if show_teorico:    cats_activas.append("Riesgo Teórico")
    if show_sinriesgo:  cats_activas.append("Sin Riesgo")

    if not cats_activas:
        st.info("Selecciona al menos una categoría.")
    else:
        df_filtro_cat = df_g[df_g["categoria"].isin(cats_activas)]

        mat_rows = []
        for s in avail:
            col_t3 = f"{s}_T3"
            n_bajo = int((df_filtro_cat[col_t3].dropna() < 4.0).sum())
            if n_bajo == 0:
                continue
            mat_rows.append({
                "Materia":     SUBJECT_LABELS[s],
                "_s":          s,
                "N bajo T3":   n_bajo,
                "Importancia": IMPORTANCIA_MODELO.get(s, 0.0),
                "En inglés":   s in MATERIAS_INGLES,
                "pct":         round(n_bajo / len(df_filtro_cat) * 100, 1)
                               if len(df_filtro_cat) > 0 else 0,
            })

        if not mat_rows:
            st.info("No hay estudiantes con T3 bajo 4.0 en las categorías seleccionadas.")
        else:
            df_mat = pd.DataFrame(mat_rows)

            # ── Columna izquierda: gráfico | Columna derecha: filtros ──
            col_chart, col_filtros = st.columns([4, 1])

            with col_filtros:
                st.markdown("&nbsp;")
                mostrar_ingles = st.checkbox(
                    "Resaltar materias en inglés", value=False,
                    key="mat_ingles"
                )
                st.caption("Materias dictadas en inglés se muestran en azul.")

                st.markdown("&nbsp;")
                ordenar_imp = st.checkbox(
                    "Ordenar por importancia en el modelo", value=False,
                    key="mat_orden_imp"
                )
                st.caption(
                    "Importancia Gini: qué tanto predice cada materia "
                    "el riesgo de perder el año. "
                    "Rango: 0.000 (no predice) → 0.122 (Mathematics, mayor predictor)."
                )

            # Ordenar según filtro
            if ordenar_imp:
                df_mat = df_mat.sort_values("Importancia", ascending=False)
            else:
                df_mat = df_mat.sort_values("N bajo T3", ascending=False)

            colores = [
                "#1a5276" if (mostrar_ingles and row["En inglés"]) else "#e74c3c"
                for _, row in df_mat.iterrows()
            ]

            with col_chart:
                fig_mat = go.Figure()
                fig_mat.add_trace(go.Bar(
                    name="Bajo 4.0 en T3",
                    x=df_mat["Materia"],
                    y=df_mat["N bajo T3"],
                    marker_color=colores,
                    text=df_mat["N bajo T3"],
                    textposition="outside",
                    opacity=0.9,
                    hovertemplate="<b>%{x}</b><br>Estudiantes: %{y}<extra></extra>"
                ))

                max_n   = df_mat["N bajo T3"].max()
                max_imp = df_mat["Importancia"].max()
                if max_imp > 0:
                    imp_escalada = df_mat["Importancia"] / max_imp * max_n * 0.85
                    fig_mat.add_trace(go.Scatter(
                        name="Importancia en el modelo",
                        x=df_mat["Materia"],
                        y=imp_escalada,
                        mode="markers+text",
                        marker=dict(
                            symbol="diamond", size=12,
                            color="#f39c12",
                            line=dict(width=1.5, color="#e67e22")
                        ),
                        text=df_mat["Importancia"].apply(
                            lambda x: f"{x:.3f}" if x > 0 else ""
                        ),
                        textposition="top center",
                        textfont=dict(size=9, color="#1a5276"),
                        hovertemplate="<b>%{x}</b><br>Importancia: %{customdata:.3f}<extra></extra>",
                        customdata=df_mat["Importancia"]
                    ))

                if mostrar_ingles:
                    fig_mat.add_annotation(
                        x=0.01, y=1.12, xref="paper", yref="paper",
                        text="🔵 Azul = inglés · 🔴 Rojo = español",
                        showarrow=False, font=dict(size=10, color="#555"),
                        align="left"
                    )

                fig_mat.update_layout(
                    height=400,
                    xaxis=dict(tickangle=-30, gridcolor="#f0f0f0"),
                    yaxis=dict(title="N° estudiantes", gridcolor="#f0f0f0"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=40, r=20, t=60, b=90),
                    hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#ddd")
                )
                st.plotly_chart(fig_mat, use_container_width=True)
                st.caption(
                    "◆ Diamante naranja = importancia Gini de la materia en el modelo "
                    "(qué tanto predice el riesgo de perder el año)"
                )

            # ── Tabla ─────────────────────────
            st.markdown("**Detalle por materia**")
            det_rows = []
            for s in avail:
                col_t3 = f"{s}_T3"
                n_bajo = int((df_filtro_cat[col_t3].dropna() < 4.0).sum())
                df_sub = df_filtro_cat[[f"{s}_T1", f"{s}_T2", col_t3]].dropna()
                if not df_sub.empty:
                    acum = (df_sub[f"{s}_T1"]*0.30 +
                            df_sub[f"{s}_T2"]*0.30 +
                            df_sub[col_t3]*0.40)
                    n_acum    = int((acum < 4.0).sum())
                    prom_acum = round(acum.mean(), 2)
                else:
                    n_acum = 0; prom_acum = None
                pct = round(n_bajo / len(df_filtro_cat) * 100, 1) \
                      if len(df_filtro_cat) > 0 else 0
                det_rows.append({
                    "Materia":          SUBJECT_LABELS[s],
                    "Bajo 4.0 en T3":   n_bajo,
                    "% grupo filtrado": f"{pct}%",
                    "Acum. en riesgo":  n_acum,
                    "Prom. acumulado":  prom_acum,
                    "Imp. modelo":      IMPORTANCIA_MODELO.get(s, 0.0),
                })
            df_det = pd.DataFrame(det_rows).sort_values(
                "Bajo 4.0 en T3", ascending=False
            )
            st.dataframe(df_det, use_container_width=True, hide_index=True)

    st.divider()

    # ── Comparativa por sección ───────────────
    st.markdown("### N° estudiantes en riesgo por sección")
    st.caption("Categorías de riesgo activo: Riesgo Confirmado + Punto Ciego")

    if grado_sel == "Todos":
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

    df_gain = df_g.copy()
    df_gain["es_riesgo"] = df_gain["categoria"].isin(
        ["Riesgo Confirmado", "Punto Ciego"]
    ).astype(int)
    df_gain = df_gain.sort_values("proba_critical", ascending=False).reset_index(drop=True)
    df_gain["rank"]     = df_gain.index + 1
    df_gain["gain"]     = df_gain["es_riesgo"].cumsum()
    df_gain["gain_pct"] = df_gain["gain"] / max(df_gain["es_riesgo"].sum(), 1) * 100

    total_riesgo     = int(df_gain["es_riesgo"].sum())
    total_confirmado = int((df_g["categoria"] == "Riesgo Confirmado").sum())
    total_ciego      = int((df_g["categoria"] == "Punto Ciego").sum())
    total_teorico    = int((df_g["categoria"] == "Riesgo Teórico").sum())
    total_da_max     = total_confirmado + total_ciego

    df_g["grupo"] = df_g["grado_str"].astype(str) + "-" + df_g["seccion"].astype(str)
    grupos = sorted(df_g["grupo"].unique().tolist())

    st.markdown("### Eficiencia del modelo — curva de ganancia")
    st.caption(f"Middle School · {len(df_g)} estudiantes · {total_riesgo + total_teorico} en riesgo activo")

    if total_riesgo > 0:
        target_80   = total_riesgo * 0.80
        n_modelo_80 = int(df_gain[df_gain["gain"] >= target_80]["rank"].min())
        n_azar_80   = int(round(len(df_g) * 0.80))
        ganancia    = round(n_azar_80 / max(n_modelo_80, 1), 1)
    else:
        n_modelo_80 = 0; n_azar_80 = 0; ganancia = 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("En riesgo activo", total_riesgo + total_teorico,
              delta=f"{total_confirmado} confirmados · {total_teorico} teóricos")
    c2.metric("Para cubrir 80% con modelo", f"~{n_modelo_80}", delta="estudiantes")
    c3.metric("Para cubrir 80% al azar", f"~{n_azar_80}", delta="estudiantes")
    c4.metric("Ganancia del modelo", f"{ganancia}×", delta="más eficiente que el azar")

    st.divider()

    st.markdown("**🔴🟠 Director Académico**")
    st.caption("Atiende Riesgo Confirmado y Punto Ciego — prioridad máxima")

    cap_da = st.slider(
        "Capacidad DA",
        min_value=0, max_value=max(total_da_max, 1),
        value=min(total_da_max, 10),
        key="slider_da"
    )

    df_da_pool = df_g[df_g["categoria"].isin(["Riesgo Confirmado","Punto Ciego"])]\
                 .sort_values("proba_critical", ascending=False).reset_index(drop=True)
    df_da          = df_da_pool.head(cap_da).copy()
    df_desbordados = df_da_pool.iloc[cap_da:].copy() \
                     if cap_da < len(df_da_pool) else pd.DataFrame()

    total_hrt_interv = sum([
        st.session_state.get(f"slider_hrt_{grupo}", 0)
        for grupo in grupos
    ])
    total_interv = cap_da + total_hrt_interv
    pct_da_cub   = round(cap_da / max(total_da_max, 1) * 100, 1)
    pct_hrt_cub  = round(total_hrt_interv / max(total_teorico, 1) * 100, 1)
    sin_cubrir   = max(0, (total_da_max - cap_da) + (total_teorico - total_hrt_interv))

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total intervenidos", total_interv)
    m2.metric("Confirmado + ciego cubierto", f"{pct_da_cub}%",
              delta=f"{cap_da} de {total_da_max}")
    m3.metric("Teórico cubierto", f"{pct_hrt_cub}%",
              delta=f"{total_hrt_interv} de {total_teorico}")
    m4.metric("En riesgo sin cubrir", sin_cubrir)

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

    pct_da_curva = float(df_gain[df_gain["rank"] == max(cap_da, 1)]["gain_pct"].values[0]) \
                   if 0 < cap_da <= len(df_gain) else 0.0
    if cap_da > 0:
        fig_gain.add_vline(
            x=cap_da, line_dash="dash", line_color="#e74c3c", line_width=2,
            annotation_text=f"DA: {cap_da} → {pct_da_curva:.0f}%",
            annotation_position="top left",
            annotation_font_color="#e74c3c", annotation_font_size=11
        )

    rank_total      = min(total_interv, len(df_gain))
    pct_total_curva = float(df_gain[df_gain["rank"] == max(rank_total, 1)]["gain_pct"].values[0]) \
                      if rank_total > 0 else 0.0
    if total_interv > 0 and total_interv != cap_da:
        fig_gain.add_vline(
            x=total_interv, line_dash="dash", line_color="#3498db", line_width=2,
            annotation_text=f"DA+HRT: {total_interv} → {pct_total_curva:.0f}%",
            annotation_position="top right",
            annotation_font_color="#3498db", annotation_font_size=11
        )

    fig_gain.update_layout(
        height=380,
        xaxis=dict(title="N° estudiantes intervenidos", gridcolor="#f0f0f0"),
        yaxis=dict(title="% riesgo capturado", range=[0, 105], gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=50, r=20, t=60, b=50)
    )
    st.plotly_chart(fig_gain, use_container_width=True)

    st.markdown(f"""
    <div style="background:#e6f1fb;border-left:3px solid #185FA5;border-radius:0 8px 8px 0;
                padding:10px 14px;font-size:13px;color:#0C447C;line-height:1.6;margin-bottom:16px">
        Con <b>{total_interv} intervenciones</b> ({cap_da} DA + {total_hrt_interv} HRT)
        el sistema cubre el <b>{pct_total_curva:.0f}% del riesgo</b>.
        Sin el modelo necesitarías intervenir ~{n_azar_80} estudiantes para cubrir el 80%.
    </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown(f"**Lista DA — top {cap_da} estudiantes**")
    if df_da.empty:
        st.info("DA sin intervenciones asignadas.")
    else:
        df_da_show = df_da[["student_id","grado_label","categoria",
                             "proba_critical","n_bajo_acumulada","marcador_LSC"]].copy()
        df_da_show["categoria"]      = df_da_show["categoria"].apply(
            lambda x: f"{ALERT_EMOJI.get(x,'')} {x}")
        df_da_show["proba_critical"] = df_da_show["proba_critical"].apply(lambda x: f"{x:.0%}")
        df_da_show["marcador_LSC"]   = df_da_show["marcador_LSC"].map({1:"✓", 0:""})
        df_da_show = df_da_show.rename(columns={
            "student_id":"ID","grado_label":"Grado","categoria":"Categoría",
            "proba_critical":"P(crítico)","n_bajo_acumulada":"Mat.<4.0","marcador_LSC":"LSC"
        })
        st.dataframe(df_da_show, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("**🔵 Directores de grupo (HRT)**")
    st.caption("Cada HRT atiende primero los desbordados del DA de su sección, luego sus teóricos")

    filas = [grupos[i:i+3] for i in range(0, len(grupos), 3)]

    for fila in filas:
        cols_hrt = st.columns(3)
        for j, grupo in enumerate(fila):
            with cols_hrt[j]:
                grado_str = grupo.split("-")[0]
                sec_str   = grupo.split("-")[1]
                grado_num = GRADO_MAP[grado_str]

                desb_sec = df_desbordados[
                    (df_desbordados["seccion"] == sec_str) &
                    (df_desbordados["grade"] == grado_num)
                ] if not df_desbordados.empty else pd.DataFrame()

                teor_sec = df_g[
                    (df_g["categoria"] == "Riesgo Teórico") &
                    (df_g["seccion"] == sec_str) &
                    (df_g["grade"] == grado_num)
                ].sort_values("proba_critical", ascending=False)

                n_desb     = len(desb_sec)
                n_teor     = len(teor_sec)
                n_conf_sec = int((
                    df_g[
                        (df_g["seccion"] == sec_str) &
                        (df_g["grade"] == grado_num)
                    ]["categoria"] == "Riesgo Confirmado"
                ).sum())
                pool_hrt = pd.concat([desb_sec, teor_sec], ignore_index=True)

                st.markdown(
                    f"**{grupo}** · {n_conf_sec} confirmados · {n_teor} teóricos"
                    + (f" · ⚠️ {n_desb} desbordados" if n_desb > 0 else "")
                )

                cap_hrt = st.slider(
                    f"Capacidad {grupo}",
                    min_value=0, max_value=max(len(pool_hrt), 1),
                    value=min(n_teor, 3),
                    key=f"slider_hrt_{grupo}",
                    label_visibility="collapsed"
                )

                df_hrt_show = pool_hrt.head(cap_hrt).copy()
                if not df_hrt_show.empty:
                    df_hrt_show["Tipo"] = df_hrt_show["categoria"].apply(
                        lambda x: "⚠️ Desbordado DA" if x in ["Riesgo Confirmado","Punto Ciego"]
                        else f"{ALERT_EMOJI.get(x,'')} Teórico"
                    )
                    df_hrt_show["P(crítico)"] = df_hrt_show["proba_critical"].apply(
                        lambda x: f"{x:.0%}")
                    df_hrt_show["LSC"] = df_hrt_show["marcador_LSC"].map({1:"✓", 0:""})
                    st.dataframe(
                        df_hrt_show[["student_id","Tipo","P(crítico)","LSC"]].rename(
                            columns={"student_id":"ID"}
                        ),
                        use_container_width=True, hide_index=True,
                        height=min(150 + cap_hrt * 35, 320)
                    )
                else:
                    st.caption("Sin intervenciones asignadas")
