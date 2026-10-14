"""Assemblage du projet : voix superposables sur une timeline, nappe avec ducking,
effets DJ placés, écho de début / de fin de jingle."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d

from engine import fx
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


def _echo(voices: np.ndarray, t0: float, t1: float, cfg: dict):
    """Écho (répétitions seules) appliqué à la zone [t0, t1] du bus voix. Retourne (wet, début_s)."""
    i0, i1 = max(0, int(t0 * SR)), min(voices.shape[1], int(t1 * SR))
    if i1 - i0 < int(0.05 * SR):
        return None
    seg = fade(voices[:, i0:i1].copy(), 0.015, 0.015)
    wet = fx.echo_wet(seg, cfg["ms"], cfg["fb"], cfg.get("tone", 5000.0), cfg.get("pp", True))
    return wet * db_to_lin(cfg["db"]), i0 / SR


def build_project(tracks, music=None, music_db=-8.0, duck_db=-10.0, loop=True, sfx_events=(),
                  lead_in=1.5, tail=1.5, fade_out=1.0, echo_in=None, echo_out=None):
    """tracks : [{name, label, audio, place, offset, bg}] — sfx_events : [{label, audio, mode, t, db}]
    echo_in / echo_out : None ou {dur, ms, fb, db, tone, pp}
    music : tableau audio, fonction secondes -> audio, ou None.  Retourne (mix, stems, layout)."""
    lead = lead_in
    for e in sfx_events:
        if e["mode"] == "Avant la voix":
            lead = max(lead, e["audio"].shape[1] / SR)

    placed, cursor = [], lead
    for tr in tracks:
        dur = tr["audio"].shape[1] / SR
        after = tr.get("place") == "Après la précédente" and placed
        start = (cursor if after else lead) + tr.get("offset", 0.0)
        placed.append((tr, start))
        if not tr.get("bg"):
            cursor = max(cursor, start + dur)
    first_start = min(s for _, s in placed)
    voice_end = max(s + tr["audio"].shape[1] / SR for tr, s in placed)
    N = int((voice_end + tail) * SR)

    layout = []
    sfx_bus = np.zeros((2, N), np.float32)
    for e in sfx_events:
        d = e["audio"].shape[1] / SR
        start = {"Au début": 0.0, "Avant la voix": max(0.0, lead - d),
                 "Après la voix": voice_end, "À t secondes": e.get("t", 0.0)}[e["mode"]]
        sfx_bus = mix(sfx_bus, e["audio"] * db_to_lin(e["db"]), start)
        layout.append((e.get("label", "Effet"), start, start + d, "sfx"))
    M = max(N, sfx_bus.shape[1])

    stems, voices, duck_src = {}, np.zeros((2, M), np.float32), np.zeros((2, M), np.float32)
    for tr, s in placed:
        layer, i = np.zeros((2, M), np.float32), int(s * SR)
        seg = tr["audio"][:, : M - i]
        layer[:, i : i + seg.shape[1]] = seg
        stems[tr["name"]] = layer
        voices += layer
        if not tr.get("bg"):
            duck_src += layer
        layout.append((tr.get("label", tr["name"]), s, s + tr["audio"].shape[1] / SR,
                       "bg" if tr.get("bg") else "voice"))

    echo_bus = np.zeros((2, M), np.float32)
    jobs = []
    if echo_in:
        jobs.append(("Écho début", first_start, min(first_start + echo_in["dur"], voice_end), echo_in))
    if echo_out:
        jobs.append(("Écho fin", max(first_start, voice_end - echo_out["dur"]), voice_end, echo_out))
    for label, t0, t1, cfg in jobs:
        res = _echo(voices, t0, t1, cfg)
        if res is None:
            continue
        wet, start = res
        echo_bus = mix(echo_bus, wet, start)
        layout.append((label, start, start + wet.shape[1] / SR, "echo"))

    M2 = max(M, echo_bus.shape[1])
    voices, sfx_bus, echo_bus, duck_src = (_pad(x, M2) for x in (voices, sfx_bus, echo_bus, duck_src))
    stems = {k: _pad(v, M2) for k, v in stems.items()}

    mus = np.zeros((2, M2), np.float32)
    if music is not None:
        m = music(M2 / SR + 0.5) if callable(music) else music
        m = _fit(m, M2, loop) * db_to_lin(music_db)
        mus = fade(m * duck_curve(duck_src, duck_db), 0.3, fade_out)
        layout.append(("Musique", 0.0, M2 / SR, "music"))
    stems["echos"], stems["musique"], stems["effets"] = echo_bus, mus, sfx_bus

    final = fade(voices + echo_bus + mus + sfx_bus, 0.005, 0.08)
    return final, stems, layout
