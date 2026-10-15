"""Synthèse vocale neurale gratuite (edge-tts), avec cache, relances et appels en parallèle."""
from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import edge_tts

from config import VOICES
from engine import audio


async def _fetch(text: str, voice: str, rate: str, pitch: str, volume: str) -> bytes:
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    buf = bytearray()
    async for chunk in com.stream():
        if chunk["type"] == "audio":
            buf.extend(chunk["data"])
    return bytes(buf)


@lru_cache(maxsize=256)
def _synth_bytes(text: str, voice: str, rate: int, pitch: int, volume: int) -> bytes:
    args = (text, voice, f"{rate:+d}%", f"{pitch:+d}Hz", f"{volume:+d}%")
    last: Exception | None = None
    for attempt in range(3):                       # le service gratuit refuse parfois un appel : on réessaie
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                data = ex.submit(lambda: asyncio.run(_fetch(*args))).result()
            if data:
                return data
            last = RuntimeError("Aucun audio reçu (connexion internet requise).")
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"Synthèse vocale impossible : {last}")


def synthesize(text: str, voice_label: str, rate: int = 0, pitch: int = 0, volume: int = 0):
    voice = VOICES.get(voice_label, voice_label)
    return audio.decode(_synth_bytes(text.strip(), voice, int(rate), int(pitch), int(volume)))


def synthesize_many(jobs, workers: int = 4):
    """jobs : [(texte, voix, vitesse, hauteur, volume)] -> liste d'audios (même ordre)."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(lambda j: synthesize(*j), jobs))
