"""Chaîne d'effets voix (Pedalboard, Spotify) : réglages, de-esser, modulations et presets."""
from __future__ import annotations

import numpy as np
from pedalboard import (Bitcrush, Chorus, Compressor, Delay, Distortion, Gain,
                        HighpassFilter, HighShelfFilter, Limiter, LowpassFilter,
                        LowShelfFilter, NoiseGate, Pedalboard, PeakFilter,
                        Phaser, PitchShift, Reverb)
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt

from engine import audio
from engine import synth as sy

DEFAULTS = {
    "gain_db": 0.0, "gate_db": -80.0,
    "hp_hz": 20, "lp_hz": 20000,
    "low_db": 0.0, "mud_db": 0.0, "mid_db": 0.0, "high_db": 0.0,
    "deess": 0.0, "pitch_st": 0.0,
    "comp_thr": 0.0, "comp_ratio": 3.0,
    "drive_db": 0.0, "crush_bits": 16,
    "chorus_mix": 0.0, "phaser_mix": 0.0, "flanger_mix": 0.0,
    "trem_depth": 0.0, "trem_hz": 5.0, "ring_mix": 0.0, "ring_hz": 60,
    "echo_mix": 0.0, "echo_ms": 350, "echo_fb": 0.35, "echo_pp": False,
    "reverb_wet": 0.0, "reverb_room": 0.4,
    "width": 1.0, "reverse": False, "limiter": True,
}

PRESETS = {
    "Naturel": {},
    "Voix grasse": {"hp_hz": 60, "low_db": 6.0, "mid_db": 2.0, "high_db": 1.0, "pitch_st": -2.0, "deess": 0.4,
                    "comp_thr": -22.0, "comp_ratio": 4.0, "drive_db": 4.0, "reverb_wet": 0.08, "reverb_room": 0.3},
    "Voix agressive": {"hp_hz": 120, "low_db": 2.0, "mud_db": -2.0, "mid_db": 5.0, "high_db": 3.0, "pitch_st": -1.0,
                       "deess": 0.3, "comp_thr": -26.0, "comp_ratio": 6.0, "drive_db": 9.0, "reverb_wet": 0.1,
                       "reverb_room": 0.25, "echo_mix": 0.12, "echo_ms": 120, "echo_fb": 0.3},
    "Hype Hip-Hop": {"hp_hz": 90, "low_db": 3.0, "mid_db": 3.0, "high_db": 4.0, "deess": 0.4, "comp_thr": -22.0,
                     "comp_ratio": 5.0, "drive_db": 3.0, "echo_mix": 0.22, "echo_ms": 250, "echo_fb": 0.35,
                     "echo_pp": True, "reverb_wet": 0.12, "width": 1.2},
    "Démon / Boss final": {"pitch_st": -6.0, "hp_hz": 50, "low_db": 6.0, "comp_thr": -22.0, "comp_ratio": 4.0,
                           "drive_db": 8.0, "chorus_mix": 0.25, "reverb_wet": 0.4, "reverb_room": 0.8,
                           "echo_mix": 0.25, "echo_ms": 400, "echo_fb": 0.45},
    "Nuit radio — chaude": {"hp_hz": 70, "low_db": 4.0, "mud_db": -1.0, "mid_db": 1.5, "high_db": 1.0,
                            "deess": 0.4, "comp_thr": -20.0, "comp_ratio": 3.0, "drive_db": 1.5,
                            "reverb_wet": 0.1, "reverb_room": 0.3},
    "Diva club": {"hp_hz": 120, "mid_db": 3.0, "high_db": 4.0, "deess": 0.6, "comp_thr": -20.0, "comp_ratio": 3.0,
                  "drive_db": 1.0, "echo_mix": 0.2, "echo_ms": 350, "echo_fb": 0.4, "echo_pp": True,
                  "reverb_wet": 0.25, "reverb_room": 0.6, "width": 1.2},
    "Narrateur littéraire": {"hp_hz": 75, "low_db": 3.0, "mud_db": -2.0, "mid_db": 2.0, "high_db": 2.0,
                             "deess": 0.5, "comp_thr": -22.0, "comp_ratio": 2.5, "drive_db": 1.0,
                             "reverb_wet": 0.12, "reverb_room": 0.35},
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
    "Ping-pong DJ": {"hp_hz": 100, "comp_thr": -20.0, "mid_db": 2.0, "high_db": 3.0, "echo_mix": 0.5,
                     "echo_ms": 300, "echo_fb": 0.5, "echo_pp": True, "reverb_wet": 0.12, "width": 1.3},
    "Géant": {"pitch_st": -6.0, "low_db": 5.0, "hp_hz": 50, "comp_thr": -20.0, "reverb_wet": 0.25,
              "reverb_room": 0.7, "echo_mix": 0.15, "echo_ms": 300, "echo_fb": 0.3},
    "Enfant / Chipmunk": {"pitch_st": 7.0, "high_db": 3.0, "hp_hz": 200},
    "Dalek / Ring mod": {"ring_mix": 0.9, "ring_hz": 60, "hp_hz": 200, "comp_thr": -20.0, "drive_db": 4.0},
    "Flanger jet": {"flanger_mix": 0.6, "hp_hz": 120, "comp_thr": -20.0, "reverb_wet": 0.1},
    "Phaser spatial": {"phaser_mix": 0.6, "hp_hz": 120, "reverb_wet": 0.3, "reverb_room": 0.7, "width": 1.4},
    "Voix inversée": {"reverse": True, "reverb_wet": 0.3, "reverb_room": 0.6},
    "Voix grasse": {"hp_hz": 60, "low_db": 6.0, "mid_db": 2.0, "high_db": 1.5, "deess": 0.4, "comp_thr": -22.0,
                    "comp_ratio": 5.0, "drive_db": 6.0, "pitch_st": -1.5, "reverb_wet": 0.08, "reverb_room": 0.3},
    "Agressif / Hype": {"hp_hz": 100, "low_db": 3.0, "mud_db": -2.0, "mid_db": 5.0, "high_db": 3.0, "deess": 0.5,
                        "comp_thr": -28.0, "comp_ratio": 7.0, "drive_db": 10.0, "echo_mix": 0.12, "echo_ms": 160,
                        "echo_fb": 0.3, "reverb_wet": 0.1, "reverb_room": 0.3, "gain_db": 1.5},
    "Monstre / Démon": {"pitch_st": -6.0, "ring_mix": 0.25, "ring_hz": 40, "low_db": 6.0, "drive_db": 8.0,
                        "lp_hz": 9000, "comp_thr": -22.0, "reverb_wet": 0.35, "reverb_room": 0.8,
                        "echo_mix": 0.2, "echo_ms": 260, "echo_fb": 0.4},
    "Velours radio": {"hp_hz": 70, "low_db": 4.0, "mud_db": -2.0, "mid_db": 2.0, "high_db": 2.5, "deess": 0.6,
                      "comp_thr": -22.0, "comp_ratio": 3.5, "drive_db": 1.5, "reverb_wet": 0.06, "reverb_room": 0.15},
    "Narrateur littéraire": {"hp_hz": 70, "low_db": 2.0, "mud_db": -2.0, "mid_db": 1.5, "high_db": 2.0, "deess": 0.5,
                             "comp_thr": -22.0, "comp_ratio": 2.5, "reverb_wet": 0.1, "reverb_room": 0.3},
    "Voix douce / proche": {"hp_hz": 90, "low_db": 3.5, "mid_db": 1.0, "high_db": 2.0, "deess": 0.7,
                            "comp_thr": -24.0, "comp_ratio": 3.0, "reverb_wet": 0.04},
    "Voix grasse DJ": {"hp_hz": 60, "low_db": 6.0, "mud_db": -1.0, "mid_db": 3.0, "high_db": 2.0, "deess": 0.4,
                       "comp_thr": -24.0, "comp_ratio": 5.0, "drive_db": 5.0, "pitch_st": -2.0,
                       "reverb_wet": 0.08, "reverb_room": 0.3, "echo_mix": 0.12, "echo_ms": 380, "echo_fb": 0.3,
                       "gain_db": 1.0},
    "Agressive / Hype": {"hp_hz": 130, "low_db": 2.0, "mud_db": -3.0, "mid_db": 5.0, "high_db": 3.0, "deess": 0.5,
                         "comp_thr": -26.0, "comp_ratio": 7.0, "drive_db": 9.0, "echo_mix": 0.18, "echo_ms": 140,
                         "echo_fb": 0.25, "reverb_wet": 0.10, "reverb_room": 0.3, "gain_db": 1.0},
    "Démon / Monstre": {"pitch_st": -8.0, "hp_hz": 50, "low_db": 6.0, "lp_hz": 8000, "drive_db": 10.0,
                        "chorus_mix": 0.3, "comp_thr": -22.0, "reverb_wet": 0.4, "reverb_room": 0.8,
                        "echo_mix": 0.2, "echo_ms": 300, "echo_fb": 0.4},
    "Voix douce proche (ASMR)": {"hp_hz": 100, "low_db": 3.0, "mid_db": -1.0, "high_db": 2.0, "deess": 0.7,
                                 "comp_thr": -22.0, "comp_ratio": 3.0, "reverb_wet": 0.06, "reverb_room": 0.2},
    "Narrateur littéraire": {"hp_hz": 80, "mud_db": -2.0, "low_db": 2.0, "mid_db": 1.5, "high_db": 1.5, "deess": 0.5,
                             "comp_thr": -20.0, "comp_ratio": 2.5, "drive_db": 1.0, "reverb_wet": 0.10,
                             "reverb_room": 0.4},
    "Radio nuit / Late night": {"hp_hz": 100, "low_db": 4.0, "mid_db": 1.0, "high_db": -1.0, "deess": 0.5,
                                "comp_thr": -22.0, "comp_ratio": 4.0, "drive_db": 2.0, "reverb_wet": 0.12,
                                "reverb_room": 0.35},
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


def tremolo(a: np.ndarray, depth: float, hz: float) -> np.ndarray:
    if depth <= 0:
        return a
    t = np.arange(a.shape[1]) / audio.SR
    return (a * (1 - depth * (0.5 - 0.5 * np.cos(2 * np.pi * hz * t)))).astype(np.float32)


def ringmod(a: np.ndarray, hz: float, mix: float) -> np.ndarray:
    if mix <= 0:
        return a
    car = np.sin(2 * np.pi * hz * np.arange(a.shape[1]) / audio.SR)
    return ((1 - mix) * a + mix * a * car).astype(np.float32)


def widen(a: np.ndarray, w: float) -> np.ndarray:
    mid, side = (a[0] + a[1]) / 2, (a[0] - a[1]) / 2 * w
    return np.vstack([mid + side, mid - side]).astype(np.float32)


def echo_wet(seg: np.ndarray, ms: float, fb: float, tone_hz: float = 5000.0,
             pingpong: bool = True, max_taps: int = 10) -> np.ndarray:
    """Répétitions d'écho SEULES (sans le signal sec), avec ping-pong G/D optionnel."""
    sr = audio.SR
    d = max(1, int(ms * sr / 1000))
    fb = float(np.clip(fb, 0.05, 0.9))
    taps = int(max(1, min(max_taps, np.ceil(np.log(0.03) / np.log(fb)) + 1)))
    n = seg.shape[1]
    wet = np.zeros((2, n + d * taps), np.float32)
    mono = seg.mean(axis=0)
    for k in range(1, taps + 1):
        g, off = fb ** (k - 1), d * k
        if pingpong:
            ch = (k - 1) % 2
            wet[ch, off : off + n] += mono * g
            wet[1 - ch, off : off + n] += mono * g * 0.25
        else:
            wet[:, off : off + n] += seg * g
    return sy.lp(wet, tone_hz).astype(np.float32)


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
        p.append(LowShelfFilter(150.0, float(q["low_db"])))
    if q["mud_db"]:
        p.append(PeakFilter(320.0, float(q["mud_db"]), 1.0))
    if q["mid_db"]:
        p.append(PeakFilter(3500.0, float(q["mid_db"]), 0.9))
    if q["high_db"]:
        p.append(HighShelfFilter(9000.0, float(q["high_db"])))
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
    if q["flanger_mix"] > 0:
        p.append(Chorus(rate_hz=0.25, depth=0.9, centre_delay_ms=2.0, feedback=0.65, mix=float(q["flanger_mix"])))
    if q["phaser_mix"] > 0:
        p.append(Phaser(rate_hz=0.6, depth=0.6, centre_frequency_hz=1300.0, feedback=0.3,
                        mix=float(q["phaser_mix"])))
    if q["echo_mix"] > 0 and not q["echo_pp"]:
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
    """Applique toute la chaîne, en laissant les queues d'écho/reverb se terminer."""
    q = {**DEFAULTS, **params}
    if q["reverse"]:
        a = np.ascontiguousarray(a[:, ::-1])
    a = ringmod(tremolo(deess(a, q["deess"]), q["trem_depth"], q["trem_hz"]), q["ring_hz"], q["ring_mix"])
    tail = 0.0
    if q["echo_mix"] > 0:
        tail += min(4.0, q["echo_ms"] / 1000 * (2 + 8 * q["echo_fb"]))
    if q["reverb_wet"] > 0:
        tail += 0.8 + 3 * q["reverb_room"]
    padded = np.hstack([a, audio.silence(tail)]) if tail else a
    out = build_board(q)(np.ascontiguousarray(padded, dtype=np.float32), audio.SR)
    if q["echo_pp"] and q["echo_mix"] > 0:
        out = audio.mix(out, echo_wet(out, q["echo_ms"], q["echo_fb"], 6000.0, True) * q["echo_mix"] * 1.4, 0.0)
    if abs(q["width"] - 1.0) > 1e-3:
        out = widen(out, q["width"])
    return audio.trim_silence(out, trim_start=False, thr_db=-60.0, pad_s=0.1)
