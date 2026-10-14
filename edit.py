"""Montage : couper, supprimer une partie, garder une partie, supprimer les silences."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter1d

from engine.audio import SR, db_to_lin, fade


def cut_out(a: np.ndarray, t0: float, t1: float, xfade_ms: float = 12.0) -> np.ndarray:
    """Supprime la zone [t0, t1] (secondes) et raccorde les deux côtés par un fondu enchaîné."""
    n = a.shape[1]
    i0, i1 = max(0, int(t0 * SR)), min(n, int(t1 * SR))
    if i1 <= i0:
        return a
    left, right = a[:, :i0], a[:, i1:]
    if left.shape[1] == 0:
        return right
    if right.shape[1] == 0:
        return left
    xf = min(int(xfade_ms * SR / 1000), left.shape[1], right.shape[1])
    if xf < 2:
        return np.hstack([left, right])
    ramp = np.linspace(0, 1, xf, dtype=np.float32)
    mid = left[:, -xf:] * (1 - ramp) + right[:, :xf] * ramp
    return np.hstack([left[:, :-xf], mid, right[xf:] if right.ndim == 1 else right[:, xf:]])


def keep(a: np.ndarray, t0: float, t1: float) -> np.ndarray:
    """Ne garde que la zone [t0, t1] (équivaut à couper le début et la fin)."""
    i0, i1 = max(0, int(t0 * SR)), min(a.shape[1], int(t1 * SR))
    if i1 - i0 < 2:
        return a
    return fade(a[:, i0:i1], 0.005, 0.005)


def remove_silences(a: np.ndarray, thr_db: float = -45.0, min_s: float = 0.8, keep_s: float = 0.25) -> np.ndarray:
    """Raccourcit chaque silence plus long que min_s à keep_s."""
    env = uniform_filter1d(np.abs(a).max(axis=0), size=max(1, int(0.010 * SR)))
    silent = np.concatenate([[False], env < db_to_lin(thr_db), [False]])
    edges = np.diff(silent.astype(np.int8))
    starts, ends = np.where(edges == 1)[0], np.where(edges == -1)[0]
    cuts = []
    for s, e in zip(starts, ends):
        if (e - s) / SR >= min_s:
            half = keep_s / 2
            cuts.append((s / SR + half, e / SR - half))
    for t0, t1 in reversed(cuts):            # de la fin vers le début : les indices restent valides
        a = cut_out(a, t0, t1)
    return a


def apply_ops(a: np.ndarray, ops) -> np.ndarray:
    """ops : [("cut", t0, t1) | ("keep", t0, t1) | ("silences", seuil_db, durée_min_s)]"""
    for op in ops:
        if op[0] == "cut":
            a = cut_out(a, op[1], op[2])
        elif op[0] == "keep":
            a = keep(a, op[1], op[2])
        elif op[0] == "silences":
            a = remove_silences(a, op[1], op[2])
    return a
