"""Composants partagés : panneau d'effets, choix de voix, import de fichiers, lecteur de résultat."""
import os
import zlib

import streamlit as st

import theme
from config import LANGS, VOICE_META, VOICES
from engine import audio, fx, layers, store, tts
from engine.casting import CHARACTERS
from engine.fx import DEFAULTS, PRESETS
from views.helptexts import h

AUDIO_TYPES = ["wav", "mp3", "flac", "ogg"]
SAMPLES = {"fr": "Oxygène Jingle ! La radio qui vous fait respirer la musique.",
           "en": "Oxygen Jingle! The radio that makes you breathe music.",
           "es": "Oxígeno Jingle, la radio que te hace respirar música.",
           "it": "Ossigeno Jingle, la radio che ti fa respirare la musica.",
           "de": "Sauerstoff Jingle, das Radio, das die Musik atmen lässt.",
           "pt": "Oxigênio Jingle, a rádio que te faz respirar música."}


def _sl(label, lo, hi, val, step, key, hk):
    return st.slider(label, lo, hi, val, step, key=key, help=h(hk))


def fx_panel(prefix: str, default: str = "Naturel") -> dict:
    names = list(PRESETS)
    preset = st.selectbox("Preset d'effets", names, index=names.index(default) if default in names else 0,
                          key=f"{prefix}_preset", help=h("preset"))
    base = {**DEFAULTS, **PRESETS[preset]}

    def k(n):  # clé liée au preset : changer de preset recharge ses valeurs
        return f"{prefix}_{preset}_{n}"

    p = {}
    t1, t2, t3, t4 = st.tabs(["Essentiel", "Tonalité", "Caractère", "Modulation"])
    with t1:
        p["gain_db"] = _sl("Gain (dB)", -12.0, 12.0, float(base["gain_db"]), 0.5, k("g"), "gain_db")
        p["echo_mix"] = _sl("Écho — niveau", 0.0, 1.0, float(base["echo_mix"]), 0.05, k("em"), "echo_mix")
        p["echo_ms"] = _sl("Écho — délai (ms)", 20, 1000, int(base["echo_ms"]), 10, k("ems"), "echo_ms")
        p["echo_fb"] = _sl("Écho — répétitions", 0.0, 0.9, float(base["echo_fb"]), 0.05, k("efb"), "echo_fb")
        p["echo_pp"] = st.checkbox("Écho ping-pong (gauche / droite)", value=bool(base["echo_pp"]), key=k("epp"), help=h("echo_pp"))
        p["reverb_wet"] = _sl("Reverb — niveau", 0.0, 1.0, float(base["reverb_wet"]), 0.05, k("rw"), "reverb_wet")
        p["reverb_room"] = _sl("Reverb — taille de salle", 0.0, 1.0, float(base["reverb_room"]), 0.05, k("rr"), "reverb_room")
    with t2:
        p["hp_hz"] = _sl("Coupe-bas (Hz)", 20, 1000, int(base["hp_hz"]), 10, k("hp"), "hp_hz")
        p["lp_hz"] = _sl("Coupe-haut (Hz)", 2000, 20000, int(base["lp_hz"]), 500, k("lp"), "lp_hz")
        p["low_db"] = _sl("Chaleur 150 Hz (dB)", -12.0, 12.0, float(base["low_db"]), 0.5, k("lo"), "low_db")
        p["mud_db"] = _sl("Boue 320 Hz (dB)", -12.0, 12.0, float(base["mud_db"]), 0.5, k("mu"), "mud_db")
        p["mid_db"] = _sl("Présence 3,5 kHz (dB)", -12.0, 12.0, float(base["mid_db"]), 0.5, k("mi"), "mid_db")
        p["high_db"] = _sl("Air 9 kHz (dB)", -12.0, 12.0, float(base["high_db"]), 0.5, k("hi"), "high_db")
        p["pitch_st"] = _sl("Hauteur (demi-tons)", -12.0, 12.0, float(base["pitch_st"]), 0.5, k("pi"), "pitch_st")
    with t3:
        p["deess"] = _sl("De-esser (sifflantes)", 0.0, 1.0, float(base["deess"]), 0.05, k("de"), "deess")
        p["comp_thr"] = _sl("Compresseur — seuil (dB, 0 = off)", -40.0, 0.0, float(base["comp_thr"]), 1.0, k("ct"), "comp_thr")
        p["comp_ratio"] = _sl("Compresseur — force", 1.0, 10.0, float(base["comp_ratio"]), 0.5, k("cr"), "comp_ratio")
        p["gate_db"] = _sl("Gate anti-bruit (dB, -80 = off)", -80.0, -20.0, float(base["gate_db"]), 1.0, k("ga"), "gate_db")
        p["drive_db"] = _sl("Saturation (dB)", 0.0, 30.0, float(base["drive_db"]), 1.0, k("dr"), "drive_db")
        p["crush_bits"] = _sl("Bitcrusher (bits, 16 = off)", 4, 16, int(base["crush_bits"]), 1, k("bc"), "crush_bits")
        p["limiter"] = st.checkbox("Limiteur de sécurité", value=bool(base["limiter"]), key=k("li"), help=h("limiter"))
    with t4:
        p["chorus_mix"] = _sl("Chorus", 0.0, 1.0, float(base["chorus_mix"]), 0.05, k("ch"), "chorus_mix")
        p["flanger_mix"] = _sl("Flanger (effet jet)", 0.0, 1.0, float(base["flanger_mix"]), 0.05, k("fl"), "flanger_mix")
        p["phaser_mix"] = _sl("Phaser", 0.0, 1.0, float(base["phaser_mix"]), 0.05, k("ph"), "phaser_mix")
        p["trem_depth"] = _sl("Trémolo — profondeur", 0.0, 1.0, float(base["trem_depth"]), 0.05, k("td"), "trem_depth")
        p["trem_hz"] = _sl("Trémolo — vitesse (Hz)", 0.5, 20.0, float(base["trem_hz"]), 0.5, k("th"), "trem_hz")
        p["ring_mix"] = _sl("Modulation en anneau (robot / dalek)", 0.0, 1.0, float(base["ring_mix"]), 0.05, k("rm"), "ring_mix")
        p["ring_hz"] = _sl("Modulation — fréquence (Hz)", 20, 2000, int(base["ring_hz"]), 10, k("rh"), "ring_hz")
        p["width"] = _sl("Largeur stéréo", 0.0, 2.0, float(base["width"]), 0.1, k("wi"), "width")
        p["reverse"] = st.checkbox("Inverser la voix (à l'envers)", value=bool(base["reverse"]), key=k("rv"), help=h("reverse"))
    return p


def import_box(kind: str, key: str, label: str, help_key: str = "import") -> None:
    """Zone d'import : les fichiers déposés entrent dans la médiathèque (voix, effet ou musique)."""
    files = st.file_uploader(label, type=AUDIO_TYPES, accept_multiple_files=True, key=f"imp_{key}", help=h(help_key))
    for f in files or []:
        sig = (kind, f.name, f.size)
        if store.has_sig(sig):
            continue
        try:
            store.add_media(kind, os.path.splitext(f.name)[0], audio.decode(f.getvalue()), sig)
            st.toast(f"« {f.name} » ajouté à la médiathèque")
        except Exception as e:  # noqa: BLE001
            st.error(f"Impossible de lire « {f.name} » ({e}). Formats : wav, mp3, flac, ogg.")


def _audition(vp: dict) -> None:
    vid = VOICES.get(vp["voice"], vp["voice"])
    try:
        with st.spinner("Préparation de l'extrait…"):
            a = tts.synthesize(SAMPLES.get(vid.split("-")[0], SAMPLES["en"]), vp["voice"], vp["rate"], vp["pitch"], vp["vol"])
            a = fx.process(a, PRESETS.get(vp["preset"], {}))
            a = audio.normalize(layers.thicken(a, vp["thick"]), -3.0)
            st.audio(audio.export(a, "wav", 16), format="audio/wav")
    except Exception as e:  # noqa: BLE001
        st.error(f"Extrait impossible : {e}")


def voice_picker(prefix: str, d: dict) -> dict:
    """Choix d'une voix : caractère prêt à l'emploi ou catalogue filtrable. Retourne les réglages de départ."""
    chars = list(CHARACTERS)
    modes = ["⭐ Voix de caractère", "📚 Catalogue de voix"]
    mode = st.radio("Choix de la voix", modes, horizontal=True, index=0 if d.get("char") else 1,
                    key=f"{prefix}_mode", help=h("picker_mode"))
    if mode == modes[0]:
        ch = st.selectbox("Caractère", chars, index=chars.index(d["char"]) if d.get("char") in chars else 0,
                          key=f"{prefix}_char", help=h("char"))
        c = CHARACTERS[ch]
        st.caption(c["desc"])
        vp = dict(voice=c["voice"], rate=c["rate"], pitch=c["pitch"], vol=c["vol"], preset=c["preset"],
                  thick=c["thick"], level=c.get("level", 0.0), style=c["style"], sig=ch)
    else:
        c1, c2 = st.columns(2)
        lang = c1.selectbox("Langue", ["Toutes"] + list(LANGS.values()), key=f"{prefix}_lang", help=h("lang"))
        gender = c2.selectbox("Genre", ["Tous", "Homme", "Femme"], key=f"{prefix}_gen", help=h("gender"))
        code = next((k for k, v in LANGS.items() if v == lang), None)
        opts = [lb for lb, m in VOICE_META.items() if (code is None or m["lang"] == code)
                and (gender == "Tous" or m["gender"] == ("H" if gender == "Homme" else "F"))] or list(VOICES)
        voice = st.selectbox("Voix", opts, index=opts.index(d["voice"]) if d.get("voice") in opts else 0,
                             key=f"{prefix}_voice", help=h("voice"))
        vp = dict(voice=voice, rate=0, pitch=0, vol=0, preset=d["preset"], thick=d["thick"],
                  level=d["level"], style="Naturel", sig=voice)
    vp["sig"] = f"{zlib.crc32(vp['sig'].encode()):x}"
    if st.button("▶ Écouter un extrait", key=f"{prefix}_aud_{vp['sig']}", help=h("audition")):
        _audition(vp)
    return vp


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
    btns = [("⬇️ WAV 24-bit", item["wav"], f"{item['name']}.wav", "audio/wav", "wav", False),
            ("⬇️ MP3 HQ", item["mp3"] or b"", f"{item['name']}.mp3", "audio/mpeg", "mp3", item["mp3"] is None)]
    if item.get("stems"):
        btns.append(("📦 Stems (ZIP)", item["stems"], f"{item['name']}-stems.zip", "application/zip", "zip", False))
    if item.get("srt"):
        btns.append(("📝 Sous-titres .srt", item["srt"].encode("utf-8"), f"{item['name']}.srt", "text/plain", "srt", False))
    for col, (label, data, fname, mime, kk, dis) in zip(st.columns(len(btns)), btns):
        col.download_button(label, data, file_name=fname, mime=mime, key=f"{key}_{kk}",
                            use_container_width=True, disabled=dis)
