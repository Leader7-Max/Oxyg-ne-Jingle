"""Effets DJ synthétisés : scratch, sirènes, airhorn, impacts, risers… (aucun fichier, aucun droit)."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter1d

from engine import audio
from engine import synth as sy
from engine.audio import SR


def _out(x, peak_db: float = -3.0) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = sy.stereo(x)
    return audio.normalize(x, peak_db)


def _env(n: int, attack: float = 0.005, release: float = 0.05) -> np.ndarray:
    e = np.ones(n)
    a, r = min(int(attack * SR), n), min(int(release * SR), n)
    if a > 0:
        e[:a] = np.linspace(0, 1, a)
    if r > 0:
        e[n - r:] *= np.linspace(1, 0, r)
    return e


# ---------- Scratch ----------
def _scratch_src(dur: float = 0.7) -> np.ndarray:
    t = sy.t_axis(dur)
    f0 = 190 * (1 + 0.12 * np.sin(2 * np.pi * 5 * t))
    ph = 2 * np.pi * np.cumsum(f0) / SR
    sig = sum(np.sin(k * ph) / k for k in range(1, 18))
    sig = sy.bp(sig, 600, 2400) + 0.08 * sy.hp(sy.noise(t.size), 3500)
    return sig / np.max(np.abs(sig))


def _scratch(points, dur: float, gate_hz: float = 0.0) -> np.ndarray:
    src, n = _scratch_src(), int(dur * SR)
    L = src.size
    pos = np.interp(np.linspace(0, 1, n), [p[0] for p in points], [p[1] for p in points])
    pos = uniform_filter1d(pos, size=int(0.010 * SR))
    speed = np.abs(np.gradient(pos)) * L            # 1.0 = vitesse normale du disque
    amp = np.clip(speed / 0.8, 0, 1) ** 0.8         # le son s'arrête quand le disque s'arrête
    out = np.interp(pos * (L - 1), np.arange(L), src) * amp
    if gate_hz:
        gate = (np.sin(2 * np.pi * gate_hz * np.arange(n) / SR) > 0).astype(float)
        out *= uniform_filter1d(gate, size=int(0.004 * SR))
    out += 0.03 * sy.hp(sy.noise(n), 2000) * np.clip(amp * 2, 0, 1)   # craquement vinyle
    return _out(np.tanh(1.8 * out) * _env(n, 0.002, 0.03))


def scratch_wiki():
    return _scratch([(0, .2), (.12, .7), (.25, .2), (.37, .7), (.5, .25), (.62, .75), (.75, .3), (.88, .8), (1, .8)], 0.95)


def scratch_long():
    return _scratch([(0, .1), (.22, .95), (.32, .95), (.5, .35), (.6, .35), (.78, .9), (1, .9)], 1.5)


def scratch_transform():
    return _scratch([(0, .1), (1, .9)], 1.1, gate_hz=9.0)


def tape_stop():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    speed = np.exp(-t * 2.6)
    src = _scratch_src()
    idx = np.clip(np.cumsum(speed), 0, src.size - 1)
    return _out(np.interp(idx, np.arange(src.size), src) * speed ** 0.4 * _env(n, 0.002, 0.02))


def rewind():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    speed = 2.5 * np.exp(-t * 3.5)
    src = _scratch_src()
    idx = np.clip(src.size - 1 - np.cumsum(speed), 0, src.size - 1)
    return _out(np.interp(idx, np.arange(src.size), src) * np.minimum(1, speed) * _env(n, 0.002, 0.03))


# ---------- Sirènes ----------
def _siren(f: np.ndarray, fade: float = 0.15) -> np.ndarray:
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.tanh(1.8 * (np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)))
    return _out(sy.lp(sig, 4200) * _env(f.size, fade, 0.25))


def siren_wail():
    t = sy.t_axis(5.0)
    return _siren(650 + 650 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 2.4)))


def siren_yelp():
    t = sy.t_axis(3.2)
    return _siren(700 + 700 * (0.5 - 0.5 * np.cos(2 * np.pi * 3.3 * t)))


def siren_hilo():
    t = sy.t_axis(4.0)
    f = np.where(np.floor(t / 0.5) % 2 == 0, 960.0, 770.0)
    return _siren(uniform_filter1d(f, size=int(0.01 * SR)))


# ---------- Airhorn, impacts, montées ----------
def _horn(dur: float, freqs=(349, 466, 587)) -> np.ndarray:
    t = sy.t_axis(dur)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
    sig = np.zeros(t.size)
    for f in freqs:
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        sig += sum(np.sin(k * ph) / k ** 0.9 for k in range(1, 9))
    return np.tanh(0.7 * sig) * _env(t.size, 0.012, 0.12)


def airhorn():
    gap = np.zeros(int(0.09 * SR))
    return _out(sy.bp(np.concatenate([_horn(0.22), gap, _horn(0.22), gap, _horn(0.9)]), 250, 6000))


def impact():
    t = sy.t_axis(1.8)
    boom = np.sin(2 * np.pi * np.cumsum(35 + 110 * np.exp(-t * 3)) / SR) * np.exp(-t * 2.2)
    hit = sy.noise(t.size) * np.exp(-t * 25) * 0.4
    return _out(boom + hit)


def sub_drop():
    t = sy.t_axis(2.5)
    sig = np.sin(2 * np.pi * np.cumsum(28 + 80 * np.exp(-t * 3.0)) / SR) * np.exp(-t * 1.6)
    return _out(np.tanh(1.4 * sig) * _env(t.size, 0.003, 0.05))


def riser():
    n = int(3.0 * SR)
    t = np.linspace(0, 1, n)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 5000 * t ** 2) / SR)
    noise = np.convolve(sy.noise(n), np.ones(4) / 4, "same")
    return _out((0.6 * tone + 0.4 * noise) * t ** 1.5)


def reverse_swell():
    n = int(2.6 * SR)
    t = np.linspace(0, 1, n)
    return _out(sy.hp(sy.noise(n), 1500) * t ** 2.5 * _env(n, 0.0, 0.004))


def whoosh():
    n = int(1.2 * SR)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t) ** 2
    ch = [np.convolve(sy.noise(n), np.ones(10) / 10, "same") * env for _ in range(2)]
    return _out(np.vstack(ch))


def snare_roll():
    d, n = 2.4, int(2.4 * SR)
    out, t, gap, hit = np.zeros(n), 0.0, 0.22, sy.snare()
    while t < d - 0.1:
        i = int(t * SR)
        seg = hit[: n - i]
        out[i : i + seg.size] += seg * (0.35 + 0.65 * t / d)
        t, gap = t + gap, max(0.035, gap * 0.88)
    return _out(out)


def laser():
    t = sy.t_axis(0.6)
    return _out(np.sin(2 * np.pi * np.cumsum(300 + 3000 * np.exp(-t * 12)) / SR) * np.exp(-t * 5))


def beeps():
    def beep(d):
        t = sy.t_axis(d)
        return np.sin(2 * np.pi * 1000 * t) * np.minimum(1, np.minimum(t, d - t) * 200)
    return _out(np.concatenate([beep(0.18), np.zeros(int(SR * 0.12)), beep(0.18)]))


EFFECTS = {
    "🎛️ Scratch — wiki wiki": scratch_wiki,
    "🎛️ Scratch — long": scratch_long,
    "🎛️ Scratch — transform": scratch_transform,
    "💿 Tape stop": tape_stop,
    "⏪ Rewind": rewind,
    "🚨 Sirène — wail": siren_wail,
    "🚨 Sirène — yelp": siren_yelp,
    "🚨 Sirène — hi-lo": siren_hilo,
    "📯 Airhorn DJ": airhorn,
    "💥 Impact": impact,
    "🔊 Sub drop": sub_drop,
    "📈 Riser": riser,
    "🌬️ Reverse swell": reverse_swell,
    "🌪️ Whoosh": whoosh,
    "🥁 Roulement caisse claire": snare_roll,
    "🔫 Laser": laser,
    "📻 Bips radio": beeps,
}


def get(label: str):
    fn = EFFECTS.get(label)
    return fn() if fn else None
