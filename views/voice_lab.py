"""Page Labo voix : prise de voix -> anti-bruit -> montage (couper/supprimer) -> effets -> clip."""
import numpy as np
import streamlit as st

import theme
from engine import audio, denoise, edit, fx, master, store
from views.components import fx_panel, player

TARGETS = {"Crête seulement": None, "-16 LUFS · vidéo / podcast": -16.0,
           "-14 LUFS · streaming / radio": -14.0, "-11 LUFS · club / festival": -11.0}
HUMS = ["Aucun", "50 Hz (Europe)", "60 Hz (Amérique)"]


@st.cache_data(show_spinner=False, max_entries=4)
def _clean(data: bytes, nr_on: bool, strength: float, use_start: bool, start_s: float, hum: str):
    a = audio.decode(data)
    if hum != "Aucun":
        a = denoise.remove_hum(a, 50.0 if hum.startswith("50") else 60.0)
    if nr_on:
        a = denoise.denoise(a, strength, start_s if use_start else None)
    return a


def _describe(op) -> str:
    if op[0] == "cut":
        return f"✂️ supprimé {op[1]:.2f}–{op[2]:.2f} s"
    if op[0] == "keep":
        return f"🎯 gardé {op[1]:.2f}–{op[2]:.2f} s"
    return f"🤫 silences > {op[2]:.1f} s"


def render() -> None:
    theme.header("Labo voix", "Prise de voix : anti-bruit, coupe, effets complets, puis envoi au Studio.",
                 ["Anti-bruit", "Couper / supprimer", "Effets", "Clips"])

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

    sig = (len(data), hash(data[:4096]))
    if st.session_state.get("lab_sig") != sig:      # nouvel enregistrement : on repart de zéro
        st.session_state["lab_sig"], st.session_state["lab_ops"] = sig, []
    ops = st.session_state.setdefault("lab_ops", [])

    # ---- 1. Anti-bruit ----
    theme.section("Anti-bruit", 1)
    nr_on = st.toggle("Réduction de bruit (souffle, ventilateur, fond sonore)", value=True)
    strength = st.slider("Force", 0.0, 1.0, 0.6, 0.05, disabled=not nr_on,
                         help="Trop fort = voix « sous l'eau ». 0,5–0,7 convient à la plupart des prises.")
    c1, c2 = st.columns(2)
    mode = c1.radio("Profil du bruit", ["Automatique", "Début de la prise"], disabled=not nr_on,
                    help="« Début de la prise » : reste silencieux 1 s avant de parler, l'outil apprend le bruit.")
    start_s = c2.slider("Durée du bruit seul (s)", 0.3, 3.0, 0.8, 0.1, disabled=not (nr_on and mode != "Automatique"))
    hum = st.selectbox("Filtre anti-ronflement secteur", HUMS)
    try:
        with st.spinner("Nettoyage de la voix…"):
            clean = _clean(data, nr_on, strength, mode != "Automatique", start_s, hum)
    except Exception as e:  # noqa: BLE001
        st.error(f"Fichier illisible ({e}). Utilise du wav, mp3, flac ou ogg.")
        return
    with st.expander("Comparer avant / après anti-bruit"):
        st.caption("Original")
        st.audio(data)
        st.caption("Nettoyé")
        st.audio(audio.export(clean, "wav", 16), format="audio/wav")

    # ---- 2. Montage : couper / supprimer ----
    theme.section("Couper / supprimer une partie", 2)
    cur = edit.apply_ops(clean, ops)
    dur = audio.duration(cur)
    dur_r = float(np.floor(dur * 20) / 20)
    if dur_r < 0.2:
        st.warning("Audio trop court pour être découpé.")
        sel = (0.0, dur)
    else:
        sel = st.slider("Sélection (secondes)", 0.0, dur_r, (0.0, min(dur_r, max(0.5, round(dur_r * 0.2, 2)))),
                        0.05, key=f"lab_sel_{len(ops)}")
    theme.waveform(audio.peaks(cur, 300), selection=(sel[0] / dur, sel[1] / dur) if dur > 0 else None)
    st.caption(f"Durée actuelle : {dur:.2f} s" + (" · " + " → ".join(_describe(o) for o in ops) if ops else ""))
    if sel[1] > sel[0]:
        with st.expander("▶ Écouter la sélection"):
            seg = cur[:, int(sel[0] * audio.SR): int(sel[1] * audio.SR)]
            if seg.shape[1] > 200:
                st.audio(audio.export(seg, "wav", 16), format="audio/wav")
    r1 = st.columns(2)
    r2 = st.columns(2)
    if r1[0].button("✂️ Supprimer la sélection", use_container_width=True, disabled=dur_r < 0.2):
        ops.append(("cut", float(sel[0]), float(sel[1])))
        st.rerun()
    if r1[1].button("🎯 Garder uniquement la sélection", use_container_width=True, disabled=dur_r < 0.2):
        ops.append(("keep", float(sel[0]), float(sel[1])))
        st.rerun()
    if r2[0].button("↩️ Annuler la dernière action", use_container_width=True, disabled=not ops):
        ops.pop()
        st.rerun()
    if r2[1].button("🔄 Tout réinitialiser", use_container_width=True, disabled=not ops):
        ops.clear()
        st.rerun()
    with st.expander("Supprimer automatiquement les silences"):
        c1, c2 = st.columns(2)
        thr = c1.slider("Seuil de silence (dB)", -60.0, -20.0, -45.0, 1.0)
        min_s = c2.slider("Silence mini (s)", 0.3, 3.0, 0.8, 0.1)
        if st.button("🤫 Raccourcir les silences", use_container_width=True):
            ops.append(("silences", float(thr), float(min_s)))
            st.rerun()
    c1, c2 = st.columns(2)
    fin = c1.slider("Fondu d'entrée (ms)", 0, 500, 10, 10)
    fout = c2.slider("Fondu de sortie (ms)", 0, 1000, 40, 10)
    cur = audio.fade(cur, fin / 1000, fout / 1000)

    # ---- 3. Effets & finition ----
    theme.section("Effets & finition", 3)
    params = fx_panel("lab", "Studio Pro — voix off")
    c1, c2 = st.columns(2)
    trim = c1.checkbox("Ajuster début/fin automatiquement", value=True)
    target = TARGETS[c2.selectbox("Loudness", list(TARGETS), index=2)]

    with st.spinner("Traitement…"):
        out = fx.process(cur, params)
        if trim:
            out = audio.trim_silence(out)
        out = master.master(out, target, -1.0, glue=False, air=False) if target else audio.normalize(out, -1.0)
        item = store.make_item("voix-traitee", out)

    theme.section(f"Résultat · {item['seconds']:.1f} s", 4)
    player(item, "lab")
    name = st.text_input("Nom du clip", "ma-voix")
    c1, c2 = st.columns(2)
    if c1.button("🎙️ Utiliser dans le Studio", type="primary", use_container_width=True):
        store.add_clip(name, out)
        st.toast("Clip disponible dans le Studio (source « Clip du Labo voix »)")
    if c2.button("📚 Ajouter à la bibliothèque", use_container_width=True):
        store.push(item)
        st.toast("Ajouté à la bibliothèque")
