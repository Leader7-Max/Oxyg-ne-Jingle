"""Utilitaires audio : décodage, rééchantillonnage, fondus, mixage, export."""
from __future__ import annotations

import io
import os
import tempfile
from math import gcd

import numpy as np
from pedalboard.io import AudioFile
from scipy.signal import resample_poly

SR = 44100  # fréquence de travail unique


def db_to_lin(db: float) -> float:
    return float(10 ** (db / 20))


def to_stereo(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    if a.ndim == 1:
        a = a[None, :]
    if a.shape[0] == 1:
        a = np.vstack([a, a])
    return np.ascontiguousarray(a[:2])


def resample(a: np.ndarray, sr_in: int, sr_out: int = SR) -> np.ndarray:
    if sr_in == sr_out:
        return a.astype(np.float32)
    g = gcd(int(sr_in), int(sr_out))
    return resample_poly(a, sr_out // g, sr_in // g, axis=1).astype(np.float32)


def decode(data: bytes) -> np.ndarray:
    """bytes (wav/mp3/flac/ogg) -> float32 stéréo (2, n) à 44,1 kHz."""
    with AudioFile(io.BytesIO(data)) as f:
        sr = int(f.samplerate)
        a = f.read(f.frames)
    return to_stereo(resample(a, sr))


def silence(seconds: float) -> np.ndarray:
    return np.zeros((2, max(0, int(seconds * SR))), dtype=np.float32)


def concat(parts: list[np.ndarray]) -> np.ndarray:
    parts = [p for p in parts if p.shape[1] > 0]
    return np.hstack(parts) if parts else silence(0.1)


def normalize(a: np.ndarray, peak_db: float = -1.0) -> np.ndarray:
    peak = float(np.max(np.abs(a))) if a.size else 0.0
    if peak < 1e-9:
        return a
    return (a * (db_to_lin(peak_db) / peak)).astype(np.float32)


def fade(a: np.ndarray, fade_in_s: float = 0.0, fade_out_s: float = 0.0) -> np.ndarray:
    a = a.copy()
    n = a.shape[1]
    fi, fo = min(int(fade_in_s * SR), n), min(int(fade_out_s * SR), n)
    if fi > 0:
        a[:, :fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    if fo > 0:
        a[:, n - fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    return a


def mix(base: np.ndarray, layer: np.ndarray, start_s: float = 0.0) -> np.ndarray:
    start = max(0, int(start_s * SR))
    n = max(base.shape[1], start + layer.shape[1])
    out = np.zeros((2, n), dtype=np.float32)
    out[:, : base.shape[1]] += base
    out[:, start : start + layer.shape[1]] += layer
    return out


def trim_silence(a: np.ndarray, thr_db: float = -55.0, pad_s: float = 0.08,
                 trim_start: bool = True) -> np.ndarray:
    idx = np.where(np.abs(a).max(axis=0) > db_to_lin(thr_db))[0]
    if idx.size == 0:
        return a
    pad = int(pad_s * SR)
    s = max(0, idx[0] - pad) if trim_start else 0
    e = min(a.shape[1], idx[-1] + pad)
    return a[:, s:e]


def duration(a: np.ndarray) -> float:
    return a.shape[1] / SR


def peaks(a: np.ndarray, bins: int = 240) -> list[float]:
    """Enveloppe (0-1) pour dessiner la forme d'onde."""
    m = np.abs(a).max(axis=0)
    hop = max(1, m.size // bins)
    m = np.pad(m, (0, max(0, hop * bins - m.size)))[: hop * bins]
    p = m.reshape(bins, hop).max(axis=1)
    return (p / (p.max() + 1e-9)).round(3).tolist()


def export(a: np.ndarray, fmt: str = "wav", bit_depth: int = 24) -> bytes:
    """Exporte en bytes : 'wav' (16/24 bits) ou 'mp3' (haute qualité)."""
    a = np.ascontiguousarray(np.clip(a, -1.0, 1.0), dtype=np.float32)
    if fmt == "mp3":
        options = [{"quality": "320k"}, {"quality": "192k"}, {}]
    else:
        options = [{"bit_depth": int(bit_depth)}, {}]
    last_err: Exception | None = None
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, f"out.{fmt}")
        for opt in options:
            try:
                with AudioFile(path, "w", SR, 2, **opt) as f:
                    f.write(a)
                with open(path, "rb") as fh:
                    return fh.read()
            except Exception as e:  # noqa: BLE001
                last_err = e
    raise RuntimeError(f"Export {fmt} impossible : {last_err}")
