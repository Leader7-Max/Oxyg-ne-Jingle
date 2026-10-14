"""Page Studio : voix superposables (synthèse ou clips), nappe, effets DJ, écho début/fin, mastering."""
import streamlit as st

import theme
from config import VOICES
from engine import audio, beds, layers, master, mixer, sfx, store, voices

VOICE_LIST = list(VOICES)
PLACEMENTS = ["En même temps", "Après la précédente"]
SFX_POS = ["Au début", "Avant la voix", "Après la voix", "À t secondes"]
LUFS = {"-16 LUFS · vidéo / podcast": -16.0, "-14 LUFS · streaming / radio": -14.0,
        "-11 LUFS · club / festival": -11.0}
NONE = "(aucun)"
MAX_VOICES = 6

HENRI, DENISE = "🇫🇷 Henri — homme, chaleureux", "🇫🇷 Denise — femme, claire"
REMY, VIV, GUY = "🇫🇷 Rémy — homme, multilingue", "🇫🇷 Vivienne — femme, multilingue", "🇺🇸 Guy — voix annonceur"


def _t(text, voice, preset, thick="Aucune", level=0.0, pan=0.0, place="En même temps",
       offset=0.0, repeat=1, bg=False):
    return dict(text=text, voice=voice, preset=preset, thick=thick, level=level, pan=pan,
                place=place, offset=offset, repeat=repeat, bg=bg)


def _e(on, dur=1.5, ms=375, fb=0.45, db=-6.0, tone=5000, pp=True):
    return dict(on=on, dur=dur, ms=ms, fb=fb, db=db, tone=tone, pp=pp)


DEFAULT_TRACK = _t("Nouvelle voix superposée.", HENRI, "Studio Pro — voix off", level=-3.0)

TEMPLATES = {
    "🎧 Jingle DJ / Radio": dict(
        tracks=[_t("Oxygène Jingle !\nLa radio qui vous fait respirer la musique.", HENRI, "DJ Club Drop", "Double voix"),
                _t("Oxygène", GUY, "Voix de fond — nappe", "Chœur 3 voix", level=-9.0, offset=0.6, repeat=2, bg=True)],
        music=dict(src="Générée", style="House", bpm=124, key="A"), music_db=-7.0, duck_db=-10.0,
        lufs=-14.0, lead_in=1.8, tail=1.5, fade_out=1.2, echo_in=_e(False, 1.0), echo_out=_e(True, 1.6),
        sfx=[("🎛️ Scratch — wiki wiki", "Au début", 0.0, -4.0), ("📯 Airhorn DJ", "Après la voix", 0.0, -7.0)]),
    "🎬 Voix off vidéo événement": dict(
        tracks=[_t("Bienvenue à la grande soirée Oxygène. Une nuit, une énergie, une seule destination.",
                   REMY, "Voix off événement / Trailer", "Double + octave grave"),
                _t("Oxygène", VIV, "Chuchotement fantôme", level=-10.0, offset=2.0, bg=True)],
        music=dict(src="Générée", style="Cinématique", bpm=70, key="D"), music_db=-9.0, duck_db=-12.0,
        lufs=-16.0, lead_in=2.0, tail=2.5, fade_out=2.5, echo_in=_e(True, 0.8, 450, 0.4, -9.0),
        echo_out=_e(True, 1.2, 500, 0.5, -6.0),
        sfx=[("🌬️ Reverse swell", "Avant la voix", 0.0, -8.0), ("🔊 Sub drop", "Après la voix", 0.0, -4.0)]),
    "📣 Annonce soirée / festival": dict(
        tracks=[_t("Attention, attention ! Ce samedi, Oxygène vous invite à la plus grosse soirée de l'année !",
                   HENRI, "Stade / Arena", "Double voix"),
                _t("Entrée gratuite avant minuit. Réservez vos places dès maintenant !", DENISE,
                   "Studio Pro — voix off", place="Après la précédente", offset=0.3),
                _t("Oxygène ! Oxygène !", GUY, "Voix de fond — nappe", "Chœur 3 voix", level=-9.0, offset=0.5, bg=True)],
        music=dict(src="Générée", style="Techno", bpm=130, key="F"), music_db=-8.0, duck_db=-11.0,
        lufs=-11.0, lead_in=2.0, tail=1.5, fade_out=1.2, echo_in=_e(False), echo_out=_e(True, 1.4, 300, 0.5, -6.0),
        sfx=[("🚨 Sirène — wail", "Au début", 0.0, -9.0), ("📈 Riser", "Avant la voix", 0.0, -8.0),
             ("📯 Airhorn DJ", "Après la voix", 0.0, -6.0)]),
    "✨ Stinger court": dict(
        tracks=[_t("Oxygène !", HENRI, "DJ Club Drop", "Double voix"),
                _t("Oxygène", GUY, "Voix de fond — nappe", "Chœur 3 voix", level=-8.0, offset=0.15, bg=True)],
        music=dict(src="Générée", style="Hip-Hop", bpm=90, key="C"), music_db=-8.0, duck_db=-9.0,
        lufs=-14.0, lead_in=0.6, tail=1.0, fade_out=0.8, echo_in=_e(False), echo_out=_e(True, 0.8, 300, 0.5, -5.0),
        sfx=[("🎛️ Scratch — long", "Au début", 0.0, -4.0), ("💥 Impact", "Après la voix", 0.0, -5.0)]),
    "🛠️ Personnalisé": dict(
        tracks=[_t("Votre texte ici.", HENRI, "Studio Pro — voix off")],
        music=dict(src="Générée", style="Pop / Dance", bpm=118, key="C"), music_db=-8.0, duck_db=-10.0,
        lufs=-14.0, lead_in=1.5, tail=1.5, fade_out=1.0, echo_in=_e(False), echo_out=_e(False), sfx=[]),
}


def _idx(label):
    return VOICE_LIST.index(label) if label in VOICE_LIST else 0


def _track_ui(i, d, k):
    from views.components import fx_panel

    clips = store.clips()
    source = "Texte"
    if clips:
        source = st.radio("Source de la voix", ["Texte", "Clip du Labo voix"], horizontal=True, key=k(f"t{i}src"))
    text, voice, repeat, clip_id = "", VOICE_LIST[0], 1, None
    if source == "Texte":
        text = st.text_area("Texte", d["text"], height=96, key=k(f"t{i}txt"),
                            help="Une ligne = une phrase. [pause 1] ajoute 1 s de silence.")
        voice = st.selectbox("Voix", VOICE_LIST, index=_idx(d["voice"]), key=k(f"t{i}v"))
        repeat = st.slider("Répétitions du texte", 1, 4, int(d["repeat"]), key=k(f"t{i}rp"))
    else:
        clip_id = st.selectbox("Clip", [c["id"] for c in clips], key=k(f"t{i}clip"),
                               format_func=lambda cid: f"{store.get_clip(cid)['name']} · {store.get_clip(cid)['seconds']:.1f} s")
    c1, c2 = st.columns(2)
    level = c1.slider("Niveau (dB)", -24.0, 6.0, float(d["level"]), 0.5, key=k(f"t{i}lv"))
    pan = c2.slider("Panoramique", -1.0, 1.0, float(d["pan"]), 0.1, key=k(f"t{i}pn"))
    thick = st.selectbox("Épaisseur de voix", layers.MODES, index=layers.MODES.index(d["thick"]), key=k(f"t{i}th"))
    place = "En même temps"
    if i > 0:
        place = st.selectbox("Placement", PLACEMENTS, index=PLACEMENTS.index(d["place"]), key=k(f"t{i}pl"),
                             help="« En même temps » superpose cette voix à la précédente.")
    offset = st.slider("Décalage de départ (s)", 0.0, 15.0, float(d["offset"]), 0.1, key=k(f"t{i}of"))
    bg = st.checkbox("Voix d'arrière-plan (ne fait pas baisser la musique)", value=bool(d["bg"]), key=k(f"t{i}bg"))
    with st.expander("Synthèse & effets avancés"):
        c1, c2, c3 = st.columns(3)
        rate = c1.slider("Vitesse %", -50, 100, 0, 5, key=k(f"t{i}ra"))
        pitch = c2.slider("Hauteur Hz", -50, 50, 0, 5, key=k(f"t{i}pi"))
        vol = c3.slider("Volume %", -50, 50, 0, 5, key=k(f"t{i}vo"))
        params = fx_panel(k(f"t{i}fx"), d["preset"])
    return dict(source=source, clip_id=clip_id, text=text, voice=voice, rate=rate, pitch=pitch, vol=vol,
                params=params, level=level, pan=pan, thick=thick, place=place, offset=offset,
                repeat=repeat, bg=bg)


def _echo_ui(title, d, k, tag):
    with st.expander(title, expanded=d["on"]):
        if not st.toggle("Activer", value=d["on"], key=k(f"{tag}on")):
            return None
        c1, c2 = st.columns(2)
        dur = c1.slider("Zone d'écho (s)", 0.3, 6.0, float(d["dur"]), 0.1, key=k(f"{tag}du"),
                        help="Durée de voix qui reçoit l'écho (début ou fin du jingle).")
        ms = c2.slider("Délai (ms)", 60, 1000, int(d["ms"]), 10, key=k(f"{tag}ms"))
        c1, c2 = st.columns(2)
        fb = c1.slider("Répétitions", 0.1, 0.85, float(d["fb"]), 0.05, key=k(f"{tag}fb"))
        db = c2.slider("Niveau (dB)", -24.0, 0.0, float(d["db"]), 0.5, key=k(f"{tag}db"))
        tone = st.slider("Ton des répétitions (Hz)", 1500, 12000, int(d["tone"]), 100, key=k(f"{tag}tn"))
        pp = st.checkbox("Ping-pong (gauche / droite)", value=bool(d["pp"]), key=k(f"{tag}pp"))
        return dict(dur=dur, ms=ms, fb=fb, db=db, tone=tone, pp=pp)


def render() -> None:
    from views.components import player

    theme.header("Studio de production",
                 "Voix superposées, effets complets, écho début/fin, nappe, effets DJ et mastering.",
                 ["Voix superposées", "Écho début / fin", "Clips enregistrés", "Stems"])

    theme.section("Projet", 1)
    tpl = st.selectbox("Modèle de départ", list(TEMPLATES), key="studio_tpl")
    T, ti = TEMPLATES[tpl], list(TEMPLATES).index(tpl)

    def k(n):
        return f"s{ti}_{n}"

    theme.section("Voix superposées", 2)
    n = st.slider("Nombre de voix", 1, MAX_VOICES, len(T["tracks"]), key=k("ntr"),
                  help="Chaque voix a son texte (ou clip), ses effets, son placement : superpose-les librement.")
    cfgs = []
    for i, tab in enumerate(st.tabs([f"🎙️ Voix {j + 1}" for j in range(n)])):
        with tab:
            cfgs.append(_track_ui(i, T["tracks"][i] if i < len(T["tracks"]) else DEFAULT_TRACK, k))

    theme.section("Écho de début & de fin", 3)
    echo_in = _echo_ui("🔊 Écho sur le début du jingle", T["echo_in"], k, "ei")
    echo_out = _echo_ui("🔊 Écho sur la fin du jingle", T["echo_out"], k, "eo")

    theme.section("Nappe musicale", 4)
    M = T["music"]
    srcs = ["Générée", "Importer", "Aucune"]
    src = st.radio("Source", srcs, horizontal=True, index=srcs.index(M["src"]), key=k("msrc"))
    gen, upload, music_db, duck_db = None, None, T["music_db"], T["duck_db"]
    if src == "Générée":
        c1, c2 = st.columns(2)
        styles = list(beds.STYLES)
        style = c1.selectbox("Style", styles, index=styles.index(M["style"]), key=k("mst"))
        note = c2.selectbox("Tonalité", beds.NOTES, index=beds.NOTES.index(M["key"]), key=k("mkey"))
        bpm_def = M["bpm"] if style == M["style"] else beds.STYLES[style]["bpm"]
        bpm = st.slider("Tempo (BPM)", 60, 150, int(bpm_def), key=k(f"mbpm_{style}"))
        e1, e2, e3 = st.columns(3)
        drums = e1.checkbox("Rythmique", True, key=k("md"))
        bass = e2.checkbox("Basse", True, key=k("mb"))
        pad = e3.checkbox("Accords", True, key=k("mp"))
        gen = (style, bpm, note, drums, bass, pad)
    elif src == "Importer":
        upload = st.file_uploader("Musique (wav, mp3, flac, ogg)", type=["wav", "mp3", "flac", "ogg"], key=k("mup"))
    if src != "Aucune":
        c1, c2 = st.columns(2)
        music_db = c1.slider("Niveau musique (dB)", -30.0, 0.0, float(T["music_db"]), 1.0, key=k("mdb"))
        duck_db = c2.slider("Ducking sous la voix (dB)", -30.0, 0.0, float(T["duck_db"]), 1.0, key=k("mdk"))

    theme.section("Effets DJ", 5)
    labels = [NONE] + list(sfx.EFFECTS)
    events = []
    for j in range(4):
        d = T["sfx"][j] if j < len(T["sfx"]) else (NONE, "Au début", 0.0, -4.0)
        with st.expander(f"Effet {j + 1}" + (f" · {d[0]}" if d[0] != NONE else "")):
            lab = st.selectbox("Effet", labels, index=labels.index(d[0]), key=k(f"fx{j}l"))
            c1, c2 = st.columns(2)
            mode = c1.selectbox("Placement", SFX_POS, index=SFX_POS.index(d[1]), key=k(f"fx{j}m"))
            db = c2.slider("Niveau (dB)", -24.0, 6.0, float(d[3]), 0.5, key=k(f"fx{j}d"))
            t = st.slider("À t = (s)", 0.0, 30.0, float(d[2]), 0.1, key=k(f"fx{j}t")) if mode == "À t secondes" else 0.0
            if lab != NONE:
                events.append(dict(label=lab, mode=mode, t=t, db=db))

    theme.section("Mastering & export", 6)
    lab_l = next(l for l, v in LUFS.items() if v == T["lufs"])
    c1, c2 = st.columns(2)
    target = LUFS[c1.selectbox("Loudness cible", list(LUFS), index=list(LUFS).index(lab_l), key=k("lufs"))]
    ceiling = c2.slider("Plafond crête (dBFS)", -3.0, -0.1, -1.0, 0.1, key=k("ceil"))
    c1, c2, c3 = st.columns(3)
    lead_in = c1.slider("Avant la voix (s)", 0.0, 6.0, float(T["lead_in"]), 0.1, key=k("lead"))
    tail = c2.slider("Après la voix (s)", 0.0, 6.0, float(T["tail"]), 0.1, key=k("tail"))
    fade_out = c3.slider("Fondu musique (s)", 0.0, 6.0, float(T["fade_out"]), 0.1, key=k("fo"))
    c1, c2 = st.columns(2)
    glue = c1.checkbox("Compression de bus (glue)", True, key=k("glue"))
    air = c2.checkbox("Brillance « air »", True, key=k("air"))
    stems_on = st.checkbox("Exporter les pistes séparées (stems)", True, key=k("stems"))
    name = st.text_input("Nom du fichier", "oxygene-jingle", key=k("name"))

    if st.button("✨ Produire le jingle", type="primary", use_container_width=True):
        ok = cfgs[0]["clip_id"] or cfgs[0]["text"].strip()
        if not ok:
            st.warning("Écris le texte de la voix 1 (ou choisis un clip).")
        else:
            _produce(cfgs, gen, upload, music_db, duck_db, events, echo_in, echo_out, dict(
                lead_in=lead_in, tail=tail, fade_out=fade_out, target=target, ceiling=ceiling,
                glue=glue, air=air, stems=stems_on, name=name))

    item = st.session_state.get("last_jingle")
    if item:
        theme.section(f"Résultat · {item['name']}")
        player(item, "last")


def _produce(cfgs, gen, upload, music_db, duck_db, events, echo_in, echo_out, o) -> None:
    with st.status("Production en cours…", expanded=True) as status:
        try:
            tracks = []
            for i, c in enumerate(cfgs):
                clip = store.get_clip(c["clip_id"]) if c["clip_id"] else None
                if clip is None and not c["text"].strip():
                    continue
                label = f"Voix {i + 1}" + (f" · {clip['name']}" if clip else "")
                st.write(f"🎙️ {label} : {'clip' if clip else 'synthèse'}, effets, épaisseur")
                cfg = {**c, "clip": clip["audio"] if clip else None}
                tracks.append(dict(name=f"voix_{i + 1}", label=label, audio=voices.build_voice(cfg, c["bg"]),
                                   place=c["place"], offset=c["offset"], bg=c["bg"]))
            st.write("🥁 Nappe & effets DJ")
            music = None
            if gen:
                style, bpm, note, drums, bass, pad = gen
                music = lambda secs: beds.render(style, bpm, note, secs, drums, bass, pad)  # noqa: E731
            elif upload is not None:
                music = audio.decode(upload.getvalue())
            ev = [dict(label=e["label"], audio=sfx.get(e["label"]), mode=e["mode"], t=e["t"], db=e["db"])
                  for e in events]
            st.write("🎛️ Mixage, ducking & échos")
            final, stems, layout = mixer.build_project(tracks, music, music_db, duck_db, True, ev,
                                                       o["lead_in"], o["tail"], o["fade_out"], echo_in, echo_out)
            st.write("🎚️ Mastering")
            final = master.master(final, o["target"], o["ceiling"], o["glue"], o["air"])
            st.session_state["last_jingle"] = store.add(o["name"], final, stems if o["stems"] else None, layout)
            status.update(label="Jingle prêt ✅", state="complete", expanded=False)
        except Exception as e:  # noqa: BLE001
            status.update(label="Échec de la production", state="error")
            st.error(f"Production impossible : {e}")
