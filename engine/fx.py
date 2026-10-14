"""Chaîne d'effets voix (Pedalboard, Spotify) : réglages, de-esser et presets « studio »."""
from __future__ import annotations

import numpy as np
from pedalboard import (Bitcrush, Chorus, Compressor, Delay, Distortion, Gain,
                        HighpassFilter, HighShelfFilter, Limiter, LowpassFilter,
                        LowShelfFilter, NoiseGate, Pedalboard, PeakFilter,
                        PitchShift, Reverb)
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt

from engine import audio

DEFAULTS = {
    "gain_db": 0.0, "gate_db": -80.0,
    "hp_hz": 20, "lp_hz": 20000,
    "low_db": 0.0, "mud_db": 0.0, "mid_db": 0.0, "high_db": 0.0,
    "deess": 0.0, "pitch_st": 0.0,
    "comp_thr": 0.0, "comp_ratio": 3.0,
    "drive_db": 0.0, "crush_bits": 16, "chorus_mix": 0.0,
    "echo_mix": 0.0, "echo_ms": 350, "echo_fb": 0.35,
    "reverb_wet": 0.0, "reverb_room": 0.4,
    "limiter": True,
}

PRESETS = {
    "Naturel": {},
    "Studio Pro — voix off": {"gate_db": -60.0, "hp_hz": 80, "mud_db": -2.5, "low_db": 2.5, "mid_db": 2.5,
                              "high_db": 3.0, "deess": 0.5, "comp_thr": -20.0, "comp_ratio": 3.0,
                              "drive_db": 2.0, "reverb_wet": 0.05, "reverb_room": 0.15},
    "Voix off événement / Trailer": {"hp_hz": 70, "mud_db": -3.0, "low_db": 4.0, "mid_db": 3.0, "high_db": 3.0,
                                     "deess": 0.6, "comp_thr": -22.0, "comp_ratio": 4.0, "drive_db": 3.0,
                                     "pitch_st": -1.0, "reverb_wet": 0.16, "reverb_room": 0.55,
                                     "echo_mix": 0.08, "echo_ms": 420, "echo_fb": 0.25},
    "Annonceur radio FM": {"hp_hz": 110, "mud_db": -2.0, "low_db": 3.0, "mid_db": 3.5, "high_db": 3.5,
                           "deess": 0.6, "comp_thr": -24.0, "comp_ratio": 5.0, "drive_db": 2.5,
                           "reverb_wet": 0.06, "gain_db": 1.0},
    "DJ Club Drop": {"hp_hz": 100, "mud_db": -2.0, "low_db": 2.0, "mid_db": 2.5, "high_db": 3.5, "deess": 0.4,
                     "comp_thr": -20.0, "comp_ratio": 4.0, "drive_db": 2.5, "echo_mix": 0.28, "echo_ms": 375,
                     "echo_fb": 0.42, "reverb_wet": 0.22, "reverb_room": 0.5, "gain_db": 1.0},
    "Stade / Arena": {"hp_hz": 150, "mud_db": -2.0, "mid_db": 3.0, "high_db": 2.0, "deess": 0.4,
                      "comp_thr": -20.0, "comp_ratio": 4.0, "echo_mix": 0.3, "echo_ms": 220, "echo_fb": 0.3,
                      "reverb_wet": 0.3, "reverb_room": 0.8},
    "Voix de fond — nappe": {"hp_hz": 220, "lp_hz": 5500, "mid_db": -2.0, "comp_thr": -22.0, "comp_ratio": 3.0,
                             "reverb_wet": 0.5, "reverb_room": 0.85, "echo_mix": 0.35, "echo_ms": 450,
                             "echo_fb": 0.45},
    "Chuchotement fantôme": {"hp_hz": 300, "lp_hz": 7000, "pitch_st": -2.0, "chorus_mix": 0.35,
                             "reverb_wet": 0.55, "reverb_room": 0.9, "echo_mix": 0.3, "echo_ms": 380,
                             "echo_fb": 0.5},
    "Nettoyage voix": {"gate_db": -55.0, "hp_hz": 90, "comp_thr": -18.0, "high_db": 2.0, "deess": 0.3},
    "Mégaphone": {"hp_hz": 500, "lp_hz": 4000, "drive_db": 12.0, "comp_thr": -24.0, "comp_ratio": 6.0,
                  "mid_db": 4.0, "gain_db": -1.0},
    "Téléphone": {"hp_hz": 400, "lp_hz": 3500, "crush_bits": 10, "comp_thr": -20.0},
    "Robot": {"pitch_st": -2.0, "crush_bits": 8, "chorus_mix": 0.5, "echo_mix": 0.5, "echo_ms": 25,
              "echo_fb": 0.6},
    "Voix grave cinéma": {"pitch_st": -3.0, "hp_hz": 60, "low_db": 4.0, "comp_thr": -20.0,
                          "reverb_wet": 0.18, "reverb_room": 0.6},
    "Voix aiguë fun": {"pitch_st": 4.0, "high_db": 2.0, "chorus_mix": 0.2},
    "Grotte": {"lp_hz": 9000, "reverb_wet": 0.45, "reverb_room": 0.95, "echo_mix": 0.3, "echo_ms": 500,
               "echo_fb": 0.5},
}


def deess(a: np.ndarray, amount: float) -> np.ndarray:
    """De-esser dynamique : atténue les sifflantes (5–9,5 kHz) quand elles dépassent un seuil."""
    if amount <= 0:
        return a
    sos = butter(4, [5000, 9500], btype="band", fs=audio.SR, output="sos")
    band = sosfilt(sos, a, axis=1)
    env = uniform_filter1d(np.abs(band).max(axis=0), size=int(0.004 * audio.SR))
    thr, ratio = 0.03, 1 + 6 * amount
    g = np.where(env > thr, (thr / np.maximum(env, 1e-9)) ** (1 - 1 / ratio), 1.0)
    g = uniform_filter1d(g, size=int(0.003 * audio.SR))
    return (a - band * (1 - g)).astype(np.float32)


def build_board(params: dict) -> Pedalboard:
    q = {**DEFAULTS, **params}
    p = []
    if q["gate_db"] > -79:
        p.append(NoiseGate(threshold_db=q["gate_db"], ratio=4.0, attack_ms=2.0, release_ms=150.0))
    if q["hp_hz"] > 25:
        p.append(HighpassFilter(float(q["hp_hz"])))
    if q["lp_hz"] < 19000:
        p.append(LowpassFilter(float(q["lp_hz"])))
    if q["low_db"]:
        p.append(LowShelfFilter(150.0, float(q["low_db"])))        # chaleur / proximité
    if q["mud_db"]:
        p.append(PeakFilter(320.0, float(q["mud_db"]), 1.0))       # « boue »
    if q["mid_db"]:
        p.append(PeakFilter(3500.0, float(q["mid_db"]), 0.9))      # présence
    if q["high_db"]:
        p.append(HighShelfFilter(9000.0, float(q["high_db"])))     # air
    if q["pitch_st"]:
        p.append(PitchShift(float(q["pitch_st"])))
    if q["comp_thr"] < 0:
        p.append(Compressor(threshold_db=q["comp_thr"], ratio=q["comp_ratio"], attack_ms=5.0, release_ms=120.0))
    if q["drive_db"] > 0:
        p.append(Distortion(float(q["drive_db"])))
    if q["crush_bits"] < 16:
        p.append(Bitcrush(float(q["crush_bits"])))
    if q["chorus_mix"] > 0:
        p.append(Chorus(rate_hz=1.2, depth=0.3, centre_delay_ms=7.0, feedback=0.0, mix=float(q["chorus_mix"])))
    if q["echo_mix"] > 0:
        p.append(Delay(delay_seconds=q["echo_ms"] / 1000, feedback=float(q["echo_fb"]), mix=float(q["echo_mix"])))
    if q["reverb_wet"] > 0:
        w = float(q["reverb_wet"])
        p.append(Reverb(room_size=float(q["reverb_room"]), damping=0.5, wet_level=w,
                        dry_level=max(0.4, 1.0 - w), width=1.0))
    if q["gain_db"]:
        p.append(Gain(float(q["gain_db"])))
    if q["limiter"]:
        p.append(Limiter(threshold_db=-1.0))
    return Pedalboard(p)


def process(a: np.ndarray, params: dict) -> np.ndarray:
    """Applique la chaîne, en laissant la queue d'écho/reverb se terminer."""
    q = {**DEFAULTS, **params}
    a = deess(a, q["deess"])
    tail = 0.0
    if q["echo_mix"] > 0:
        tail += min(4.0, q["echo_ms"] / 1000 * (2 + 8 * q["echo_fb"]))
    if q["reverb_wet"] > 0:
        tail += 0.8 + 3 * q["reverb_room"]
    padded = np.hstack([a, audio.silence(tail)]) if tail else a
    out = build_board(q)(np.ascontiguousarray(padded, dtype=np.float32), audio.SR)
    return audio.trim_silence(out, trim_start=False, thr_db=-60.0, pad_s=0.1)
