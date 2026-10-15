"""Fabrication d'une piste de voix : lecture (texte ou clip) -> effets -> épaisseur -> niveau -> pan."""
from __future__ import annotations

from engine import audio, fx, layers, reader


def build_voice(cfg: dict, background: bool = False, with_timings: bool = False):
    timings = None
    if cfg.get("clip") is not None:                  # voix importée / enregistrée
        a = cfg["clip"]
    else:
        text = "\n".join([cfg["text"].strip()] * int(cfg.get("repeat", 1)))
        plan = reader.build_plan(text, cfg["voice"], cfg.get("style", "Naturel"), cfg["rate"], cfg["pitch"],
                                 cfg["vol"], pro=cfg.get("pro", True) and not background,
                                 caps=cfg.get("caps", False), gap=0.45 if background else 0.25)
        a, timings = reader.render(plan, cfg["voice"])
    a = fx.process(a, cfg["params"])
    a = layers.thicken(a, cfg["thick"])
    a = audio.normalize(a, -3.0) * audio.db_to_lin(cfg["level"])
    a = layers.pan(a, cfg["pan"])
    return (a, timings) if with_timings else a
