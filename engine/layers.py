"""Épaisseur de voix (double, octave, chœur) et panoramique."""
from __future__ import annotations

import numpy as np
from pedalboard import PitchShift

from engine.audio import SR, db_to_lin

MODES = ["Aucune", "Double voix", "Double + octave grave", "Chœur 3 voix"]


def pan(a: np.ndarray, p: float) -> np.ndarray:
    """Panoramique à puissance constante (-1 gauche … +1 droite)."""
    if abs(p) < 0.01:
        return a
    ang = (p + 1) * np.pi / 4
    mono = a.mean(axis=0)
    return (np.vstack([mono * np.cos(ang), mono * np.sin(ang)]) * np.sqrt(2)).astype(np.float32)


def _layer(base: np.ndarray, semis: float, ms: float, p: float, gain_db: float) -> np.ndarray:
    x = PitchShift(float(semis))(base, SR) if semis else base.copy()
    x = np.hstack([np.zeros((2, int(ms * SR / 1000)), np.float32), x])[:, : base.shape[1]]
    return pan(x, p) * db_to_lin(gain_db)


def thicken(a: np.ndarray, mode: str) -> np.ndarray:
    if mode == "Aucune":
        return a
    base = np.ascontiguousarray(np.hstack([a, np.zeros((2, int(0.08 * SR)), np.float32)]), dtype=np.float32)
    out = base.copy()
    if mode in ("Double voix", "Double + octave grave"):
        out += _layer(base, +0.12, 18, -0.7, -5) + _layer(base, -0.12, 27, 0.7, -5)
    if mode == "Double + octave grave":
        out += _layer(base, -12, 0, 0.0, -9)
    if mode == "Chœur 3 voix":
        out += _layer(base, 0.20, 14, -0.8, -4) + _layer(base, -0.25, 26, 0.8, -4) + _layer(base, 0.40, 38, 0.0, -6)
    return out
