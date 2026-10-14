"""Assemblage du projet : pistes de voix (timeline), nappe avec ducking, effets DJ placés."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d

from engine.audio import SR, db_to_lin, fade, mix


def _fit(a: np.ndarray, total: int, loop: bool) -> np.ndarray:
    if a.shape[1] < total:
        if loop:
            a = np.tile(a, (1, int(np.ceil(total / a.shape[1]))))
        else:
            a = np.hstack([a, np.zeros((2, total - a.shape[1]), np.float32)])
    return a[:, :total].copy()


def _pad(a: np.ndarray, n: int) -> np.ndarray:
    return a if a.shape[1] >= n else np.hstack([a, np.zeros((2, n - a.shape[1]), np.float32)])


def duck_curve(voice_track: np.ndarray, duck_db: float) -> np.ndarray:
    """Gain (0-1) de la musique : baisse quand la voix parle, remonte dans les silences."""
    active = (np.abs(voice_track).max(axis=0) > 0.01).astype(np.float32)
    held = maximum_filter1d(active, size=int(0.30 * SR))
    smooth = uniform_filter1d(held, size=int(0.20 * SR))
    return (1.0 - (1.0 - db_to_lin(duck_db)) * smooth).astype(np.float32)


def build_project(tracks, music=None, music_db=-8.0, duck_db=-10.0, loop=True,
                  sfx_events=(), lead_in=1.5, tail=1.5, fade_out=1.0):
    """tracks : [{name, audio, place, offset, bg}] — sfx_events : [{audio, mode, t, db}]
    music : tableau audio, fonction secondes -> audio, ou None. Retourne (mix, stems)."""
    lead = lead_in
    for e in sfx_events:
        if e["mode"] == "Avant la voix":
            lead = max(lead, e["audio"].shape[1] / SR)

    placed, cursor = [], lead
    for tr in tracks:
        dur = tr["audio"].shape[1] / SR
        after = tr.get("place") == "Après la précédente" and not tr.get("bg") and placed
        start = (cursor if after else lead) + tr.get("offset", 0.0)
        placed.append((tr, start))
        if not tr.get("bg"):
            cursor = max(cursor, start + dur)
    voice_end = max(s + tr["audio"].shape[1] / SR for tr, s in placed)
    N = int((voice_end + tail) * SR)

    sfx_bus = np.zeros((2, N), np.float32)
    for e in sfx_events:
        d = e["audio"].shape[1] / SR
        start = {"Au début": 0.0, "Avant la voix": max(0.0, lead - d),
                 "Après la voix": voice_end, "À t secondes": e.get("t", 0.0)}[e["mode"]]
        sfx_bus = mix(sfx_bus, e["audio"] * db_to_lin(e["db"]), start)
    M = max(N, sfx_bus.shape[1])
    sfx_bus = _pad(sfx_bus, M)

    stems, voices, duck_src = {}, np.zeros((2, M), np.float32), np.zeros((2, M), np.float32)
    for tr, s in placed:
        layer, i = np.zeros((2, M), np.float32), int(s * SR)
        seg = tr["audio"][:, : M - i]
        layer[:, i : i + seg.shape[1]] = seg
        stems[tr["name"]] = layer
        voices += layer
        if not tr.get("bg"):
            duck_src += layer

    mus = np.zeros((2, M), np.float32)
    if music is not None:
        m = music(M / SR + 0.5) if callable(music) else music
        m = _fit(m, M, loop) * db_to_lin(music_db)
        mus = fade(m * duck_curve(duck_src, duck_db), 0.3, fade_out)
    stems["musique"], stems["effets"] = mus, sfx_bus

    final = fade(voices + mus + sfx_bus, 0.005, 0.08)
    return final, stems
