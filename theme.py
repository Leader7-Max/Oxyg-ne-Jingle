"""Thème visuel Oxygène : couleurs, CSS et petits composants d'interface."""
import streamlit as st
from config import APP_NAME, TAGLINE

COLORS = {
    "bg": "#0B1220",
    "panel": "#121B2E",
    "panel2": "#18243B",
    "text": "#E6EEF8",
    "muted": "#8EA0BC",
    "cyan": "#22D3EE",
    "indigo": "#6366F1",
    "pink": "#F472B6",
}

_CSS = """
<style>
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #14305a55, transparent),
                    radial-gradient(900px 500px at 100% 0%, #3b2a7a44, transparent), __bg__; }
section[data-testid="stSidebar"] { background: __panel__; border-right: 1px solid #ffffff12; }
h1, h2, h3 { letter-spacing: -0.02em; }

.oxy-hero { padding: 18px 20px; border-radius: 18px; margin-bottom: 14px;
  background: linear-gradient(135deg, #22d3ee22, #6366f122 60%, #f472b622);
  border: 1px solid #ffffff18; }
.oxy-hero h1 { margin: 0; font-size: 1.7rem; padding: 0;
  background: linear-gradient(90deg, __cyan__, __indigo__, __pink__);
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.oxy-hero p { margin: 4px 0 0; color: __muted__; font-size: .95rem; }

.oxy-eq { height: 26px; margin-bottom: 8px; }
.oxy-eq span { display: inline-block; width: 5px; height: 100%; margin-right: 3px;
  border-radius: 3px; transform-origin: bottom;
  background: linear-gradient(to top, __cyan__, __indigo__);
  animation: oxy-bounce 1.1s ease-in-out infinite; }
.oxy-eq span:nth-child(2){animation-delay:.12s} .oxy-eq span:nth-child(3){animation-delay:.28s}
.oxy-eq span:nth-child(4){animation-delay:.05s} .oxy-eq span:nth-child(5){animation-delay:.4s}
.oxy-eq span:nth-child(6){animation-delay:.2s}  .oxy-eq span:nth-child(7){animation-delay:.33s}
@keyframes oxy-bounce { 0%,100%{transform:scaleY(.25)} 50%{transform:scaleY(1)} }

.oxy-section { display:flex; align-items:center; gap:8px; margin: 18px 0 6px;
  font-weight: 700; font-size: 1.05rem; color: __text__; }
.oxy-section::before { content:""; width:4px; height:18px; border-radius:2px;
  background: linear-gradient(__cyan__, __indigo__); }

.stButton > button[kind="primary"], .stDownloadButton > button {
  border-radius: 12px; border: 0; font-weight: 600; }
.stButton > button[kind="primary"] {
  background: linear-gradient(90deg, __cyan__, __indigo__); color: #04101c; }
div[data-testid="stExpander"] { border: 1px solid #ffffff14; border-radius: 14px;
  background: __panel__; }
.oxy-foot { color: __muted__; font-size: .78rem; margin-top: 24px; }
</style>
"""


def apply() -> None:
    css = _CSS
    for k, v in COLORS.items():
        css = css.replace(f"__{k}__", v)
    st.markdown(css, unsafe_allow_html=True)


def header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="oxy-hero"><div class="oxy-eq">{"<span></span>" * 7}</div>'
        f"<h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def section(text: str) -> None:
    st.markdown(f'<div class="oxy-section">{text}</div>', unsafe_allow_html=True)


def brand() -> None:
    st.markdown(f"### 🫧 {APP_NAME}")
    st.caption(TAGLINE)


def footer() -> None:
    st.markdown(
        '<div class="oxy-foot">Voix neurales gratuites · effets Pedalboard<br>'
        "Les créations restent en session : télécharge-les !</div>",
        unsafe_allow_html=True,
    )
