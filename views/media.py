"""Page Médiathèque : importe et gère tes voix, effets et musiques (utilisables dans le Studio et la Voix off)."""
import os

import streamlit as st

import theme
from engine import audio, denoise, store
from views.components import AUDIO_TYPES
from views.helptexts import h

KINDS = {"Voix": "voix", "Effet": "effet", "Musique": "musique"}
ICONS = {"voix": "🗣️", "effet": "🎛️", "musique": "🎵"}


def render() -> None:
    theme.header("Médiathèque", "Tes voix, effets et musiques importés. Ils sont ensuite disponibles dans le Studio et la Voix off.",
                 ["Import", "Voix", "Effets", "Musiques"])
    t_imp, t_voix, t_fx, t_mus = st.tabs(["➕ Importer", "🗣️ Voix", "🎛️ Effets", "🎵 Musiques"])

    with t_imp:
        st.info("Dépose tes fichiers (wav, mp3, flac, ogg). Après l'import, retrouve-les dans le Studio : "
                "onglet **② Voix** (source « Voix importée »), **③ Effets & sons** et **⑤ Musique**.")
        kind = KINDS[st.radio("Type de fichiers", list(KINDS), horizontal=True, key="media_kind", help=h("kind"))]
        files = st.file_uploader("Fichiers audio", type=AUDIO_TYPES, accept_multiple_files=True, key="media_up", help=h("import"))
        c1, c2 = st.columns(2)
        clean = c1.toggle("Nettoyer le bruit (voix)", value=False, disabled=kind != "voix", key="media_clean", help=h("m_clean"))
        norm = c2.toggle("Égaliser le volume", value=True, key="media_norm", help=h("m_norm"))
        if st.button("Importer dans la médiathèque", type="primary", use_container_width=True, disabled=not files):
            for f in files:
                sig = (kind, f.name, f.size)
                if store.has_sig(sig):
                    continue
                try:
                    a = audio.decode(f.getvalue())
                    if clean and kind == "voix":
                        a = denoise.denoise(a, 0.6)
                    if norm:
                        a = audio.normalize(a, -3.0)
                    store.add_media(kind, os.path.splitext(f.name)[0], a, sig)
                except Exception as e:  # noqa: BLE001
                    st.error(f"« {f.name} » illisible ({e}).")
            st.toast("Import terminé")

    for tab, kind in zip((t_voix, t_fx, t_mus), KINDS.values()):
        with tab:
            items = store.media(kind)
            if not items:
                st.info("Rien ici pour l'instant — utilise l'onglet « Importer ».")
                continue
            mid = st.selectbox("Choisir un fichier", [m["id"] for m in items], key=f"media_sel_{kind}",
                               format_func=lambda x: f"{ICONS[kind]} {store.get_media(x)['name']} · {store.get_media(x)['seconds']:.1f} s")
            m = store.get_media(mid)
            theme.waveform(audio.peaks(m["audio"], 240))
            st.audio(audio.export(m["audio"], "wav", 16), format="audio/wav")
            if st.button("🗑️ Supprimer", key=f"media_del_{kind}_{mid}"):
                store.remove_media(mid)
                st.rerun()
