"""Thème Oxygène v2 : identité « studio néon » + composants (hero, sections, chips, waveform)."""
from __future__ import annotations

import html

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
:root{--cyan:#22D3EE;--indigo:#7C83FF;--pink:#F472B6;--bg:#070B14;
  --glass:rgba(255,255,255,.045);--line:rgba(255,255,255,.10);--muted:#8EA0BC;}
html, body, [class*="css"]{font-family:'Inter',sans-serif;}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif !important;letter-spacing:-.02em;}
.stApp{background:
  radial-gradient(900px 520px at 6% -8%, rgba(34,211,238,.15), transparent 60%),
  radial-gradient(900px 520px at 100% 0%, rgba(124,131,255,.17), transparent 60%),
  radial-gradient(800px 520px at 50% 115%, rgba(244,114,182,.11), transparent 60%), var(--bg);}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.4rem;max-width:1080px;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1627,#080e1a);
  border-right:1px solid var(--line);}

/* Marque */
.oxy-brand{display:flex;align-items:center;gap:12px;margin:4px 0 14px;}
.oxy-brand-name{font-family:'Space Grotesk';font-weight:700;font-size:1.35rem;line-height:1;
  background:linear-gradient(90deg,var(--cyan),var(--pink));-webkit-background-clip:text;
  background-clip:text;color:transparent;}
.oxy-brand-sub{font-size:.68rem;letter-spacing:.28em;color:var(--muted);margin-top:4px;}

/* Hero */
.oxy-hero{position:relative;padding:22px 22px 18px;border-radius:22px;margin-bottom:18px;
  background:linear-gradient(135deg,rgba(34,211,238,.13),rgba(124,131,255,.13) 55%,rgba(244,114,182,.13));
  border:1px solid var(--line);box-shadow:0 24px 70px -34px rgba(34,211,238,.55);}
.oxy-hero h1{margin:0;padding:0;font-size:1.9rem;line-height:1.1;
  background:linear-gradient(90deg,#fff,var(--cyan) 45%,var(--pink));-webkit-background-clip:text;
  background-clip:text;color:transparent;}
.oxy-hero p{margin:8px 0 0;color:var(--muted);font-size:.96rem;}
.oxy-badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;}
.oxy-badge{font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;padding:3px 9px;
  border-radius:999px;border:1px solid var(--line);color:#cfe6f5;background:rgba(255,255,255,.04);}
.oxy-eq{height:28px;margin-bottom:10px;display:flex;align-items:flex-end;gap:4px;}
.oxy-eq span{display:inline-block;width:5px;height:100%;border-radius:3px;transform-origin:bottom;
  background:linear-gradient(to top,var(--cyan),var(--indigo) 60%,var(--pink));
  animation:oxy-bounce 1.15s ease-in-out infinite;}
.oxy-eq span:nth-child(2){animation-delay:.12s}.oxy-eq span:nth-child(3){animation-delay:.3s}
.oxy-eq span:nth-child(4){animation-delay:.05s}.oxy-eq span:nth-child(5){animation-delay:.42s}
.oxy-eq span:nth-child(6){animation-delay:.2s}.oxy-eq span:nth-child(7){animation-delay:.35s}
.oxy-eq span:nth-child(8){animation-delay:.18s}.oxy-eq span:nth-child(9){animation-delay:.27s}
@keyframes oxy-bounce{0%,100%{transform:scaleY(.22)}50%{transform:scaleY(1)}}

/* Sections */
.oxy-sec{display:flex;align-items:center;gap:10px;margin:28px 0 10px;
  font-family:'Space Grotesk';font-weight:700;font-size:1.14rem;}
.oxy-step{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:26px;
  border-radius:8px;font-size:.8rem;font-weight:700;color:#04101c;
  background:linear-gradient(135deg,var(--cyan),var(--indigo));}

/* Cartes & contrôles */
div[data-testid="stExpander"]{border:1px solid var(--line) !important;border-radius:16px !important;
  background:var(--glass) !important;}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:var(--glass);padding:5px;border-radius:14px;
  border:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{border-radius:10px;padding:6px 14px;height:auto;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(34,211,238,.26),rgba(124,131,255,.26));}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}
.stButton>button[kind="primary"]{background:linear-gradient(90deg,var(--cyan),var(--indigo) 60%,var(--pink));
  color:#06101d;font-weight:700;border:0;border-radius:14px;padding:.75rem 1rem;
  box-shadow:0 12px 36px -12px rgba(34,211,238,.75);}
.stButton>button[kind="primary"]:hover{filter:brightness(1.08);}
.stDownloadButton>button{border-radius:12px;border:1px solid var(--line);background:var(--glass);}
textarea,input,div[data-baseweb="select"]>div{border-radius:12px !important;}

/* Résultat */
.oxy-chips{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 10px;}
.oxy-chip{padding:5px 12px;border-radius:999px;background:var(--glass);border:1px solid var(--line);font-size:.84rem;}
.oxy-chip b{color:var(--cyan);font-weight:600;}
.oxy-wave{padding:10px 12px;border-radius:16px;background:var(--glass);border:1px solid var(--line);margin-bottom:10px;}
.oxy-foot{color:var(--muted);font-size:.76rem;margin-top:26px;line-height:1.5;}

.oxy-tip{display:flex;gap:10px;padding:12px 14px;border-radius:14px;margin:8px 0 12px;font-size:.92rem;
  background:linear-gradient(135deg,rgba(34,211,238,.10),rgba(124,131,255,.10));border:1px solid var(--line);}
.oxy-tip b{color:var(--cyan);}
@media (max-width:640px){
  .block-container{padding:1.2rem .8rem 3rem;}
  .oxy-hero{padding:16px;border-radius:18px;} .oxy-hero h1{font-size:1.45rem;}
}
</style>
"""

_LOGO = (
    '<svg width="40" height="40" viewBox="0 0 38 38"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#22D3EE"/><stop offset="1" stop-color="#F472B6"/></linearGradient></defs>'
    '<circle cx="19" cy="19" r="17" fill="none" stroke="url(#lg)" stroke-width="2.5"/>'
    '<path d="M8 19h3l3-8 4 16 4-12 3 4h5" fill="none" stroke="url(#lg)" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def apply() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def header(title: str, subtitle: str = "", badges=None) -> None:
    b = "".join(f'<span class="oxy-badge">{html.escape(x)}</span>' for x in (badges or []))
    eq = "<span></span>" * 9
    st.markdown(
        f'<div class="oxy-hero"><div class="oxy-eq">{eq}</div><h1>{title}</h1>'
        f'<p>{subtitle}</p><div class="oxy-badges">{b}</div></div>',
        unsafe_allow_html=True,
    )


def section(text: str, step: int | None = None) -> None:
    badge = f'<span class="oxy-step">{step}</span>' if step else ""
    st.markdown(f'<div class="oxy-sec">{badge}<span>{text}</span></div>', unsafe_allow_html=True)


def chips(items) -> None:
    body = "".join(f'<span class="oxy-chip">{i} <b>{html.escape(t)}</b></span>' for i, t in items)
    st.markdown(f'<div class="oxy-chips">{body}</div>', unsafe_allow_html=True)


def waveform(peaks, height: int = 84, selection=None) -> None:
    """Forme d'onde SVG ; selection = (début, fin) en fractions 0-1 pour surligner une zone."""
    n, W = len(peaks), 600
    if n == 0:
        return
    cy, step = height / 2, W / n
    d = "".join(
        f"M{i * step + step / 2:.1f},{cy - max(1.5, p * cy * 0.92):.1f}V{cy + max(1.5, p * cy * 0.92):.1f}"
        for i, p in enumerate(peaks)
    )
    sel = ""
    if selection:
        a, b = max(0.0, min(1.0, selection[0])), max(0.0, min(1.0, selection[1]))
        sel = (f'<rect x="{a * W:.1f}" y="0" width="{max(2.0, (b - a) * W):.1f}" height="{height}" '
               'fill="rgba(244,114,182,.28)" stroke="#F472B6" stroke-width="1" '
               'vector-effect="non-scaling-stroke"/>')
    svg = (
        f'<svg viewBox="0 0 {W} {height}" preserveAspectRatio="none" style="width:100%;height:{height}px">'
        '<defs><linearGradient id="og" x1="0" x2="1"><stop offset="0" stop-color="#22D3EE"/>'
        '<stop offset=".55" stop-color="#7C83FF"/><stop offset="1" stop-color="#F472B6"/></linearGradient></defs>'
        f'{sel}<path d="{d}" stroke="url(#og)" stroke-width="{step * 0.62:.2f}" stroke-linecap="round" fill="none"/></svg>'
    )
    st.markdown(f'<div class="oxy-wave">{svg}</div>', unsafe_allow_html=True)


_TL_COLORS = {"voice": "#22D3EE", "bg": "#7C83FF", "sfx": "#F472B6", "echo": "#FBBF24", "music": "#34D399"}


def timeline(rows, total: float) -> None:
    """Vue d'ensemble du projet : une ligne par voix / effet / écho / musique."""
    if not rows or total <= 0:
        return
    W, rh, gap = 600, 22, 4
    H = len(rows) * (rh + gap) + gap
    parts = []
    for r, (label, s, e, kind) in enumerate(rows):
        x, w = s / total * W, max(4.0, (e - s) / total * W)
        y = r * (rh + gap) + gap
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{rh}" rx="6" '
                     f'fill="{_TL_COLORS.get(kind, "#8EA0BC")}" opacity=".88"/>'
                     f'<text x="{x + 7:.1f}" y="{y + 15}" font-size="11" font-weight="600" fill="#04101c">'
                     f'{html.escape(str(label))}</text>')
    st.markdown(f'<div class="oxy-wave"><svg viewBox="0 0 {W} {H}" style="width:100%">{"".join(parts)}</svg></div>',
                unsafe_allow_html=True)


def brand() -> None:
    st.markdown(
        f'<div class="oxy-brand">{_LOGO}<div><div class="oxy-brand-name">Oxygène</div>'
        '<div class="oxy-brand-sub">JINGLE STUDIO</div></div></div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        '<div class="oxy-foot">Voix neurales gratuites · mastering Pedalboard<br>'
        "Tes créations restent en session : pense à les télécharger.</div>",
        unsafe_allow_html=True,
    )
