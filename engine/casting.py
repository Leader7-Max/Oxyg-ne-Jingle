"""Voix de caractère : voix + vitesse + hauteur + effets + épaisseur réglés pour un style précis."""
from config import VOICE_LABELS


def _l(vid: str) -> str:
    return VOICE_LABELS[vid]


HENRI, DENISE = _l("fr-FR-HenriNeural"), _l("fr-FR-DeniseNeural")
REMY, VIV, ELO = _l("fr-FR-RemyMultilingualNeural"), _l("fr-FR-VivienneMultilingualNeural"), _l("fr-FR-EloiseNeural")
GUY, CHRIS = _l("en-US-GuyNeural"), _l("en-US-ChristopherNeural")

CHARACTERS = {
    "🔥 Gras & puissant": dict(
        desc="Grosse voix grave, ronde et chaude : le son « radio / club » qui impose le respect.",
        voice=HENRI, rate=-6, pitch=-22, vol=8, preset="Voix grasse", thick="Double + octave grave",
        level=0.0, style="Annonceur événement"),
    "😈 Agressif / Hard": dict(
        desc="Voix tendue, rapide et saturée. Pour les soirées hard, trap ou techno.",
        voice=HENRI, rate=12, pitch=-10, vol=18, preset="Voix agressive", thick="Double voix",
        level=0.0, style="Radio dynamique"),
    "👹 Boss final / Démon": dict(
        desc="Voix monstrueuse, très grave, avec écho. Pour les intros dramatiques.",
        voice=HENRI, rate=-14, pitch=-35, vol=10, preset="Démon / Boss final", thick="Double + octave grave",
        level=0.0, style="Annonceur événement"),
    "🎤 Hype Hip-Hop": dict(
        desc="Voix de MC : punchy, large, avec écho ping-pong.",
        voice=REMY, rate=8, pitch=-8, vol=12, preset="Hype Hip-Hop", thick="Double voix",
        level=0.0, style="Publicité punchy"),
    "🦁 Annonceur de stade": dict(
        desc="Grande salle, grande voix : l'annonce d'un concert ou d'un match.",
        voice=HENRI, rate=4, pitch=-12, vol=14, preset="Stade / Arena", thick="Double voix",
        level=0.0, style="Annonceur événement"),
    "🌙 Nuit radio — voix chaude": dict(
        desc="Voix douce et grave des radios de nuit : lente, enveloppante.",
        voice=HENRI, rate=-10, pitch=-14, vol=0, preset="Nuit radio — chaude", thick="Aucune",
        level=0.0, style="Narrateur littéraire"),
    "📻 Speaker FM énergique": dict(
        desc="Animatrice radio FM : claire, rapide, souriante.",
        voice=DENISE, rate=10, pitch=2, vol=8, preset="Annonceur radio FM", thick="Aucune",
        level=0.0, style="Radio dynamique"),
    "👑 Diva club": dict(
        desc="Voix féminine large et brillante, avec écho gauche/droite.",
        voice=VIV, rate=2, pitch=-2, vol=6, preset="Diva club", thick="Double voix",
        level=0.0, style="Annonceur événement"),
    "🎙️ Narrateur littéraire": dict(
        desc="Lecture posée de roman ou de documentaire : pauses longues, voix grave douce.",
        voice=REMY, rate=-8, pitch=-6, vol=0, preset="Narrateur littéraire", thick="Aucune",
        level=0.0, style="Narrateur littéraire"),
    "📰 Journaliste info": dict(
        desc="Ton neutre et net de journal radio.",
        voice=DENISE, rate=6, pitch=0, vol=4, preset="Studio Pro — voix off", thick="Aucune",
        level=0.0, style="Journal / information"),
    "🛍️ Pub punchy": dict(
        desc="Voix jeune et rapide pour une publicité dynamique.",
        voice=ELO, rate=14, pitch=3, vol=10, preset="Annonceur radio FM", thick="Aucune",
        level=0.0, style="Publicité punchy"),
    "🇺🇸 US Big Voice (EN)": dict(
        desc="Grosse voix américaine de bande-annonce (pour du texte en anglais).",
        voice=CHRIS, rate=-4, pitch=-15, vol=10, preset="Voix grasse", thick="Double + octave grave",
        level=0.0, style="Annonceur événement"),
    "🇺🇸 US Hype DJ (EN)": dict(
        desc="Annonceur de club américain, très énergique (texte en anglais).",
        voice=GUY, rate=10, pitch=-5, vol=14, preset="Hype Hip-Hop", thick="Double voix",
        level=0.0, style="Publicité punchy"),
    "🤖 Robot club": dict(
        desc="Voix de robot métallique, parfaite pour un drop électro.",
        voice=REMY, rate=0, pitch=-4, vol=0, preset="Robot", thick="Aucune",
        level=0.0, style="Naturel"),
}
