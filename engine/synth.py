"""Briques de synthèse : filtres, bruit, tons band-limited et percussions."""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfilt

from engine.audio import SR

_rng = np.random.default_rng(11)


def t_axis(d: float) -> np.ndarray:
    return np.arange(int(SR * d)) / SR


def noise(n: int) -> np.ndarray:
    return _rng.standard_normal(n)


def lp(x, hz, order=2):
    return sosfilt(butter(order, hz, "low", fs=SR, output="sos"), x)


def hp(x, hz, order=2):
    return sosfilt(butter(order, hz, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def stereo(x: np.ndarray) -> np.ndarray:
    return np.vstack([x, x]).astype(np.float32)


def band_saw(freq: float, t: np.ndarray, max_hz: float = 3000.0, kmax: int = 24) -> np.ndarray:
    """Dent de scie à bande limitée (somme d'harmoniques) : pas d'aliasing."""
    top = max(1, min(kmax, int(max_hz / max(freq, 1.0))))
    ph = 2 * np.pi * freq * t
    return sum(np.sin(k * ph) / k for k in range(1, top + 1))


# ---- percussions ----
def kick(dur: float = 0.45) -> np.ndarray:
    t = t_axis(dur)
    f = 45 + 120 * np.exp(-t * 38)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
    click = noise(t.size) * np.exp(-t * 250) * 0.25
    return (np.tanh(1.6 * (body + click)) * 0.9).astype(np.float32)


def snare(dur: float = 0.28) -> np.ndarray:
    t = t_axis(dur)
    n = hp(noise(t.size), 1500) * np.exp(-t * 20)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 28) * 0.6
    return (np.tanh(1.4 * (0.8 * n + tone)) * 0.8).astype(np.float32)


def clap(dur: float = 0.3) -> np.ndarray:
    t = t_axis(dur)
    n = bp(noise(t.size), 1000, 3500)
    env = np.zeros_like(t)
    for o in (0.0, 0.011, 0.023):
        env += np.where(t >= o, np.exp(-(t - o) * 220), 0.0) * 0.6
    env += np.where(t >= 0.03, np.exp(-(t - 0.03) * 16), 0.0)
    return (n * env * 0.9).astype(np.float32)


def hat(open_: bool = False) -> np.ndarray:
    t = t_axis(0.35 if open_ else 0.09)
    return (hp(noise(t.size), 7000) * np.exp(-t * (12 if open_ else 70)) * 0.5).astype(np.float32)
