# -*- coding: utf-8 -*-
"""
Punto de entrada de la web.
"""

from pathlib import Path

import streamlit as st

dir_path = Path(__file__).parent / "secciones"


def run():
    page = st.navigation(
        {
            "Páginas": [
                st.Page(dir_path / "inicio.py", title="Inicio",
                        icon=":material/home:"),
                st.Page(dir_path / "talento.py", title="De dónde vienen los jugadores",
                        icon=":material/public:"),
                st.Page(dir_path / "ligas.py", title="El perfil de cada liga",
                        icon=":material/bar_chart:"),
                st.Page(dir_path / "valencia.py", title="El Valencia CF",
                        icon=":material/sports_soccer:"),
            ]
        }
    )
    page.run()


if __name__ == "__main__":
    run()
