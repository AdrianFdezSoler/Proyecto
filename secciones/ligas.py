# -*- coding: utf-8 -*-
"""
Página 2. El perfil de cada liga. 
Comparativa de las 5 grandes ligas, valor de mercado por posición y evolución del valor a lo largo de los años.
"""

from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

APP_TITLE = "El perfil de cada liga"

st.set_page_config(APP_TITLE, layout="wide")

DATOS = Path(__file__).parent.parent / "Datos"

# Métrica de la comparativa: nombre legible y columna del CSV
METRICAS = {
    "Goles por partido": "goles_por_partido",
    "Espectadores por partido": "asistencia_media",
    "Edad media": "edad_media",
    "% extranjeros": "pct_extranjeros",
}

# Orden de las posiciones de la portería al ataque
ORDEN_POSICIONES = ["Goalkeeper", "Defender", "Midfield", "Attack"]


@st.cache_data
def cargar_resumen():
    return pd.read_csv(DATOS / "ligas_resumen.csv")


@st.cache_data
def cargar_valor_temporal():
    df = pd.read_csv(DATOS / "ligas_valor_temporal.csv")
    df["valor_total"] = df["valor_total"] / 1_000_000
    return df


@st.cache_data
def cargar_valor_posicion():
    return pd.read_csv(DATOS / "valor_por_posicion.csv")


def grafica_comparativa(resumen, metrica):
    columna = METRICAS[metrica]
    datos = resumen.sort_values(columna, ascending=False)
    fig = px.bar(
        datos, x="liga", y=columna, color="liga",
        title=f"Las 5 grandes ligas: {metrica}",
        labels={columna: metrica, "liga": "Liga"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def grafica_boxplot(jugadores, ligas):
    datos = jugadores[jugadores["liga"].isin(ligas)]
    fig = px.box(
        datos, x="position", y="valor", color="liga",
        category_orders={"position": ORDEN_POSICIONES},
        title="Valor de mercado por posición",
        labels={"position": "Posición", "valor": "Valor (M€)", "liga": "Liga"},
    )
    st.plotly_chart(fig, use_container_width=True)


def grafica_evolucion(serie, ligas):
    datos = serie[serie["liga"].isin(ligas)]
    fig = px.line(
        datos, x="año", y="valor_total", color="liga",
        title="Evolución del valor de mercado por liga",
        labels={"valor_total": "Valor total (M€)", "año": "Año", "liga": "Liga"},
    )
    st.plotly_chart(fig, use_container_width=True)


st.title(APP_TITLE)
st.caption("Las 5 grandes ligas europeas en la temporada actual.")

resumen = cargar_resumen()
serie = cargar_valor_temporal()
jugadores = cargar_valor_posicion()

# Un único selector de ligas que afecta a las tres pestañas
ligas = st.multiselect("Ligas a comparar", list(resumen["liga"]), default=list(resumen["liga"]))

tab_comparativa, tab_posicion, tab_evolucion = st.tabs(
    ["Comparativa", "Valor por posición", "Evolución"])

if not ligas:
    st.info("Selecciona al menos una liga para ver los datos.")
else:
    with tab_comparativa:
        metrica = st.selectbox("Métrica", list(METRICAS.keys()))
        grafica_comparativa(resumen[resumen["liga"].isin(ligas)], metrica)

    with tab_posicion:
        grafica_boxplot(jugadores, ligas)

    with tab_evolucion:
        grafica_evolucion(serie, ligas)
