# -*- coding: utf-8 -*-
"""
Preprocesado de datos del proyecto.
Lee los CSV crudos de Transfermarkt y genera las tablas ligeras que carga la web. No descarga nada.
"""

from pathlib import Path

import pandas as pd
import geopandas as gpd

DATOS_DIR = Path(__file__).parent
RAW_DIR = DATOS_DIR / "raw"

# Las cinco grandes ligas: código de competición y nombre
GRANDES_LIGAS = {
    "GB1": "Premier League",
    "ES1": "LaLiga",
    "IT1": "Serie A",
    "L1": "Bundesliga",
    "FR1": "Ligue 1",
}

# País de cada liga, para calcular el porcentaje de extranjeros
PAIS_DE_LIGA = {
    "GB1": "England",
    "ES1": "Spain",
    "IT1": "Italy",
    "L1": "Germany",
    "FR1": "France",
}

VALENCIA_ID = 1049

# Nombre de país de Transfermarkt a código ISO de dos letras.
# England, Scotland, Wales y Northern Ireland van a GB para encajar con el mapa.
NOMBRE_A_ISO2 = {
    "Brazil": "BR", "Argentina": "AR", "Japan": "JP", "Colombia": "CO",
    "Spain": "ES", "France": "FR", "Serbia": "RS", "Sweden": "SE",
    "Ukraine": "UA", "Türkiye": "TR", "Korea, South": "KR",
    "Netherlands": "NL", "Poland": "PL", "United States": "US",
    "England": "GB", "Germany": "DE", "Mexico": "MX", "Portugal": "PT",
    "Czech Republic": "CZ", "Norway": "NO", "Saudi Arabia": "SA",
    "Denmark": "DK", "Russia": "RU", "Romania": "RO", "Croatia": "HR",
    "Belgium": "BE", "Australia": "AU", "Italy": "IT", "Greece": "GR",
    "Austria": "AT", "Switzerland": "CH", "Nigeria": "NG", "Scotland": "GB",
    "Uruguay": "UY", "Morocco": "MA", "Ghana": "GH", "Senegal": "SN",
    "Cote d'Ivoire": "CI", "Bosnia-Herzegovina": "BA", "Slovakia": "SK",
    "Cameroon": "CM", "Paraguay": "PY", "Canada": "CA", "Algeria": "DZ",
    "Chile": "CL", "Venezuela": "VE", "New Zealand": "NZ", "Ireland": "IE",
    "Kosovo": "XK", "Albania": "AL", "Mali": "ML", "Jamaica": "JM",
    "South Africa": "ZA", "Slovenia": "SI", "Ecuador": "EC", "Peru": "PE",
    "Israel": "IL", "Iceland": "IS", "Montenegro": "ME", "Hungary": "HU",
    "Georgia": "GE", "Finland": "FI", "DR Congo": "CD", "Wales": "GB",
    "Egypt": "EG", "Costa Rica": "CR", "Uganda": "UG", "Guinea": "GN",
    "Northern Ireland": "GB", "Iraq": "IQ", "The Gambia": "GM",
    "North Macedonia": "MK", "Thailand": "TH", "Comoros": "KM",
    "Belarus": "BY", "Panama": "PA", "Bolivia": "BO", "Honduras": "HN",
    "Armenia": "AM", "Qatar": "QA", "Tunisia": "TN", "Oman": "OM",
    "Bulgaria": "BG", "Uzbekistan": "UZ", "El Salvador": "SV",
    "Lithuania": "LT", "Cape Verde": "CV", "Vietnam": "VN", "Cyprus": "CY",
    "Azerbaijan": "AZ", "China": "CN", "Jordan": "JO", "Angola": "AO",
    "Tajikistan": "TJ", "Dominican Republic": "DO", "Moldova": "MD",
    "Kyrgyzstan": "KG", "Ethiopia": "ET", "Estonia": "EE", "Suriname": "SR",
    "Malta": "MT", "Bangladesh": "BD", "Andorra": "AD", "Singapore": "SG",
    "Latvia": "LV", "Indonesia": "ID", "Philippines": "PH",
    "Luxembourg": "LU", "Faroe Islands": "FO", "Burkina Faso": "BF",
    "Guinea-Bissau": "GW", "Myanmar": "MM", "Puerto Rico": "PR",
    "Curacao": "CW", "Libya": "LY", "Iran": "IR", "Gibraltar": "GI",
    "Laos": "LA", "Malaysia": "MY", "Guatemala": "GT",
    "United Arab Emirates": "AE", "Lebanon": "LB", "Cambodia": "KH",
    "Congo": "CG", "India": "IN", "Kazakhstan": "KZ", "Haiti": "HT",
    "Togo": "TG", "Syria": "SY", "San Marino": "SM", "Mauritania": "MR",
    "Kenya": "KE", "Gabon": "GA", "Equatorial Guinea": "GQ",
    "Trinidad and Tobago": "TT", "Sierra Leone": "SL", "Benin": "BJ",
    "Zimbabwe": "ZW", "Zambia": "ZM", "Liberia": "LR", "Madagascar": "MG",
    "Central African Republic": "CF", "Burundi": "BI", "Guyana": "GY",
    "Niger": "NE", "Rwanda": "RW", "Tanzania": "TZ", "Mozambique": "MZ",
    "Nicaragua": "NI", "Palestine": "PS", "Somalia": "SO", "Cuba": "CU",
    "Pakistan": "PK", "Chad": "TD", "Yemen": "YE", "Sri Lanka": "LK",
    "Mauritius": "MU", "Bahrain": "BH", "Barbados": "BB", "Malawi": "MW",
    "Liechtenstein": "LI", "Mongolia": "MN", "Sudan": "SD", "Eritrea": "ER",
    "Botswana": "BW",
}


def cargar_valoraciones():
    # Única fuente del valor de mercado: la valoración de cada jugador por año
    valoraciones = pd.read_csv(RAW_DIR / "player_valuations.csv",
                               usecols=["player_id", "date", "market_value_in_eur"])
    valoraciones["año"] = pd.to_datetime(valoraciones["date"], errors="coerce").dt.year
    return valoraciones.sort_values("date").drop_duplicates(
        ["player_id", "año"], keep="last")


def valor_actual(valoraciones):
    # Valor de mercado actual de cada jugador: su última valoración registrada
    ultima = valoraciones.drop_duplicates("player_id", keep="last")
    return ultima.set_index("player_id")["market_value_in_eur"]


def cargar_jugadores_actuales():
    columnas = ["player_id", "name", "country_of_citizenship", "position",
                "date_of_birth", "current_club_domestic_competition_id", "last_season"]
    jugadores = pd.read_csv(RAW_DIR / "players.csv", usecols=columnas)
    # Foto actual: solo la última temporada registrada (la 2025-26)
    jugadores = jugadores[jugadores["last_season"] == jugadores["last_season"].max()].copy()
    año_nacimiento = pd.to_datetime(jugadores["date_of_birth"], errors="coerce").dt.year
    jugadores["edad"] = 2025 - año_nacimiento
    return jugadores


def preparar_talento_temporal(valoraciones):
    # Quién jugó de verdad cada temporada en las cinco grandes, según las apariciones en partidos oficiales.
    apariciones = pd.read_csv(RAW_DIR / "appearances.csv",
                              usecols=["player_id", "game_id", "competition_id"])
    apariciones = apariciones[apariciones["competition_id"].isin(GRANDES_LIGAS)]
    partidos = pd.read_csv(RAW_DIR / "games.csv", usecols=["game_id", "season"])
    apariciones = apariciones.merge(partidos, on="game_id", how="left")
    apariciones = apariciones.dropna(subset=["season"])
    apariciones["año"] = apariciones["season"].astype(int)
    apariciones = apariciones[apariciones["año"].between(2010, 2025)]
    jugadores_año = apariciones[["año", "player_id"]].drop_duplicates()

    info = pd.read_csv(RAW_DIR / "players.csv",
                       usecols=["player_id", "country_of_citizenship", "date_of_birth"])
    jugadores_año = jugadores_año.merge(info, on="player_id", how="left")
    jugadores_año = jugadores_año.dropna(subset=["country_of_citizenship"])
    jugadores_año["iso2"] = jugadores_año["country_of_citizenship"].map(NOMBRE_A_ISO2)
    jugadores_año = jugadores_año.dropna(subset=["iso2"])
    año_nacimiento = pd.to_datetime(jugadores_año["date_of_birth"], errors="coerce").dt.year
    jugadores_año["edad"] = jugadores_año["año"] - año_nacimiento

    # Valor de cada jugador en su temporada, desde las valoraciones
    jugadores_año = jugadores_año.merge(
        valoraciones[["player_id", "año", "market_value_in_eur"]],
        on=["player_id", "año"], how="left")

    tabla = jugadores_año.groupby(["año", "country_of_citizenship"]).agg(
        n_jugadores=("player_id", "nunique"),
        valor_total=("market_value_in_eur", "sum"),
        valor_medio=("market_value_in_eur", "mean"),
        edad_media=("edad", "mean"),
    ).reset_index().rename(columns={"country_of_citizenship": "country_name"})
    # Cada selección por separado (Inglaterra, Escocia...) pero guardo el ISO2 para el mapa
    tabla["iso2"] = tabla["country_name"].map(NOMBRE_A_ISO2)
    tabla = tabla.sort_values(["año", "n_jugadores"], ascending=[True, False])

    tabla.to_csv(DATOS_DIR / "talento_temporal.csv", index=False)
    print(f"talento_temporal.csv: {len(tabla)} filas")
    return tabla


def preparar_ligas_resumen(jugadores):
    # Goles y asistencia de la última temporada disponible
    partidos = pd.read_csv(RAW_DIR / "games.csv",
                           usecols=["competition_id", "season", "home_club_goals",
                                    "away_club_goals", "attendance"])
    partidos = partidos[partidos["competition_id"].isin(GRANDES_LIGAS)].copy()
    partidos = partidos[partidos["season"] == partidos["season"].max()]
    partidos["goles"] = partidos["home_club_goals"] + partidos["away_club_goals"]

    filas = []
    for liga_id, nombre in GRANDES_LIGAS.items():
        de_la_liga = jugadores[jugadores["current_club_domestic_competition_id"] == liga_id]
        n = len(de_la_liga)
        extranjeros = (de_la_liga["country_of_citizenship"] != PAIS_DE_LIGA[liga_id]).sum()
        partidos_liga = partidos[partidos["competition_id"] == liga_id]
        filas.append({
            "liga": nombre,
            "edad_media": de_la_liga["edad"].mean(),
            "pct_extranjeros": extranjeros / n * 100 if n else 0,
            "goles_por_partido": partidos_liga["goles"].mean(),
            "asistencia_media": partidos_liga["attendance"].mean(),
        })
    resumen = pd.DataFrame(filas)
    resumen.to_csv(DATOS_DIR / "ligas_resumen.csv", index=False)
    print(f"ligas_resumen.csv: {len(resumen)} ligas")
    return resumen


def preparar_valor_temporal():
    columnas = ["player_id", "date", "market_value_in_eur",
                "player_club_domestic_competition_id"]
    valoraciones = pd.read_csv(RAW_DIR / "player_valuations.csv", usecols=columnas)
    valoraciones["año"] = pd.to_datetime(valoraciones["date"], errors="coerce").dt.year
    valoraciones = valoraciones[
        valoraciones["player_club_domestic_competition_id"].isin(GRANDES_LIGAS)]
    valoraciones = valoraciones[valoraciones["año"].between(2004, 2025)]

    # Última valoración de cada jugador por año y liga
    valoraciones = valoraciones.sort_values("date").drop_duplicates(
        ["player_id", "año", "player_club_domestic_competition_id"], keep="last")
    serie = valoraciones.groupby(
        ["año", "player_club_domestic_competition_id"]
    )["market_value_in_eur"].sum().reset_index()
    serie["liga"] = serie["player_club_domestic_competition_id"].map(GRANDES_LIGAS)
    serie = serie.rename(columns={"market_value_in_eur": "valor_total"})
    serie = serie[["año", "liga", "valor_total"]].sort_values(["año", "liga"])

    serie.to_csv(DATOS_DIR / "ligas_valor_temporal.csv", index=False)
    print(f"ligas_valor_temporal.csv: {len(serie)} filas")
    return serie


def preparar_valor_por_posicion(jugadores, valores_actuales):
    de_grandes = jugadores[
        jugadores["current_club_domestic_competition_id"].isin(GRANDES_LIGAS)].copy()
    de_grandes = de_grandes[de_grandes["position"] != "Missing"].dropna(subset=["position"])
    de_grandes["liga"] = de_grandes["current_club_domestic_competition_id"].map(GRANDES_LIGAS)
    de_grandes["valor"] = de_grandes["player_id"].map(valores_actuales) / 1_000_000
    de_grandes = de_grandes.dropna(subset=["valor"])
    de_grandes = de_grandes[["liga", "position", "valor"]]
    de_grandes.to_csv(DATOS_DIR / "valor_por_posicion.csv", index=False)
    print(f"valor_por_posicion.csv: {len(de_grandes)} jugadores")
    return de_grandes


def simplificar_cartografia():
    # La cartografía cruda está en raw, aquí solo se simplifica para aligerarla
    mundo = gpd.read_file(RAW_DIR / "arcgis_world_countries.geojson")
    mundo = mundo.rename(columns={"ISO": "iso2", "COUNTRY": "carto_name"})
    mundo = mundo[["iso2", "carto_name", "geometry"]].copy()
    mundo["geometry"] = mundo["geometry"].simplify(0.4, preserve_topology=True)
    mundo.to_file(DATOS_DIR / "world_simplificado.geojson", driver="GeoJSON")
    print(f"world_simplificado.geojson: {len(mundo)} países")

    # Un punto por país para los mapas de marcadores
    centroides = mundo.dropna(subset=["iso2"]).copy()
    # Reproyecto solo para medir el tamaño y quedarme con el territorio mayor
    centroides["area"] = centroides.to_crs(6933).geometry.area
    centroides = centroides.sort_values("area", ascending=False).drop_duplicates("iso2")
    puntos = centroides.geometry.representative_point()
    centroides["lat"] = puntos.y
    centroides["lon"] = puntos.x
    centroides = centroides[["iso2", "carto_name", "lat", "lon"]]
    centroides.to_csv(DATOS_DIR / "centroides_paises.csv", index=False)
    return mundo


def preparar_valencia(valoraciones, valores_actuales):
    info = pd.read_csv(RAW_DIR / "players.csv",
                       usecols=["player_id", "name", "position", "current_club_id",
                                "country_of_citizenship", "last_season"])

    # Plantilla real: la última temporada, para no arrastrar cantera ni ex jugadores
    del_club = info[info["current_club_id"] == VALENCIA_ID]
    plantilla = del_club[del_club["last_season"] == del_club["last_season"].max()].copy()
    plantilla["valor"] = plantilla["player_id"].map(valores_actuales) / 1_000_000

    # Trayectoria de valor de cada jugador de la plantilla
    carrera = valoraciones[valoraciones["player_id"].isin(plantilla["player_id"])].copy()
    carrera = carrera.merge(plantilla[["player_id", "name"]], on="player_id")
    carrera["valor"] = carrera["market_value_in_eur"] / 1_000_000
    carrera = carrera[["name", "date", "valor"]].sort_values(["name", "date"])
    carrera.to_csv(DATOS_DIR / "valencia_jugadores.csv", index=False)

    # Valor de la plantilla por año, con las valoraciones que tuvieron al Valencia
    valencia_val = pd.read_csv(RAW_DIR / "player_valuations.csv",
                               usecols=["player_id", "date", "market_value_in_eur",
                                        "current_club_id"])
    valencia_val = valencia_val[valencia_val["current_club_id"] == VALENCIA_ID].copy()
    valencia_val["año"] = pd.to_datetime(valencia_val["date"]).dt.year
    valencia_val = valencia_val.sort_values("date").drop_duplicates(
        ["player_id", "año"], keep="last")
    valor_anual = valencia_val.groupby("año")["market_value_in_eur"].sum().reset_index()
    valor_anual["valor_total"] = valor_anual["market_value_in_eur"] / 1_000_000
    valor_anual = valor_anual[valor_anual["año"].between(2004, 2025)][["año", "valor_total"]]
    # El año en curso está incompleto en valoraciones: uso el valor actual de la plantilla
    ultimo_año = valor_anual["año"].max()
    valor_anual.loc[valor_anual["año"] == ultimo_año, "valor_total"] = plantilla["valor"].sum()
    valor_anual.to_csv(DATOS_DIR / "valencia_plantilla_total.csv", index=False)

    # Valor y posición de cada jugador, para el treemap
    plantilla_valor = plantilla.dropna(subset=["valor"])
    plantilla_valor = plantilla_valor[["name", "position", "valor"]].sort_values(
        "valor", ascending=False)
    plantilla_valor.to_csv(DATOS_DIR / "valencia_plantilla.csv", index=False)

    # Procedencia de la plantilla por país, con coordenadas para los marcadores
    centroides = pd.read_csv(DATOS_DIR / "centroides_paises.csv")
    procedencia = plantilla.dropna(subset=["country_of_citizenship"]).copy()
    procedencia["iso2"] = procedencia["country_of_citizenship"].map(NOMBRE_A_ISO2)
    procedencia = procedencia.dropna(subset=["iso2"])
    procedencia = procedencia.groupby("iso2").agg(
        pais=("country_of_citizenship", "first"),
        n_jugadores=("player_id", "count"),
    ).reset_index()
    procedencia = procedencia.merge(centroides[["iso2", "lat", "lon"]], on="iso2", how="left")
    procedencia = procedencia.dropna(subset=["lat", "lon"]).sort_values(
        "n_jugadores", ascending=False)
    procedencia.to_csv(DATOS_DIR / "valencia_procedencia.csv", index=False)
    print(f"valencia: {len(plantilla)} jugadores en la plantilla, "
          f"{len(procedencia)} países de origen")


def main():
    valoraciones = cargar_valoraciones()
    valores_actuales = valor_actual(valoraciones)
    jugadores = cargar_jugadores_actuales()
    preparar_talento_temporal(valoraciones)
    preparar_ligas_resumen(jugadores)
    preparar_valor_temporal()
    preparar_valor_por_posicion(jugadores, valores_actuales)
    simplificar_cartografia()
    preparar_valencia(valoraciones, valores_actuales)
    print("Preprocesado completado.")


if __name__ == "__main__":
    main()
