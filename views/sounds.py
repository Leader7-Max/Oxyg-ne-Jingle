"""Page Sons & nappes : écoute et télécharge les effets DJ et les nappes générées."""
import streamlit as st

import theme
from engine import audio, beds, sfx
from views.helptexts import h


@st.cache_data(show_spinner=False)
def _sfx_wav(label: str) -> bytes:
    return audio.export(sfx.get(label), "wav", 16)


@st.cache_data(show_spinner=False)
def _bed_wav(style, bpm, key, seconds, drums, bass, pad) -> bytes:
    return audio.export(beds.render(style, bpm, key, seconds, drums, bass, pad), "wav", 16)


def render() -> None:
    theme.header("Sons & nappes", "Effets DJ synthétisés et nappes musicales libres de droits.",
                 ["Scratch", "Sirènes", "Airhorn", "Nappes"])
    fx_tab, bed_tab = st.tabs(["🎛️ Effets DJ", "🥁 Nappes musicales"])

    with fx_tab:
        label = st.selectbox("Effet", list(sfx.EFFECTS), help=h("sfx_label"))
        wav = _sfx_wav(label)
        st.audio(wav, format="audio/wav")
        st.download_button("⬇️ Télécharger (WAV)", wav, file_name="effet.wav", mime="audio/wav",
                           use_container_width=True)

    with bed_tab:
        c1, c2 = st.columns(2)
        style = c1.selectbox("Style", list(beds.STYLES), help=h("mstyle"))
        note = c2.selectbox("Tonalité", beds.NOTES, index=9, help=h("mkey"))
        bpm = st.slider("Tempo (BPM)", 60, 150, int(beds.STYLES[style]["bpm"]), key=f"bpm_{style}", help=h("bpm"))
        seconds = st.slider("Durée (s)", 5, 60, 20, 5, help="Longueur de la nappe générée, en secondes.")
        e1, e2, e3 = st.columns(3)
        drums = e1.checkbox("Rythmique", True, help=h("drums"))
        bass = e2.checkbox("Basse", True, help=h("bass"))
        pad = e3.checkbox("Accords", True, help=h("pad"))
        if st.button("🥁 Générer la nappe", type="primary", use_container_width=True):
            with st.spinner("Synthèse…"):
                st.session_state["bed_wav"] = _bed_wav(style, bpm, note, seconds, drums, bass, pad)
        if st.session_state.get("bed_wav"):
            st.audio(st.session_state["bed_wav"], format="audio/wav")
            st.download_button("⬇️ Télécharger la nappe (WAV)", st.session_state["bed_wav"],
                               file_name="nappe.wav", mime="audio/wav", use_container_width=True)
