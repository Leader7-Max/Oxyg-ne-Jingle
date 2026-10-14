"""Page Labo voix : nettoie et met en forme une voix enregistrée ou importée."""
import streamlit as st

import theme
from engine import audio, fx, store
from views.components import fx_panel, player


def render() -> None:
    theme.header("Labo voix", "Importe ou enregistre une voix, puis nettoie-la et donne-lui du caractère.")

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

    theme.section("Traitement")
    params = fx_panel("lab", "Nettoyage voix")
    c1, c2 = st.columns(2)
    trim = c1.checkbox("Couper les silences début/fin", value=True)
    peak = c2.slider("Niveau crête final (dB)", -6.0, 0.0, -1.0, 0.5)

    with st.spinner("Traitement…"):
        out = fx.process(voice, params)
        if trim:
            out = audio.trim_silence(out)
        out = audio.normalize(out, peak)
        item = {"id": "lab", "name": "voix-traitee", "seconds": audio.duration(out),
                "wav": audio.export(out, "wav"), "mp3": None}
        try:
            item["mp3"] = audio.export(out, "mp3")
        except Exception:  # noqa: BLE001
            pass

    theme.section(f"Résultat · {item['seconds']:.1f} s")
    player(item, "lab")
    if st.button("📚 Ajouter à la bibliothèque", use_container_width=True):
        store.add("voix-traitee", out)
        st.toast("Ajouté à la bibliothèque")
