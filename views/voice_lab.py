"""Page Labo voix : traite une voix enregistrée (micro ou fichier) comme en studio."""
import streamlit as st

import theme
from engine import audio, fx, master, store
from views.components import fx_panel, player

TARGETS = {"Crête seulement": None, "-16 LUFS · vidéo / podcast": -16.0,
           "-14 LUFS · streaming / radio": -14.0, "-11 LUFS · club / festival": -11.0}


def render() -> None:
    theme.header("Labo voix", "Importe ou enregistre une voix, nettoie-la et donne-lui un son de studio.",
                 ["De-esser", "Compression", "EQ", "LUFS"])

    src = st.radio("Source", ["Importer un fichier", "Micro"], horizontal=True)
    data = None
    if src == "Importer un fichier":
        up = st.file_uploader("Voix (wav, mp3, flac, ogg)", type=["wav", "mp3", "flac", "ogg"])
        data = up.getvalue() if up else None
    elif hasattr(st, "audio_input"):
        rec = st.audio_input("Enregistre ta voix")
        data = rec.getvalue() if rec else None
    else:
        st.info("Mets à jour Streamlit pour utiliser le micro, ou importe un fichier.")
    if not data:
        return

    try:
        voice = audio.decode(data)
    except Exception as e:  # noqa: BLE001
        st.error(f"Fichier illisible ({e}). Utilise du wav, mp3, flac ou ogg.")
        return

    st.caption("Original")
    st.audio(data)

    theme.section("Traitement", 1)
    params = fx_panel("lab", "Studio Pro — voix off")
    c1, c2 = st.columns(2)
    trim = c1.checkbox("Couper les silences début/fin", value=True)
    target = TARGETS[c2.selectbox("Loudness", list(TARGETS), index=2)]

    with st.spinner("Traitement…"):
        out = fx.process(voice, params)
        if trim:
            out = audio.trim_silence(out)
        out = master.master(out, target, -1.0, glue=False, air=False) if target else audio.normalize(out, -1.0)
        item = store.make_item("voix-traitee", out)

    theme.section(f"Résultat · {item['seconds']:.1f} s", 2)
    player(item, "lab")
    if st.button("📚 Ajouter à la bibliothèque", use_container_width=True):
        store.push(item)
        st.toast("Ajouté à la bibliothèque")
