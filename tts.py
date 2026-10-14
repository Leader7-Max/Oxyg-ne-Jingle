"""Synthèse vocale neurale gratuite (edge-tts) + gestion des scripts multi-voix."""
from __future__ import annotations

import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import edge_tts

from config import VOICES
from engine import audio

_B_LINE = re.compile(r"^\s*(?:B|2)\s*[:：]\s*(.+)$", re.IGNORECASE)
_PAUSE = re.compile(r"^\s*\[pause\s*([\d.,]+)\s*s?\]\s*$", re.IGNORECASE)


async def _fetch(text: str, voice: str, rate: str, pitch: str, volume: str) -> bytes:
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    buf = bytearray()
    async for chunk in com.stream():
        if chunk["type"] == "audio":
            buf.extend(chunk["data"])
    return bytes(buf)


@lru_cache(maxsize=64)
def _synth_bytes(text: str, voice: str, rate: int, pitch: int, volume: int) -> bytes:
    args = (text, voice, f"{rate:+d}%", f"{pitch:+d}Hz", f"{volume:+d}%")
    # thread dédié : évite tout conflit avec la boucle d'événements de Streamlit
    with ThreadPoolExecutor(max_workers=1) as ex:
        data = ex.submit(lambda: asyncio.run(_fetch(*args))).result()
    if not data:
        raise RuntimeError("Aucun audio reçu (connexion internet requise).")
    return data


def synthesize(text: str, voice_label: str, rate: int = 0, pitch: int = 0, volume: int = 0):
    voice = VOICES.get(voice_label, voice_label)
    return audio.decode(_synth_bytes(text.strip(), voice, int(rate), int(pitch), int(volume)))


def parse_script(script: str):
    """Lignes -> [('pause', s) | ('line', ('A'|'B', texte))]."""
    out = []
    for raw in script.splitlines():
        if not raw.strip():
            continue
        if m := _PAUSE.match(raw):
            out.append(("pause", float(m.group(1).replace(",", "."))))
        elif m := _B_LINE.match(raw):
            out.append(("line", ("B", m.group(1).strip())))
        else:
            out.append(("line", ("A", raw.strip())))
    return out


def render_script(script: str, voice_a: str, voice_b: str, rate=0, pitch=0, volume=0,
                  gap_s: float = 0.25):
    parts = []
    for kind, val in parse_script(script):
        if kind == "pause":
            parts.append(audio.silence(val))
        else:
            who, line = val
            parts.append(synthesize(line, voice_b if who == "B" else voice_a, rate, pitch, volume))
            parts.append(audio.silence(gap_s))
    return audio.concat(parts)
