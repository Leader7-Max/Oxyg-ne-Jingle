"""Bibliothèque de session : créations, statistiques de loudness, export des stems."""
from __future__ import annotations

import hashlib
import io
import re
import time
import uuid
import zipfile

import numpy as np
import streamlit as st

from engine import audio, master

KEY, CLIPS, MAX_ITEMS, MAX_CLIPS = "library", "clips", 10, 8


def items() -> list[dict]:
    return st.session_state.setdefault(KEY, [])


def _zip_stems(final: np.ndarray, stems: dict) -> bytes:
    peak = max((float(np.abs(v).max()) for v in stems.values()), default=1.0)
    scale = min(1.0, 0.98 / peak) if peak > 0 else 1.0
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mix_final.wav", audio.export(final, "wav", 24))
        for name, v in stems.items():
            if np.abs(v).max() > 1e-6:
                z.writestr(f"stem_{name}.wav", audio.export(v * scale, "wav", 16))
    return buf.getvalue()


def make_item(name: str, a: np.ndarray, stems: dict | None = None, layout=None) -> dict:
    slug = re.sub(r"[^\w\-]+", "-", name.strip().lower()).strip("-") or "jingle"
    try:
        mp3 = audio.export(a, "mp3")
    except Exception:  # noqa: BLE001
        mp3 = None
    stats = master.measure(a)
    return {"id": uuid.uuid4().hex[:8], "name": slug, "ts": time.strftime("%H:%M"),
            "seconds": audio.duration(a), "lufs": stats["lufs"], "peak": stats["peak"],
            "peaks": audio.peaks(a), "wav": audio.export(a, "wav", 24), "mp3": mp3,
            "stems": _zip_stems(a, stems) if stems else None, "layout": layout}


def push(item: dict) -> dict:
    lib = items()
    lib.insert(0, item)
    for old in lib[1:]:      # les stems pèsent lourd : on ne garde que ceux du dernier projet
        old["stems"] = None
    del lib[MAX_ITEMS:]
    return item


def add(name: str, a: np.ndarray, stems: dict | None = None, layout=None) -> dict:
    return push(make_item(name, a, stems, layout))


def remove(item_id: str) -> None:
    st.session_state[KEY] = [i for i in items() if i["id"] != item_id]


# ---- médiathèque : voix, effets et musiques importés ----
MEDIA = "media"
LIMITS = {"voix": 10, "effet": 16, "musique": 3}
MAX_MUSIC_S = 300.0


def media(kind: str | None = None) -> list[dict]:
    lst = st.session_state.setdefault(MEDIA, [])
    return [m for m in lst if kind in (None, m["kind"])]


def add_media(kind: str, name: str, a: np.ndarray, sig=None) -> dict:
    a = a.astype(np.float32)
    if kind == "musique" and audio.duration(a) > MAX_MUSIC_S:
        a = a[:, : int(MAX_MUSIC_S * audio.SR)]
    m = {"id": uuid.uuid4().hex[:8], "kind": kind, "name": (name or kind).strip()[:40] or kind,
         "audio": a, "seconds": audio.duration(a), "sig": sig}
    lst = st.session_state.setdefault(MEDIA, [])
    lst.insert(0, m)
    same = [x for x in lst if x["kind"] == kind]
    for old in same[LIMITS.get(kind, 10):]:
        lst.remove(old)
    return m


def get_media(media_id: str | None) -> dict | None:
    return next((m for m in media() if m["id"] == media_id), None)


def remove_media(media_id: str) -> None:
    st.session_state[MEDIA] = [m for m in media() if m["id"] != media_id]


def has_sig(sig) -> bool:
    return any(m.get("sig") == sig for m in media())


# compatibilité : « clips » = voix de la médiathèque
def clips() -> list[dict]:
    return media("voix")


def add_clip(name: str, a: np.ndarray) -> dict:
    return add_media("voix", name, a)


def get_clip(clip_id: str | None) -> dict | None:
    return get_media(clip_id)
