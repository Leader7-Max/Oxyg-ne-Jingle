"""Effets sonores DJ générés par synthèse (aucun fichier externe, aucun droit)."""
from __future__ import annotations

import numpy as np

from engine import audio

SR = audio.SR
_rng = np.random.default_rng(7)


def _st(x: np.ndarray) -> np.ndarray:
    return audio.normalize(np.vstack([x, x]).astype(np.float32), -3.0)


def impact() -> np.ndarray:
    t = np.linspace(0, 1.8, int(SR * 1.8), endpoint=False)
    f = 35 + 110 * np.exp(-t * 3)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    hit = _rng.standard_normal(t.size) * np.exp(-t * 25) * 0.4
    return _st(boom + hit)


def riser() -> np.ndarray:
    n = int(SR * 3.0)
    t = np.linspace(0, 1, n)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 5000 * t**2) / SR)
    noise = np.convolve(_rng.standard_normal(n), np.ones(4) / 4, "same")
    return _st((0.6 * tone + 0.4 * noise) * t**1.5)


def whoosh() -> np.ndarray:
    n = int(SR * 1.2)
    t = np.linspace(0, 1, n)
    noise = np.convolve(_rng.standard_normal(n), np.ones(10) / 10, "same")
    return _st(noise * np.sin(np.pi * t) ** 2)


def laser() -> np.ndarray:
    t = np.linspace(0, 0.6, int(SR * 0.6), endpoint=False)
    f = 300 + 3000 * np.exp(-t * 12)
    return _st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5))


def beeps() -> np.ndarray:
    def beep(d):
        t = np.linspace(0, d, int(SR * d), endpoint=False)
        return np.sin(2 * np.pi * 1000 * t) * np.minimum(1, np.minimum(t, d - t) * 200)
    gap = np.zeros(int(SR * 0.12))
    return _st(np.concatenate([beep(0.18), gap, beep(0.18)]))


EFFECTS = {
    "💥 Impact": impact,
    "📈 Riser": riser,
    "🌬️ Whoosh": whoosh,
    "🔫 Laser": laser,
    "📻 Bips radio": beeps,
}


def get(label: str):
    fn = EFFECTS.get(label)
    return fn() if fn else None
