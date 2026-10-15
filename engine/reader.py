"""Lecture « pro » d'un texte collé : normalisation, pauses, intonation, mise en valeur, sous-titres."""
from __future__ import annotations

import re
import textwrap

from config import VOICES
from engine import audio, tts

# rate/pitch/vol : décalage de base ; para/sent/comma : pauses (s) ; var : amplitude des variations ;
# fall : chute de hauteur en fin de paragraphe
STYLES = {
    "Naturel": dict(rate=0, pitch=0, vol=0, para=0.60, sent=0.35, comma=0.15, var=0.5, fall=-2),
    "Narrateur littéraire": dict(rate=-8, pitch=-4, vol=0, para=1.00, sent=0.55, comma=0.25, var=1.0, fall=-5),
    "Radio dynamique": dict(rate=10, pitch=2, vol=6, para=0.45, sent=0.22, comma=0.10, var=1.2, fall=-1),
    "Annonceur événement": dict(rate=4, pitch=-6, vol=10, para=0.70, sent=0.38, comma=0.14, var=1.4, fall=-3),
    "Journal / information": dict(rate=6, pitch=0, vol=0, para=0.60, sent=0.28, comma=0.12, var=0.6, fall=-3),
    "Conte & poésie": dict(rate=-14, pitch=-2, vol=-4, para=1.30, sent=0.75, comma=0.35, var=1.2, fall=-6),
    "Publicité punchy": dict(rate=14, pitch=3, vol=10, para=0.40, sent=0.20, comma=0.08, var=1.5, fall=0),
    "Documentaire": dict(rate=-4, pitch=-3, vol=0, para=0.90, sent=0.45, comma=0.20, var=0.8, fall=-4),
}
STYLE_HELP = {
    "Naturel": "Lecture simple et neutre.",
    "Narrateur littéraire": "Lent, grave, pauses longues : roman, récit, livre audio.",
    "Radio dynamique": "Rapide et souriant : animateur radio.",
    "Annonceur événement": "Voix forte et solennelle : annonce de soirée, de concert.",
    "Journal / information": "Neutre, net et régulier : flash info.",
    "Conte & poésie": "Très lent, pauses marquées, voix douce.",
    "Publicité punchy": "Très rapide et énergique : spot publicitaire.",
    "Documentaire": "Posé et clair : voix off de documentaire.",
}

_OPEN, _CLOSE = "\u0001", "\u0002"
_PAUSE_LINE = re.compile(r"^\s*\[pause\s*([\d.,]+)\s*s?\]\s*$", re.I)
_EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]")
_FR = [(r"(\d)\s?%", r"\1 pour cent"), (r"%", " pour cent"), (r"&", " et "), (r"€", " euros"), (r"\$", " dollars"),
       (r"°C", " degrés"), (r"\bn°\s*", "numéro "), (r"\betc\.", "et cetera"), (r"\bM\.\s", "Monsieur "),
       (r"\bMme\b\.?", "Madame"), (r"\bDr\b\.?", "Docteur"), (r"\bvs\b\.?", "contre"),
       (r"(\d{1,2})\s?h\s?(\d{2})\b", r"\1 heures \2"), (r"(\d{1,2})\s?h\b", r"\1 heures"),
       (r"\bkm/h\b", "kilomètres par heure"), (r"\bkm\b", "kilomètres"), (r"\bsam\.", "samedi"),
       (r"\bdim\.", "dimanche"), (r"\bven\.", "vendredi")]
_EN = [(r"(\d)\s?%", r"\1 percent"), (r"%", " percent"), (r"&", " and "), (r"€", " euros"),
       (r"\$", " dollars"), (r"\bvs\b\.?", "versus")]


def normalize(text: str, lang: str = "fr") -> str:
    """Nettoie le texte collé : liens, emojis, abréviations, symboles lus en toutes lettres."""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"https?://\S+|www\.\S+", "", t)
    t = _EMOJI.sub("", t)
    t = re.sub(r"\*([^*\n]+)\*", _OPEN + r"\1" + _CLOSE, t)       # *mot* = mise en valeur
    t = re.sub(r"^[#>\-•]+\s*", "", t, flags=re.M)
    t = re.sub(r"[`_~]+", "", t)
    for pat, rep in (_FR if lang == "fr" else _EN):
        t = re.sub(pat, rep, t)
    t = t.replace("...", "…")
    t = re.sub(r"[!?]{2,}", lambda m: m.group(0)[0], t)
    return re.sub(r"[ \t]+", " ", t).strip()


def _split_sentences(par: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", par.strip()) if s.strip()]


def _chunks(sent: str, max_words: int = 14) -> list[str]:
    """Coupe les phrases longues aux virgules / points-virgules pour respirer."""
    if len(sent.split()) <= max_words:
        return [sent]
    out: list[str] = []
    for part in re.split(r"(?<=[,;:])\s+|\s+[—–]\s+", sent):
        if out and len(part.split()) < 3:
            out[-1] += " " + part
        else:
            out.append(part)
    return out


def _emph_parts(text: str, caps: bool):
    alt = r"|\b([A-ZÀ-ÖØ-Ý]{4,})\b" if caps and text.upper() != text else ""
    pat = re.compile(_OPEN + r"(.+?)" + _CLOSE + alt)
    parts, pos = [], 0
    for m in pat.finditer(text):
        if m.start() > pos:
            parts.append((text[pos:m.start()], False))
        parts.append((next(g for g in m.groups() if g), True))
        pos = m.end()
    if pos < len(text):
        parts.append((text[pos:], False))
    clean = [(s.replace(_OPEN, "").replace(_CLOSE, "").strip(), e) for s, e in parts]
    return [(s.lstrip(",;: ") if i else s, e) for i, (s, e) in enumerate(clean) if re.search(r"\w", s)]


def _prosody(sent: str, st: dict, idx: int, par_end: bool):
    r = p = v = 0.0
    end, var = sent.rstrip()[-1:], st["var"]
    if end == "?":
        p, r = p + 4 * var, r - 3
    elif end == "!":
        r, p, v = r + 5 * var, p + 3 * var, v + 6 * var
    elif end == "…":
        r, p = r - 6, p - 2
    if par_end:
        r, p = r - 4 * var, p + st["fall"]
    p += ((idx * 7) % 5 - 2) * 0.7 * var          # petites variations : jamais monotone
    r += ((idx * 3) % 5 - 2) * 0.9 * var
    return r, p, v


def _after(chunk: str, st: dict, last_chunk: bool, par_end: bool) -> float:
    c = chunk.rstrip()[-1:]
    if last_chunk:
        return st["para"] if par_end else st["sent"] * {"!": 1.0, "?": 1.1, "…": 1.6}.get(c, 1.0)
    return st["comma"] * (1.7 if c in ";:" else 1.0 if c == "," else 0.5)


def _cl(v, lo, hi) -> int:
    return int(max(lo, min(hi, round(v))))


def _speech(text, rate, pitch, vol, after, sid, stext):
    return dict(kind="speech", text=text, rate=_cl(rate, -50, 100), pitch=_cl(pitch, -50, 50),
                vol=_cl(vol, -50, 50), after=round(float(after), 2), sid=sid, stext=stext)


def build_plan(text: str, voice: str, style: str = "Naturel", rate: int = 0, pitch: int = 0, vol: int = 0,
               pro: bool = True, caps: bool = False, gap: float = 0.25) -> list[dict]:
    """Transforme un texte en plan de lecture : segments à dire + pauses, avec rythme et intonation."""
    vid = VOICES.get(voice, voice)
    t = normalize(text, vid.split("-")[0])
    plan: list[dict] = []
    if not t:
        return plan
    if not pro:                                       # mode simple : 1 ligne = 1 phrase
        for line in t.split("\n"):
            if not line.strip():
                continue
            m = _PAUSE_LINE.match(line)
            if m:
                plan.append(dict(kind="pause", sec=float(m.group(1).replace(",", "."))))
            else:
                clean = line.replace(_OPEN, "").replace(_CLOSE, "").strip()
                plan.append(_speech(clean, rate, pitch, vol, gap, len(plan), clean))
        return plan

    st, sid = STYLES.get(style, STYLES["Naturel"]), 0
    for par in re.split(r"\n\s*\n", t):
        blocks, buf = [], []
        for line in par.split("\n"):
            if not line.strip():
                continue
            m = _PAUSE_LINE.match(line)
            if m:
                if buf:
                    blocks.append(("text", buf))
                    buf = []
                blocks.append(("pause", float(m.group(1).replace(",", "."))))
            else:
                buf.append(line.strip())
        if buf:
            blocks.append(("text", buf))
        for bi, (kind, val) in enumerate(blocks):
            if kind == "pause":
                plan.append(dict(kind="pause", sec=val))
                continue
            joined = val[0]
            for ln in val[1:]:                        # retour à la ligne = petite respiration
                joined += (" " if joined[-1] in ".!?…:;,—" else ", ") + ln
            sents = _split_sentences(joined)
            for si, sent in enumerate(sents):
                last_sent = si == len(sents) - 1
                par_end = last_sent and bi == len(blocks) - 1
                r0, p0, v0 = _prosody(sent, st, sid, par_end)
                stext = sent.replace(_OPEN, "").replace(_CLOSE, "")
                chunks = _chunks(sent)
                for ci, ch in enumerate(chunks):
                    last_ch = ci == len(chunks) - 1
                    after = _after(ch, st, last_ch, par_end and last_ch)
                    if last_ch and last_sent and not par_end:
                        after = st["sent"]
                    r, p, v = (r0, p0, v0) if last_ch else (r0, p0 + st["var"], v0)   # petite montée si la phrase continue
                    parts = _emph_parts(ch, caps)
                    for pi, (txt, emph) in enumerate(parts):
                        rr, pp, vv = (r - 8, p + 4, v + 12 * min(st["var"], 1.2)) if emph else (r, p, v)
                        a = after if pi == len(parts) - 1 else 0.06
                        plan.append(_speech(txt, rate + st["rate"] + rr, pitch + st["pitch"] + pp,
                                            vol + st["vol"] + vv, a, sid, stext))
                sid += 1
    if plan and plan[-1]["kind"] == "speech":
        plan[-1]["after"] = 0.0
    return plan


def describe(plan: list[dict]) -> list[dict]:
    rows = []
    for it in plan:
        if it["kind"] == "pause":
            rows.append({"Type": "⏸ pause", "Texte": "", "Vitesse": "", "Hauteur": "", "Volume": "", "Pause après (s)": it["sec"]})
        else:
            rows.append({"Type": "🗣 lecture", "Texte": it["text"], "Vitesse": f"{it['rate']:+d} %",
                         "Hauteur": f"{it['pitch']:+d} Hz", "Volume": f"{it['vol']:+d} %", "Pause après (s)": it["after"]})
    return rows


def render(plan: list[dict], voice: str):
    """Synthétise le plan (en parallèle) et assemble : retourne (audio, timings par phrase)."""
    speech = [it for it in plan if it["kind"] == "speech"]
    if not speech:
        raise ValueError("Aucun texte à lire.")
    auds = tts.synthesize_many([(it["text"], voice, it["rate"], it["pitch"], it["vol"]) for it in speech])
    parts, n, ai, spans = [], 0, 0, {}
    for it in plan:
        if it["kind"] == "pause":
            s = audio.silence(it["sec"])
            parts.append(s)
            n += s.shape[1]
            continue
        a = audio.fade(audio.trim_silence(auds[ai], -48.0, 0.02), 0.004, 0.008)
        ai += 1
        sp = spans.setdefault(it["sid"], [n, n, it["stext"]])
        parts.append(a)
        n += a.shape[1]
        sp[1] = n
        s = audio.silence(it["after"])
        parts.append(s)
        n += s.shape[1]
    timings = [dict(text=v[2], start=v[0] / audio.SR, end=v[1] / audio.SR) for _, v in sorted(spans.items())]
    return audio.concat(parts), timings


def _ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def to_srt(timings: list[dict], offset: float = 0.0, width: int = 42) -> str:
    """Sous-titres .srt prêts pour un logiciel de montage vidéo."""
    out = []
    for i, t in enumerate(timings, 1):
        lines = textwrap.wrap(t["text"], width) or [t["text"]]
        out.append(f"{i}\n{_ts(t['start'] + offset)} --> {_ts(t['end'] + offset)}\n" + "\n".join(lines) + "\n")
    return "\n".join(out)
