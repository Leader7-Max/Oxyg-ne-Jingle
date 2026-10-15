"""Routeur Oxygène Jingle — volontairement minimal.
La navigation est groupée par catégories ; toute la logique vit dans engine/ et views/."""
from importlib import import_module

import streamlit as st

from config import APP_ICON, APP_NAME

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")

import theme  # noqa: E402  (après set_page_config)


def _page(module: str, title: str, icon: str, path: str, default: bool = False):
    def run() -> None:
        import_module(module).render()  # seule la page active est chargée

    return st.Page(run, title=title, icon=icon, url_path=path, default=default)


PAGES = {
    "Créer": [_page("views.studio", "Studio jingle", "🎙️", "studio", True),
              _page("views.voice_over", "Voix off", "🎬", "voix-off")],
    "Préparer": [_page("views.voice_lab", "Labo voix", "🎚️", "labo-voix"),
                 _page("views.media", "Médiathèque", "📁", "mediatheque"),
                 _page("views.sounds", "Sons & nappes", "🥁", "sons-nappes")],
    "Mes créations": [_page("views.library", "Bibliothèque", "📚", "bibliotheque")],
    "Aide": [_page("views.guide", "Guide débutant", "❓", "aide")],
}


def main() -> None:
    theme.apply()
    pg = st.navigation(PAGES)
    with st.sidebar:
        theme.footer()
    pg.run()


main()
