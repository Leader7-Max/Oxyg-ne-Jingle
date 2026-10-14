"""Page Bibliothèque : réécoute et téléchargement des créations de la session."""
import streamlit as st

import theme
from engine import store
from views.components import player


def render() -> None:
    theme.header("Bibliothèque", "Tes dernières créations (conservées le temps de la session).")
    lib = store.items()
    if not lib:
        st.info("Rien ici pour l'instant — crée un jingle dans le Studio.")
        return
    for it in lib:
        with st.expander(f"{it['name']} · {it['seconds']:.1f} s · {it['ts']}"):
            player(it, f"lib_{it['id']}")
            if st.button("🗑️ Supprimer", key=f"del_{it['id']}"):
                store.remove(it["id"])
                st.rerun()
