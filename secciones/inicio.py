# -*- coding: utf-8 -*-
"""
Portada de la web. Las 5 grandes ligas europeas.
"""

import streamlit as st

APP_TITLE = "Las 5 grandes ligas europeas"

st.set_page_config(APP_TITLE, layout="wide")

st.title(APP_TITLE)

st.markdown("""
Premier League, LaLiga, Serie A, Bundesliga y Ligue 1 reúnen a buena parte de
los mejores jugadores del mundo. Esta web las retrata en tres pasos, de lo
general a lo concreto:

* **De dónde vienen los jugadores**: un mapa mundial con la procedencia de los
  futbolistas que juegan en las cinco grandes ligas, y los países que más
  talento aportan.
* **El perfil de cada liga**: cómo es cada una por dentro, con sus goles por
  partido, la asistencia a los estadios, la edad media, el porcentaje de
  extranjeros y la evolución de su valor de mercado.
* **El Valencia CF**: bajamos de la liga al club, con el valor de su plantilla,
  la trayectoria de sus jugadores y su composición por posiciones.

Usa el menú de la izquierda para navegar entre las páginas.
""")

st.subheader("Fuente de los datos")
st.markdown("""
Los datos provienen de **Transfermarkt** y se han extraído del dataset abierto publicado en Kaggle:
[davidcariboo/player-scores](https://www.kaggle.com/datasets/davidcariboo/player-scores). Incluye jugadores, valoraciones de mercado,
clubes, competiciones y partidos. La cartografía es la capa **World Countries (Generalized)** de ArcGIS Hub.
""")