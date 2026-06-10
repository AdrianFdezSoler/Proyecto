# -*- coding: utf-8 -*-
"""
Página 1. De dónde vienen los jugadores de las grandes ligas.
Mapa mundial por país de nacionalidad con un slider de año y un ranking de los países que más aportan en el año seleccionado.
"""

import copy
from pathlib import Path

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import mapclassify

APP_TITLE = "De dónde vienen los jugadores de las grandes ligas"

st.set_page_config(APP_TITLE, layout="wide")

DATOS = Path(__file__).parent.parent / "Datos"

# Métrica del mapa: nombre legible, columna, unidad y decimales del texto
METRICAS = {
    "Nº de jugadores": ("n_jugadores", "", 0),
    "Valor total (M€)": ("valor_total", " M€", 0),
    "Valor medio (M€)": ("valor_medio", " M€", 1),
    "Edad media": ("edad_media", " años", 1),
}

# Cinco tonos de la paleta YlGnBu, de menos a más
COLORES = ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"]


@st.cache_data
def cargar_datos():
    df = pd.read_csv(DATOS / "talento_temporal.csv")
    for columna in ["valor_total", "valor_medio"]:
        df[columna] = df[columna] / 1_000_000
    return df


@st.cache_data
def cargar_geojson():
    mundo = gpd.read_file(DATOS / "world_simplificado.geojson")
    return mundo.__geo_interface__


def formatea(valor, unidad, decimales):
    return f"{valor:,.{decimales}f}{unidad}"


def calcular_cortes(serie):
    # Cortes por saltos naturales (Jenks): agrupa a los que aportan poco y separa a los que más
    valores = serie.dropna()
    return [valores.min()] + list(mapclassify.NaturalBreaks(valores, k=5).bins)


def color_de(valor, cortes):
    for i in range(5):
        if valor <= cortes[i + 1]:
            return COLORES[i]
    return COLORES[-1]


def leyenda_html(cortes, unidad, decimales):
    # Leyenda de cajitas con el texto en negro para que se lea sobre el fondo blanco
    filas = ""
    for i in range(5):
        texto = f"{formatea(cortes[i], unidad, decimales)} a {formatea(cortes[i + 1], unidad, decimales)}"
        filas += (
            f'<div style="margin:2px 0">'
            f'<span style="background:{COLORES[i]};width:16px;height:12px;'
            f'display:inline-block;margin-right:6px;border:1px solid #999"></span>'
            f'{texto}</div>'
        )
    filas += (
        '<div style="margin:2px 0">'
        '<span style="background:lightgrey;width:16px;height:12px;'
        'display:inline-block;margin-right:6px;border:1px solid #999"></span>'
        'Sin datos</div>'
    )
    return (
        '<div style="position:fixed;bottom:30px;left:10px;z-index:1000;'
        'background:white;color:black;padding:8px 10px;border:1px solid #999;'
        'border-radius:4px;font-size:13px;line-height:1.2">' + filas + '</div>'
    )


def agrupar_por_iso(datos):
    # El mapa es geográfico, así que Reino Unido junto
    datos = datos.copy()
    datos["edad_x_n"] = datos["edad_media"] * datos["n_jugadores"]
    por_iso = datos.groupby("iso2", as_index=False).agg(
        n_jugadores=("n_jugadores", "sum"),
        valor_total=("valor_total", "sum"),
        edad_x_n=("edad_x_n", "sum"),
    )
    por_iso["valor_medio"] = por_iso["valor_total"] / por_iso["n_jugadores"]
    por_iso["edad_media"] = por_iso["edad_x_n"] / por_iso["n_jugadores"]
    return por_iso


def display_mapa(datos, geojson, metrica):
    columna, unidad, decimales = METRICAS[metrica]
    por_iso = agrupar_por_iso(datos)
    cortes = calcular_cortes(por_iso[columna])
    valor_por_iso = dict(zip(por_iso["iso2"], por_iso[columna]))

    # Copio el geojson para no tocar el de la caché y uso el nombre del país de la cartografía
    geo = copy.deepcopy(geojson)
    for feature in geo["features"]:
        iso = feature["properties"].get("iso2")
        valor = valor_por_iso.get(iso)
        feature["properties"]["pais"] = feature["properties"].get("carto_name", "")
        if valor is None or pd.isna(valor):
            feature["properties"]["valor_txt"] = "Sin datos"
        else:
            feature["properties"]["valor_txt"] = formatea(valor, unidad, decimales)

    def estilo(feature):
        valor = valor_por_iso.get(feature["properties"].get("iso2"))
        color = "lightgrey" if valor is None or pd.isna(valor) else color_de(valor, cortes)
        return {"fillColor": color, "color": "grey", "weight": 0.3, "fillOpacity": 0.8}

    mapa = folium.Map(location=[20, 0], zoom_start=2, control_scale=True)
    folium.GeoJson(
        geo, style_function=estilo,
        tooltip=folium.GeoJsonTooltip(["pais", "valor_txt"], labels=False),
    ).add_to(mapa)
    mapa.get_root().html.add_child(folium.Element(leyenda_html(cortes, unidad, decimales)))
    st_folium(mapa, width=1100, height=550, returned_objects=[], key="mapa_talento")


def grafica_ranking(datos, metrica, n):
    columna, unidad, decimales = METRICAS[metrica]
    # Para esa métrica primero las canteras más jóvenes
    if metrica == "Edad media":
        top = datos.dropna(subset=[columna]).nsmallest(n, columna).sort_values(columna, ascending=False)
        titulo = f"Top {n} países con el talento más joven"
    else:
        top = datos.dropna(subset=[columna]).nlargest(n, columna).sort_values(columna, ascending=True)
        titulo = f"Top {n} países por {metrica.lower()}"
    fig = px.bar(
        top, x=columna, y="country_name", orientation="h",
        title=titulo, labels={columna: metrica, "country_name": "País"},
    )
    fig.update_layout(height=max(400, n * 22))
    st.plotly_chart(fig, use_container_width=True)


st.title(APP_TITLE)

df = cargar_datos()
geojson = cargar_geojson()

# Filtros en el lateral: año y métrica
año = st.sidebar.slider("Año", 2012, 2025, 2025)
metrica = st.sidebar.radio("Métrica", list(METRICAS.keys()))

st.caption(
    f"Jugadores de las 5 grandes ligas (Premier, LaLiga, Serie A, Bundesliga y "
    f"Ligue 1) por país de nacionalidad en {año}.")

datos_año = df[df["año"] == año]

tab_mapa, tab_ranking = st.tabs(["Mapa", "Ranking"])

with tab_mapa:
    st.subheader(f"Mapa del talento en {año}")
    display_mapa(datos_año, geojson, metrica)

with tab_ranking:
    st.subheader(f"Ranking de países en {año}")
    n = st.slider("Número de países", 5, 25, 15)
    grafica_ranking(datos_año, metrica, n)
