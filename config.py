"""Configuration centrale : nom de l'app et catalogue de voix (gratuites, neurales)."""

APP_NAME = "Oxygène Jingle"
APP_ICON = "🫧"
TAGLINE = "Studio de jingles & voix off pour DJs"

# (libellé affiché, identifiant edge-tts, genre H/F)
VOICE_INFO = [
    ("🇫🇷 Henri — homme, chaleureux", "fr-FR-HenriNeural", "H"),
    ("🇫🇷 Denise — femme, claire", "fr-FR-DeniseNeural", "F"),
    ("🇫🇷 Rémy — homme, multilingue", "fr-FR-RemyMultilingualNeural", "H"),
    ("🇫🇷 Vivienne — femme, multilingue", "fr-FR-VivienneMultilingualNeural", "F"),
    ("🇫🇷 Éloïse — jeune", "fr-FR-EloiseNeural", "F"),
    ("🇧🇪 Gérard — homme", "fr-BE-GerardNeural", "H"),
    ("🇧🇪 Charline — femme", "fr-BE-CharlineNeural", "F"),
    ("🇨🇦 Antoine — homme", "fr-CA-AntoineNeural", "H"),
    ("🇨🇦 Jean — homme", "fr-CA-JeanNeural", "H"),
    ("🇨🇦 Thierry — homme", "fr-CA-ThierryNeural", "H"),
    ("🇨🇦 Sylvie — femme", "fr-CA-SylvieNeural", "F"),
    ("🇨🇭 Fabrice — homme", "fr-CH-FabriceNeural", "H"),
    ("🇨🇭 Ariane — femme", "fr-CH-ArianeNeural", "F"),
    ("🇺🇸 Guy — voix annonceur", "en-US-GuyNeural", "H"),
    ("🇺🇸 Christopher — grave", "en-US-ChristopherNeural", "H"),
    ("🇺🇸 Davis — posé", "en-US-DavisNeural", "H"),
    ("🇺🇸 Jason — énergique", "en-US-JasonNeural", "H"),
    ("🇺🇸 Tony — dynamique", "en-US-TonyNeural", "H"),
    ("🇺🇸 Eric — net", "en-US-EricNeural", "H"),
    ("🇺🇸 Roger — mûr", "en-US-RogerNeural", "H"),
    ("🇺🇸 Andrew — multilingue", "en-US-AndrewMultilingualNeural", "H"),
    ("🇺🇸 Brian — multilingue", "en-US-BrianMultilingualNeural", "H"),
    ("🇺🇸 Aria — femme", "en-US-AriaNeural", "F"),
    ("🇺🇸 Jenny — femme", "en-US-JennyNeural", "F"),
    ("🇺🇸 Ava — multilingue", "en-US-AvaMultilingualNeural", "F"),
    ("🇺🇸 Emma — multilingue", "en-US-EmmaMultilingualNeural", "F"),
    ("🇬🇧 Ryan — homme", "en-GB-RyanNeural", "H"),
    ("🇬🇧 Thomas — homme", "en-GB-ThomasNeural", "H"),
    ("🇬🇧 Sonia — femme", "en-GB-SoniaNeural", "F"),
    ("🇪🇸 Álvaro — homme", "es-ES-AlvaroNeural", "H"),
    ("🇪🇸 Elvira — femme", "es-ES-ElviraNeural", "F"),
    ("🇮🇹 Diego — homme", "it-IT-DiegoNeural", "H"),
    ("🇮🇹 Elsa — femme", "it-IT-ElsaNeural", "F"),
    ("🇩🇪 Conrad — homme", "de-DE-ConradNeural", "H"),
    ("🇩🇪 Katja — femme", "de-DE-KatjaNeural", "F"),
    ("🇧🇷 Antônio — homme", "pt-BR-AntonioNeural", "H"),
    ("🇧🇷 Francisca — femme", "pt-BR-FranciscaNeural", "F"),
]

VOICES = {label: vid for label, vid, _ in VOICE_INFO}                    # libellé -> identifiant
VOICE_LABELS = {vid: label for label, vid, _ in VOICE_INFO}              # identifiant -> libellé
VOICE_META = {label: {"id": vid, "lang": vid.split("-")[0], "gender": g} for label, vid, g in VOICE_INFO}
LANGS = {"fr": "Français", "en": "Anglais", "es": "Espagnol", "it": "Italien", "de": "Allemand", "pt": "Portugais"}
