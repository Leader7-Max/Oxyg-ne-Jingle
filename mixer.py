"""Assemblage du jingle : voix + nappe musicale (ducking) + effets d'intro/outro."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d

from engine.audio import SR, db_to_lin, fade, mix, normalize


def _fit(a: np.ndarray, total: int, loop: bool) -> np.ndarray:
    if a.shape[1] < total:
        if loop:
            a = np.tile(a, (1, int(np.ceil(total / a.shape[1]))))
        else:
            a = np.hstack([a, np.zeros((2, total - a.shape[1]), np.float32)])
    return a[:, :total].copy()


def duck_curve(voice_track: np.ndarray, duck_db: float) -> np.ndarray:
    """Gain (0-1) à appliquer à la musique : baisse quand la voix parle."""
    active = (np.abs(voice_track).max(axis=0) > 0.01).astype(np.float32)
    held = maximum_filter1d(active, size=int(0.30 * SR))   # comble les petits silences
    smooth = uniform_filter1d(held, size=int(0.20 * SR))   # attaque/relâchement doux
    return (1.0 - (1.0 - db_to_lin(duck_db)) * smooth).astype(np.float32)


def build_jingle(voice, music=None, music_db=-8.0, duck_db=-12.0, loop=True,
                 intro=None, outro=None, sfx_db=-4.0,
                 lead_in=1.0, tail=1.0, fade_out=0.8) -> np.ndarray:
    lead, n_voice = int(lead_in * SR), voice.shape[1]
    total = lead + n_voice + int(tail * SR)

    out = np.zeros((2, total), np.float32)
    out[:, lead : lead + n_voice] = voice

    if music is not None:
        m = _fit(music, total, loop) * db_to_lin(music_db)
        m = m * duck_curve(out, duck_db)
        out = out + fade(m, 0.3, fade_out)

    if intro is not None:
        out = mix(out, intro * db_to_lin(sfx_db), 0.0)
    if outro is not None:
        out = mix(out, outro * db_to_lin(sfx_db), max(0.0, (lead + n_voice) / SR - 0.3))

    return normalize(fade(out, 0.005, 0.05), -1.0)
