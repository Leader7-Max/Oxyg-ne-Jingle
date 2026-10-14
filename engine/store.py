"""Bibliothèque de session : créations, statistiques de loudness, export des stems."""
from __future__ import annotations

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


# ---- clips de voix enregistrées (Labo voix -> Studio) ----
def clips() -> list[dict]:
    return st.session_state.setdefault(CLIPS, [])


def add_clip(name: str, a: np.ndarray) -> dict:
    clip = {"id": uuid.uuid4().hex[:8], "name": name.strip() or "clip", "audio": a.astype(np.float32),
            "seconds": audio.duration(a)}
    lst = clips()
    lst.insert(0, clip)
    del lst[MAX_CLIPS:]
    return clip


def get_clip(clip_id: str) -> dict | None:
    return next((c for c in clips() if c["id"] == clip_id), None)
