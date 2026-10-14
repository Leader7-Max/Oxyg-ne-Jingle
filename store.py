"""Bibliothèque de session : garde les créations pour les réécouter / télécharger."""
from __future__ import annotations

import re
import time
import uuid

import streamlit as st

from engine import audio

KEY, MAX_ITEMS = "library", 15


def items() -> list[dict]:
    return st.session_state.setdefault(KEY, [])


def add(name: str, a) -> dict:
    slug = re.sub(r"[^\w\-]+", "-", name.strip().lower()).strip("-") or "jingle"
    try:
        mp3 = audio.export(a, "mp3")
    except Exception:  # noqa: BLE001
        mp3 = None
    item = {"id": uuid.uuid4().hex[:8], "name": slug, "ts": time.strftime("%H:%M"),
            "seconds": audio.duration(a), "wav": audio.export(a, "wav"), "mp3": mp3}
    lib = items()
    lib.insert(0, item)
    del lib[MAX_ITEMS:]
    return item


def remove(item_id: str) -> None:
    st.session_state[KEY] = [i for i in items() if i["id"] != item_id]
