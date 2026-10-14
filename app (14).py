"""Routeur Oxygène Jingle — volontairement minimal.
Toute la logique vit dans engine/ (audio) et views/ (pages)."""
from importlib import import_module

import streamlit as st

from config import APP_ICON, APP_NAME

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")

import theme  # noqa: E402  (après set_page_config)

PAGES = {
    "🎙️ Studio jingle": "views.studio",
    "🎚️ Labo voix": "views.voice_lab",
    "📚 Bibliothèque": "views.library",
}


def main() -> None:
    theme.apply()
    with st.sidebar:
        theme.brand()
        choice = st.radio("Navigation", list(PAGES), label_visibility="collapsed")
        theme.footer()
    import_module(PAGES[choice]).render()  # seule la page active est chargée


main()
