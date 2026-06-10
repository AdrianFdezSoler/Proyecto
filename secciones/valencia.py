# -*- coding: utf-8 -*-
"""
Página 3. El Valencia CF.
Valor de la plantilla, su evolución, la composición por jugador y la procedencia de los futbolistas.
"""

from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

APP_TITLE = "El Valencia CF"

st.set_page_config(APP_TITLE, layout="wide")

DATOS = Path(__file__).parent.parent / "Datos"


@st.cache_data
def cargar_datos():
    jugadores = pd.read_csv(DATOS / "valencia_jugadores.csv")
    valor_anual = pd.read_csv(DATOS / "valencia_plantilla_total.csv")
    plantilla = pd.read_csv(DATOS / "valencia_plantilla.csv")
    procedencia = pd.read_csv(DATOS / "valencia_procedencia.csv")
    jugadores["date"] = pd.to_datetime(jugadores["date"])
    return jugadores, valor_anual, plantilla, procedencia


def grafica_valor_anual(valor_anual):
    fig = px.line(
        valor_anual, x="año", y="valor_total", markers=True,
        title="Evolución del valor total de la plantilla del Valencia",
        labels={"año": "Año", "valor_total": "Valor total (M€)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def grafica_treemap(plantilla):
    # Cada rectángulo es un jugador y su tamaño es el valor de mercado, agrupados por posición
    fig = px.treemap(
        plantilla, path=[px.Constant("Plantilla"), "position", "name"],
        values="valor", color="valor", color_continuous_scale="Blues",
        title="Peso de cada jugador en el valor de la plantilla (M€)",
    )
    fig.update_traces(textinfo="label+value")
    st.plotly_chart(fig, use_container_width=True)


def grafica_jugador(jugadores, jugador):
    datos = jugadores[jugadores["name"] == jugador]
    fig = px.line(
        datos, x="date", y="valor",
        title="Valor de mercado del jugador a lo largo de su carrera",
        labels={"date": "Fecha", "valor": "Valor (M€)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def grafica_mapa_procedencia(procedencia):
    mapa = folium.Map(location=[25, 5], zoom_start=2, control_scale=True)
    for _, fila in procedencia.iterrows():
        folium.Marker(
            [fila["lat"], fila["lon"]],
            tooltip=f"{fila['pais']}: {int(fila['n_jugadores'])} jugadores",
            icon=folium.Icon(color="orange", icon="user"),
        ).add_to(mapa)
    st_folium(mapa, width=1100, height=500, returned_objects=[], key="mapa_valencia")


st.title(APP_TITLE)
st.caption("Datos de mercado del Valencia CF.")

jugadores, valor_anual, plantilla, procedencia = cargar_datos()

# Tarjetas resumen de la plantilla actual
col1, col2, col3 = st.columns(3)
col1.metric("Valor de la plantilla", f"{plantilla['valor'].sum():,.0f} M€")
col2.metric("Nº de jugadores", len(plantilla))
col3.metric("Nacionalidades", procedencia["iso2"].nunique())

st.subheader("Valor total de la plantilla a lo largo de los años")
grafica_valor_anual(valor_anual)

st.subheader("Composición del valor de la plantilla")
grafica_treemap(plantilla)

st.subheader("Valor de un jugador de la plantilla")
nombres = sorted(jugadores["name"].unique())
mas_valioso = jugadores.groupby("name")["valor"].max().idxmax()
jugador = st.selectbox("Jugador", nombres, index=nombres.index(mas_valioso))
grafica_jugador(jugadores, jugador)

st.subheader("De dónde viene la plantilla")
st.caption("País de nacionalidad de los jugadores de la plantilla actual.")
grafica_mapa_procedencia(procedencia)
