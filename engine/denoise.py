"""Anti-bruit pour prises de voix : réduction spectrale (souffle, ventilateur…) + filtre anti-ronflement."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter
from scipy.signal import filtfilt, iirnotch, istft, stft

from engine.audio import SR

NPERSEG, HOP = 2048, 512


def remove_hum(a: np.ndarray, base_hz: float = 50.0, harmonics: int = 5, q: float = 30.0) -> np.ndarray:
    """Filtres coupe-bande sur le ronflement secteur (50/60 Hz) et ses harmoniques."""
    x = a.astype(np.float64)
    for k in range(1, harmonics + 1):
        f = base_hz * k
        if f >= SR / 2 - 100:
            break
        b, aa = iirnotch(f, q, fs=SR)
        x = filtfilt(b, aa, x, axis=1)
    return x.astype(np.float32)


def _denoise_channel(x: np.ndarray, strength: float, noise_s: float | None) -> np.ndarray:
    f, t, Z = stft(x, fs=SR, nperseg=NPERSEG, noverlap=NPERSEG - HOP, window="hann")
    mag = np.abs(Z)
    frames = None
    if noise_s:
        idx = np.where(t < noise_s)[0]
        frames = idx if idx.size >= 3 else None
    if frames is None:  # profil automatique : moyenne des 12 % de trames les plus calmes
        k = max(3, int(0.12 * mag.shape[1]))
        frames = np.argsort(mag.sum(axis=0))[:k]
    noise = mag[:, frames].mean(axis=1, keepdims=True)
    alpha = 1.0 + 2.0 * strength                      # sur-soustraction
    floor = 0.02 + 0.30 * (1.0 - strength)            # plancher spectral (limite les artefacts)
    mask = np.maximum(mag - alpha * noise, floor * mag) / (mag + 1e-9)
    mask = uniform_filter(mask, size=(3, 3))          # lisse le masque -> moins de « bruit musical »
    _, y = istft(Z * mask, fs=SR, nperseg=NPERSEG, noverlap=NPERSEG - HOP, window="hann")
    out = np.zeros_like(x)
    n = min(x.size, y.size)
    out[:n] = y[:n]
    return out


def denoise(a: np.ndarray, strength: float = 0.6, noise_s: float | None = None) -> np.ndarray:
    """strength 0..1 ; noise_s = durée (s) du début qui ne contient que du bruit (sinon : automatique)."""
    strength = float(np.clip(strength, 0.0, 1.0))
    if strength <= 0 or a.shape[1] < NPERSEG * 2:
        return a
    if np.allclose(a[0], a[1], atol=1e-6):            # voix mono : un seul calcul
        ch = _denoise_channel(a[0].astype(np.float64), strength, noise_s)
        return np.vstack([ch, ch]).astype(np.float32)
    return np.vstack([_denoise_channel(c.astype(np.float64), strength, noise_s) for c in a]).astype(np.float32)
