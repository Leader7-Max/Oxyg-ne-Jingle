"""Générateur de nappes musicales (rythmique + basse + accords) — 100 % synthétisé, libre de droits."""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from engine import synth as sy
from engine.audio import SR, normalize

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

_MINOR = {"chords": [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]], "roots": [0, -4, 3, -2]}   # i-VI-III-VII
_MAJOR = {"chords": [[0, 4, 7], [-5, -1, 2], [-3, 0, 4], [-7, -3, 0]], "roots": [0, -5, -3, -7]}  # I-V-vi-IV
_EVEN = list(range(0, 16, 2))

STYLES = {
    "House": dict(bpm=124, mode=_MINOR, kick=[0, 4, 8, 12], snare=[], clap=[4, 12], ch=[], oh=[2, 6, 10, 14],
                  bass=[(2, 2), (6, 2), (10, 2), (14, 2)], stab=[3, 6, 11, 14], pump=0.65, attack=0.05),
    "Hip-Hop": dict(bpm=90, mode=_MINOR, kick=[0, 7, 10], snare=[4, 12], clap=[], ch=_EVEN, oh=[],
                    bass=[(0, 3), (7, 2), (10, 5)], stab=[], pump=0.0, attack=0.1),
    "Techno": dict(bpm=130, mode=_MINOR, kick=[0, 4, 8, 12], snare=[], clap=[4, 12], ch=list(range(1, 16, 2)),
                   oh=[2, 6, 10, 14], bass=[(i, 1) for i in range(16) if i % 4], stab=[], pump=0.55, attack=0.05),
    "Pop / Dance": dict(bpm=118, mode=_MAJOR, kick=[0, 4, 8, 12], snare=[], clap=[4, 12], ch=_EVEN, oh=[],
                        bass=[(0, 2), (4, 2), (8, 2), (12, 2)], stab=[2, 6, 10, 14], pump=0.35, attack=0.08),
    "Chill / Lo-fi": dict(bpm=80, mode=_MINOR, kick=[0, 10], snare=[4, 12], clap=[], ch=_EVEN, oh=[],
                          bass=[(0, 6), (8, 6)], stab=[], pump=0.0, attack=0.2),
    "Cinématique": dict(bpm=70, mode=_MINOR, kick=[0], snare=[], clap=[], ch=[], oh=[],
                        bass=[(0, 16)], stab=[], pump=0.0, attack=0.8),
}


def _hz(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


@lru_cache(maxsize=64)
def _chord(midis: tuple, dur: float, attack: float, release: float) -> np.ndarray:
    """Accord stéréo (2 jeux de désaccords pour l'ampleur)."""
    t = np.arange(int(dur * SR)) / SR
    sides = []
    for dets in ((0.997, 1.0, 1.003), (1.004, 1.0, 0.996)):
        sig = np.zeros(t.size)
        for m in midis:
            for d in dets:
                sig += sy.band_saw(_hz(m) * d, t, max_hz=2200.0, kmax=14)
        sides.append(sig)
    x = sy.lp(np.vstack(sides), 1800.0)
    env = np.minimum(1.0, t / max(attack, 1e-3)) * np.minimum(1.0, np.maximum(dur - t, 0) / max(release, 1e-3))
    x = x * env
    return (x / (np.abs(x).max() + 1e-9)).astype(np.float32)


def _bass(freq: float, dur: float) -> np.ndarray:
    t = sy.t_axis(dur)
    sig = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) * np.exp(-t * 5)
    env = np.minimum(1, t / 0.004) * np.exp(-t * 1.6) * np.minimum(1, np.maximum(dur - t, 0) / 0.03)
    return (np.tanh(1.5 * sig) * env * 0.8).astype(np.float32)


@lru_cache(maxsize=8)
def _render(style: str, bpm: int, key: str, seconds: float, drums: bool, bass: bool, pad: bool) -> np.ndarray:
    s, mode = STYLES[style], STYLES[style]["mode"]
    spb = 60.0 / bpm
    stp, bar = spb / 4, spb * 4
    bars = int(np.ceil(seconds / bar)) + 1
    n = int(bars * bar * SR)
    k = NOTES.index(key)
    d_bus, b_bus, p_bus, s_bus = (np.zeros((2, n), np.float32) for _ in range(4))

    def put(bus, x, when, gain=1.0):
        i = int(when * SR)
        if i >= n:
            return
        x = x if x.ndim == 2 else np.vstack([x, x])
        seg = x[:, : n - i]
        bus[:, i : i + seg.shape[1]] += seg * gain

    kick, snare, clap, hat_c, hat_o = sy.kick(), sy.snare(), sy.clap(), sy.hat(False), sy.hat(True)
    for b in range(bars):
        t0, ci = b * bar, b % 4
        if pad:
            put(p_bus, _chord(tuple(48 + k + iv for iv in mode["chords"][ci]), round(bar, 3), s["attack"], 0.3), t0)
            if s["stab"]:
                stab = _chord(tuple(60 + k + iv for iv in mode["chords"][ci]), 0.2, 0.003, 0.12)
                for st in s["stab"]:
                    put(s_bus, stab, t0 + st * stp, 0.5)
        if bass:
            f = _hz(36 + k + mode["roots"][ci])
            for st, ln in s["bass"]:
                put(b_bus, _bass(f, max(0.05, ln * stp * 0.95)), t0 + st * stp)
        if drums:
            for st in s["kick"]:
                put(d_bus, kick, t0 + st * stp, 1.0)
            for st in s["snare"]:
                put(d_bus, snare, t0 + st * stp, 0.8)
            for st in s["clap"]:
                put(d_bus, clap, t0 + st * stp, 0.7)
            for j, st in enumerate(s["ch"]):
                put(d_bus, hat_c, t0 + st * stp, 0.35 if j % 2 == 0 else 0.22)
            for st in s["oh"]:
                put(d_bus, hat_o, t0 + st * stp, 0.35)

    if s["pump"] > 0:  # effet « side-chain » synchronisé sur le tempo
        beat = ((np.arange(n) / SR) % spb) / spb
        g = (1 - s["pump"] * (1 - beat) ** 3).astype(np.float32)
        p_bus *= g
        b_bus *= g

    out = d_bus * 0.9 + b_bus * 0.7 + p_bus * 0.30 + s_bus * 0.30
    return normalize(out[:, : int(seconds * SR)], -3.0)


def render(style: str, bpm: int, key: str, seconds: float,
           drums: bool = True, bass: bool = True, pad: bool = True) -> np.ndarray:
    return _render(style, int(bpm), key, round(float(seconds), 1), bool(drums), bool(bass), bool(pad)).copy()
