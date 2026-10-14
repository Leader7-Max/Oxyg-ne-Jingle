"""Composants d'interface partagés : panneau d'effets et lecteur de résultat."""
import streamlit as st

from engine.fx import DEFAULTS, PRESETS


def fx_panel(prefix: str, default: str = "Naturel") -> dict:
    names = list(PRESETS)
    preset = st.selectbox("Preset d'effets", names, index=names.index(default),
                          key=f"{prefix}_preset")
    base = {**DEFAULTS, **PRESETS[preset]}

    def k(n):  # clé liée au preset : changer de preset recharge ses valeurs
        return f"{prefix}_{preset}_{n}"

    p = {}
    t1, t2, t3 = st.tabs(["Essentiel", "Tonalité", "Caractère"])
    with t1:
        p["gain_db"] = st.slider("Gain (dB)", -12.0, 12.0, float(base["gain_db"]), 0.5, key=k("g"))
        p["echo_mix"] = st.slider("Écho — niveau", 0.0, 1.0, float(base["echo_mix"]), 0.05, key=k("em"))
        p["echo_ms"] = st.slider("Écho — délai (ms)", 20, 1000, int(base["echo_ms"]), 10, key=k("ems"))
        p["echo_fb"] = st.slider("Écho — répétitions", 0.0, 0.9, float(base["echo_fb"]), 0.05, key=k("efb"))
        p["reverb_wet"] = st.slider("Reverb — niveau", 0.0, 1.0, float(base["reverb_wet"]), 0.05, key=k("rw"))
        p["reverb_room"] = st.slider("Reverb — taille de salle", 0.0, 1.0, float(base["reverb_room"]), 0.05, key=k("rr"))
    with t2:
        p["hp_hz"] = st.slider("Coupe-bas (Hz)", 20, 1000, int(base["hp_hz"]), 10, key=k("hp"))
        p["lp_hz"] = st.slider("Coupe-haut (Hz)", 2000, 20000, int(base["lp_hz"]), 500, key=k("lp"))
        p["low_db"] = st.slider("Graves (dB)", -12.0, 12.0, float(base["low_db"]), 0.5, key=k("lo"))
        p["mid_db"] = st.slider("Présence (dB)", -12.0, 12.0, float(base["mid_db"]), 0.5, key=k("mi"))
        p["high_db"] = st.slider("Aigus (dB)", -12.0, 12.0, float(base["high_db"]), 0.5, key=k("hi"))
        p["pitch_st"] = st.slider("Hauteur (demi-tons)", -12.0, 12.0, float(base["pitch_st"]), 0.5, key=k("pi"))
    with t3:
        p["comp_thr"] = st.slider("Compresseur — seuil (dB, 0 = off)", -40.0, 0.0, float(base["comp_thr"]), 1.0, key=k("ct"))
        p["comp_ratio"] = st.slider("Compresseur — ratio", 1.0, 10.0, float(base["comp_ratio"]), 0.5, key=k("cr"))
        p["gate_db"] = st.slider("Gate anti-bruit (dB, -80 = off)", -80.0, -20.0, float(base["gate_db"]), 1.0, key=k("ga"))
        p["drive_db"] = st.slider("Saturation (dB)", 0.0, 30.0, float(base["drive_db"]), 1.0, key=k("dr"))
        p["chorus_mix"] = st.slider("Chorus", 0.0, 1.0, float(base["chorus_mix"]), 0.05, key=k("ch"))
        p["crush_bits"] = st.slider("Bitcrusher (bits, 16 = off)", 4, 16, int(base["crush_bits"]), 1, key=k("bc"))
        p["limiter"] = st.checkbox("Limiteur de sécurité", value=bool(base["limiter"]), key=k("li"))
    return p


def player(item: dict, key: str) -> None:
    st.audio(item["wav"], format="audio/wav")
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ WAV (qualité studio)", item["wav"], file_name=f"{item['name']}.wav",
                       mime="audio/wav", key=f"{key}_wav", use_container_width=True)
    c2.download_button("⬇️ MP3 192 kbit/s", item["mp3"] or b"", file_name=f"{item['name']}.mp3",
                       mime="audio/mpeg", key=f"{key}_mp3", use_container_width=True,
                       disabled=item["mp3"] is None)
