"""Fabrication d'une piste de voix : synthèse ou clip enregistré -> effets -> épaisseur -> niveau -> pan."""
from __future__ import annotations

from engine import audio, fx, layers, tts


def build_voice(cfg: dict, background: bool = False):
    if cfg.get("clip") is not None:          # voix enregistrée (clip du Labo voix)
        a = cfg["clip"]
    else:
        text = "\n".join([cfg["text"].strip()] * int(cfg.get("repeat", 1)))
        a = tts.render_script(text, cfg["voice"], cfg["voice"], cfg["rate"], cfg["pitch"], cfg["vol"],
                              gap_s=0.45 if background else 0.25)
    a = fx.process(a, cfg["params"])
    a = layers.thicken(a, cfg["thick"])
    a = audio.normalize(a, -3.0) * audio.db_to_lin(cfg["level"])
    return layers.pan(a, cfg["pan"])
