"""
Vermont Early Warning System
Andrés Velasco Hernández | EAFIT Maestría CDA 2026-1
"""
import streamlit as st

pg = st.navigation([
    st.Page("pages/0_Inicio.py",        title="🏫 Inicio",        default=True),
    st.Page("pages/1_Visualizacion.py", title="📊 Visualización"),
    st.Page("pages/4_Decisiones.py",    title="🎯 Decisiones"),
])
pg.run()
