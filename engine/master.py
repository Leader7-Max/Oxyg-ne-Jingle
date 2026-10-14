"""Mastering : loudness (LUFS), compression de bus, brillance, limiteur."""
from __future__ import annotations

import numpy as np
from pedalboard import Compressor, HighShelfFilter, Limiter, Pedalboard

from engine.audio import SR, db_to_lin

try:  # mesure LUFS conforme ITU-R BS.1770 si disponible
    import pyloudnorm as pyln
except Exception:  # noqa: BLE001
    pyln = None


def lufs(a: np.ndarray) -> float:
    if pyln is not None:
        try:
            v = float(pyln.Meter(SR).integrated_loudness(a.T.astype(np.float64)))
            if np.isfinite(v):
                return v
        except Exception:  # noqa: BLE001
            pass
    return float(20 * np.log10(np.sqrt(np.mean(a**2)) + 1e-9) - 0.7)  # estimation de secours


def peak_db(a: np.ndarray) -> float:
    return float(20 * np.log10(np.abs(a).max() + 1e-9))


def measure(a: np.ndarray) -> dict:
    return {"lufs": lufs(a), "peak": peak_db(a)}


def _limit(x: np.ndarray, ceiling_db: float) -> np.ndarray:
    return Pedalboard([Limiter(threshold_db=ceiling_db, release_ms=80.0)])(
        np.ascontiguousarray(x, dtype=np.float32), SR)


def master(a: np.ndarray, target_lufs: float = -14.0, ceiling_db: float = -1.0,
           glue: bool = True, air: bool = True) -> np.ndarray:
    chain = []
    if glue:
        chain.append(Compressor(threshold_db=-16.0, ratio=2.0, attack_ms=25.0, release_ms=200.0))
    if air:
        chain.append(HighShelfFilter(10000.0, 1.5))
    x = Pedalboard(chain)(np.ascontiguousarray(a, dtype=np.float32), SR) if chain else a
    x = _limit(x, ceiling_db)
    for _ in range(2):  # 2 passes : le limiteur « mange » un peu de loudness
        gain = float(np.clip(target_lufs - lufs(x), -18.0, 18.0))
        if abs(gain) < 0.3:
            break
        x = _limit(x * db_to_lin(gain), ceiling_db)
    return x
