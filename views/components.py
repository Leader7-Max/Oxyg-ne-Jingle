"""Composants partagés : panneau d'effets complet et lecteur de résultat."""
import streamlit as st

import theme
from engine.fx import DEFAULTS, PRESETS


def fx_panel(prefix: str, default: str = "Naturel") -> dict:
    names = list(PRESETS)
    preset = st.selectbox("Preset d'effets", names, index=names.index(default) if default in names else 0,
                          key=f"{prefix}_preset")
    base = {**DEFAULTS, **PRESETS[preset]}

    def k(n):  # clé liée au preset : changer de preset recharge ses valeurs
        return f"{prefix}_{preset}_{n}"

    p = {}
    t1, t2, t3, t4 = st.tabs(["Essentiel", "Tonalité", "Caractère", "Modulation"])
    with t1:
        p["gain_db"] = st.slider("Gain (dB)", -12.0, 12.0, float(base["gain_db"]), 0.5, key=k("g"))
        p["echo_mix"] = st.slider("Écho — niveau", 0.0, 1.0, float(base["echo_mix"]), 0.05, key=k("em"))
        p["echo_ms"] = st.slider("Écho — délai (ms)", 20, 1000, int(base["echo_ms"]), 10, key=k("ems"))
        p["echo_fb"] = st.slider("Écho — répétitions", 0.0, 0.9, float(base["echo_fb"]), 0.05, key=k("efb"))
        p["echo_pp"] = st.checkbox("Écho ping-pong (gauche / droite)", value=bool(base["echo_pp"]), key=k("epp"))
        p["reverb_wet"] = st.slider("Reverb — niveau", 0.0, 1.0, float(base["reverb_wet"]), 0.05, key=k("rw"))
        p["reverb_room"] = st.slider("Reverb — taille de salle", 0.0, 1.0, float(base["reverb_room"]), 0.05, key=k("rr"))
    with t2:
        p["hp_hz"] = st.slider("Coupe-bas (Hz)", 20, 1000, int(base["hp_hz"]), 10, key=k("hp"))
        p["lp_hz"] = st.slider("Coupe-haut (Hz)", 2000, 20000, int(base["lp_hz"]), 500, key=k("lp"))
        p["low_db"] = st.slider("Chaleur 150 Hz (dB)", -12.0, 12.0, float(base["low_db"]), 0.5, key=k("lo"))
        p["mud_db"] = st.slider("Boue 320 Hz (dB)", -12.0, 12.0, float(base["mud_db"]), 0.5, key=k("mu"))
        p["mid_db"] = st.slider("Présence 3,5 kHz (dB)", -12.0, 12.0, float(base["mid_db"]), 0.5, key=k("mi"))
        p["high_db"] = st.slider("Air 9 kHz (dB)", -12.0, 12.0, float(base["high_db"]), 0.5, key=k("hi"))
        p["pitch_st"] = st.slider("Hauteur (demi-tons)", -12.0, 12.0, float(base["pitch_st"]), 0.5, key=k("pi"))
    with t3:
        p["deess"] = st.slider("De-esser (sifflantes)", 0.0, 1.0, float(base["deess"]), 0.05, key=k("de"))
        p["comp_thr"] = st.slider("Compresseur — seuil (dB, 0 = off)", -40.0, 0.0, float(base["comp_thr"]), 1.0, key=k("ct"))
        p["comp_ratio"] = st.slider("Compresseur — ratio", 1.0, 10.0, float(base["comp_ratio"]), 0.5, key=k("cr"))
        p["gate_db"] = st.slider("Gate anti-bruit (dB, -80 = off)", -80.0, -20.0, float(base["gate_db"]), 1.0, key=k("ga"))
        p["drive_db"] = st.slider("Saturation (dB)", 0.0, 30.0, float(base["drive_db"]), 1.0, key=k("dr"))
        p["crush_bits"] = st.slider("Bitcrusher (bits, 16 = off)", 4, 16, int(base["crush_bits"]), 1, key=k("bc"))
        p["limiter"] = st.checkbox("Limiteur de sécurité", value=bool(base["limiter"]), key=k("li"))
    with t4:
        p["chorus_mix"] = st.slider("Chorus", 0.0, 1.0, float(base["chorus_mix"]), 0.05, key=k("ch"))
        p["flanger_mix"] = st.slider("Flanger (effet jet)", 0.0, 1.0, float(base["flanger_mix"]), 0.05, key=k("fl"))
        p["phaser_mix"] = st.slider("Phaser", 0.0, 1.0, float(base["phaser_mix"]), 0.05, key=k("ph"))
        p["trem_depth"] = st.slider("Trémolo — profondeur", 0.0, 1.0, float(base["trem_depth"]), 0.05, key=k("td"))
        p["trem_hz"] = st.slider("Trémolo — vitesse (Hz)", 0.5, 20.0, float(base["trem_hz"]), 0.5, key=k("th"))
        p["ring_mix"] = st.slider("Modulation en anneau (robot / dalek)", 0.0, 1.0, float(base["ring_mix"]), 0.05, key=k("rm"))
        p["ring_hz"] = st.slider("Modulation — fréquence (Hz)", 20, 2000, int(base["ring_hz"]), 10, key=k("rh"))
        p["width"] = st.slider("Largeur stéréo", 0.0, 2.0, float(base["width"]), 0.1, key=k("wi"))
        p["reverse"] = st.checkbox("Inverser la voix (lecture à l'envers)", value=bool(base["reverse"]), key=k("rv"))
    return p


def _num(v: float, unit: str) -> str:
    return f"{v:.1f} {unit}" if v > -90 else f"— {unit}"


def player(item: dict, key: str) -> None:
    theme.chips([("⏱", f"{item['seconds']:.1f} s"), ("🔊", _num(item["lufs"], "LUFS")),
                 ("📈", _num(item["peak"], "dBFS"))])
    theme.waveform(item["peaks"])
    if item.get("layout"):
        with st.expander("Vue d'ensemble de la timeline"):
            theme.timeline(item["layout"], item["seconds"])
    st.audio(item["wav"], format="audio/wav")
    cols = st.columns(3 if item.get("stems") else 2)
    cols[0].download_button("⬇️ WAV 24-bit", item["wav"], file_name=f"{item['name']}.wav",
                            mime="audio/wav", key=f"{key}_wav", use_container_width=True)
    cols[1].download_button("⬇️ MP3 HQ", item["mp3"] or b"", file_name=f"{item['name']}.mp3",
                            mime="audio/mpeg", key=f"{key}_mp3", use_container_width=True,
                            disabled=item["mp3"] is None)
    if item.get("stems"):
        cols[2].download_button("📦 Stems (ZIP)", item["stems"], file_name=f"{item['name']}-stems.zip",
                                mime="application/zip", key=f"{key}_zip", use_container_width=True)
