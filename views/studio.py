"""Page Studio jingle, organisée en onglets : projet, voix, effets & sons, écho, musique, mixage & export."""
import streamlit as st

import theme
from engine import audio, beds, fx, layers, master, mixer, reader, sfx, store, voices
from engine.casting import DENISE, GUY, HENRI, REMY, VIV
from views.components import fx_panel, import_box, player, voice_picker
from views.helptexts import h

PLACEMENTS = ["En même temps", "Après la précédente"]
SFX_POS = ["Au début", "Avant la voix", "Après la voix", "À t secondes"]
LUFS = {"-16 LUFS · vidéo / podcast": -16.0, "-14 LUFS · streaming / radio": -14.0,
        "-11 LUFS · club / festival": -11.0}
NONE = "(aucun)"
MAX_VOICES, MAX_SFX = 6, 8


def _t(text, voice, preset, thick="Aucune", level=0.0, pan=0.0, place="En même temps",
       offset=0.0, repeat=1, bg=False, char=None):
    return dict(text=text, voice=voice, preset=preset, thick=thick, level=level, pan=pan,
                place=place, offset=offset, repeat=repeat, bg=bg, char=char)


def _e(on, dur=1.5, ms=375, fb=0.45, db=-6.0, tone=5000, pp=True):
    return dict(on=on, dur=dur, ms=ms, fb=fb, db=db, tone=tone, pp=pp)


DEFAULT_TRACK = _t("Nouvelle voix superposée.", HENRI, "Studio Pro — voix off", level=-3.0)
BG = ("Voix de fond — nappe", "Chœur 3 voix")

TEMPLATES = {
    "🎧 Jingle DJ / Radio": dict(
        tracks=[_t("Oxygène Jingle !\nLa radio qui vous fait respirer la musique.", HENRI, "DJ Club Drop", char="🔥 Gras & puissant"),
                _t("Oxygène", GUY, BG[0], BG[1], level=-9.0, offset=0.6, repeat=2, bg=True)],
        music=dict(src="Générée", style="House", bpm=124, key="A"), music_db=-7.0, duck_db=-10.0,
        lufs=-14.0, lead_in=1.8, tail=1.5, fade_out=1.2, echo_in=_e(False, 1.0), echo_out=_e(True, 1.6),
        sfx=[("🎛️ Scratch — wiki wiki", "Au début", 0.0, -4.0), ("📯 Airhorn DJ", "Après la voix", 0.0, -7.0)]),
    "🎬 Voix off vidéo événement": dict(
        tracks=[_t("Bienvenue à la grande soirée Oxygène. Une nuit, une énergie, une seule destination.",
                   REMY, "Voix off événement / Trailer", char="🔥 Gras & puissant"),
                _t("Oxygène", VIV, "Chuchotement fantôme", level=-10.0, offset=2.0, bg=True)],
        music=dict(src="Générée", style="Cinématique", bpm=70, key="D"), music_db=-9.0, duck_db=-12.0,
        lufs=-16.0, lead_in=2.0, tail=2.5, fade_out=2.5, echo_in=_e(True, 0.8, 450, 0.4, -9.0),
        echo_out=_e(True, 1.2, 500, 0.5, -6.0),
        sfx=[("🌬️ Reverse swell", "Avant la voix", 0.0, -8.0), ("🔊 Sub drop", "Après la voix", 0.0, -4.0)]),
    "📣 Annonce soirée / festival": dict(
        tracks=[_t("Attention, attention ! Ce samedi, Oxygène vous invite à la plus grosse soirée de l'année !",
                   HENRI, "Stade / Arena", char="🦁 Annonceur de stade"),
                _t("Entrée gratuite avant minuit. Réservez vos places dès maintenant !", DENISE,
                   "Studio Pro — voix off", place="Après la précédente", offset=0.3, char="📻 Speaker FM énergique"),
                _t("Oxygène ! Oxygène !", GUY, BG[0], BG[1], level=-9.0, offset=0.5, bg=True)],
        music=dict(src="Générée", style="Techno", bpm=130, key="F"), music_db=-8.0, duck_db=-11.0,
        lufs=-11.0, lead_in=2.0, tail=1.5, fade_out=1.2, echo_in=_e(False), echo_out=_e(True, 1.4, 300, 0.5, -6.0),
        sfx=[("🚨 Sirène — wail", "Au début", 0.0, -9.0), ("📈 Riser", "Avant la voix", 0.0, -8.0),
             ("📯 Airhorn DJ", "Après la voix", 0.0, -6.0)]),
    "✨ Stinger court": dict(
        tracks=[_t("Oxygène !", HENRI, "DJ Club Drop", char="😈 Agressif / Hard"),
                _t("Oxygène", GUY, BG[0], BG[1], level=-8.0, offset=0.15, bg=True)],
        music=dict(src="Générée", style="Hip-Hop", bpm=90, key="C"), music_db=-8.0, duck_db=-9.0,
        lufs=-14.0, lead_in=0.6, tail=1.0, fade_out=0.8, echo_in=_e(False), echo_out=_e(True, 0.8, 300, 0.5, -5.0),
        sfx=[("🎛️ Scratch — long", "Au début", 0.0, -4.0), ("💥 Impact", "Après la voix", 0.0, -5.0)]),
    "🛠️ Personnalisé": dict(
        tracks=[_t("Votre texte ici.", HENRI, "Studio Pro — voix off")],
        music=dict(src="Générée", style="Pop / Dance", bpm=118, key="C"), music_db=-8.0, duck_db=-10.0,
        lufs=-14.0, lead_in=1.5, tail=1.5, fade_out=1.0, echo_in=_e(False), echo_out=_e(False), sfx=[]),
}


def _track_ui(i, d, k):
    p = k(f"t{i}")
    with st.expander("➕ Importer une voix enregistrée"):
        import_box("voix", f"{p}_imp", "Fichier de voix (wav, mp3, flac, ogg)")
    medias = store.media("voix")
    use_media = False
    if medias:
        use_media = st.radio("Source", ["Texte (voix de synthèse)", "Voix importée"], horizontal=True,
                             key=f"{p}_src", help=h("source")) == "Voix importée"
    cfg = dict(media_id=None, text="", voice="", rate=0, pitch=0, vol=0, style="Naturel", pro=True, caps=False, repeat=1)
    if use_media:
        cfg["media_id"] = st.selectbox("Voix importée", [m["id"] for m in medias], key=f"{p}_media", help=h("media_voice"),
                                       format_func=lambda mid: f"{store.get_media(mid)['name']} · {store.get_media(mid)['seconds']:.1f} s")
        vp = dict(preset=d["preset"], thick=d["thick"], level=d["level"], sig="media")
    else:
        vp = voice_picker(p, d)
        cfg["voice"] = vp["voice"]
        cfg["text"] = st.text_area("Texte à dire", d["text"], height=130, key=f"{p}_txt_{vp['sig']}", help=h("text"))
        with st.expander("🎭 Lecture & intonation (style radio / littérature)"):
            styles = list(reader.STYLES)
            cfg["style"] = st.selectbox("Style de lecture", styles, index=styles.index(vp["style"]),
                                        key=f"{p}_sty_{vp['sig']}", help=h("style"))
            st.caption(reader.STYLE_HELP[cfg["style"]])
            cfg["pro"] = st.toggle("Lecture professionnelle (pauses & intonations)", value=True, key=f"{p}_pro", help=h("pro"))
            cfg["caps"] = st.toggle("Accentuer les MOTS EN MAJUSCULES", value=False, key=f"{p}_caps", help=h("caps"))
            cfg["repeat"] = st.slider("Répétitions du texte", 1, 4, int(d["repeat"]), key=f"{p}_rp", help=h("repeat"))
        cfg["rate"], cfg["pitch"], cfg["vol"] = vp["rate"], vp["pitch"], vp["vol"]
    sig = vp["sig"]
    c1, c2 = st.columns(2)
    level = c1.slider("Niveau (dB)", -24.0, 6.0, float(vp["level"]), 0.5, key=f"{p}_lv_{sig}", help=h("level"))
    pan = c2.slider("Panoramique", -1.0, 1.0, float(d["pan"]), 0.1, key=f"{p}_pn", help=h("pan"))
    thick = st.selectbox("Épaisseur de voix", layers.MODES, index=layers.MODES.index(vp["thick"]),
                         key=f"{p}_th_{sig}", help=h("thick"))
    place = "En même temps"
    if i > 0:
        place = st.selectbox("Placement", PLACEMENTS, index=PLACEMENTS.index(d["place"]), key=f"{p}_pl", help=h("place"))
    offset = st.slider("Décalage de départ (s)", 0.0, 15.0, float(d["offset"]), 0.1, key=f"{p}_of", help=h("offset"))
    bg = st.checkbox("Voix d'arrière-plan (ne fait pas baisser la musique)", value=bool(d["bg"]), key=f"{p}_bg", help=h("bg"))
    with st.expander("⚙️ Réglages avancés : vitesse, hauteur, effets"):
        if not use_media:
            c1, c2, c3 = st.columns(3)
            cfg["rate"] = c1.slider("Vitesse %", -50, 100, int(vp["rate"]), 1, key=f"{p}_ra_{sig}", help=h("rate"))
            cfg["pitch"] = c2.slider("Hauteur Hz", -50, 50, int(vp["pitch"]), 1, key=f"{p}_pi_{sig}", help=h("pitch"))
            cfg["vol"] = c3.slider("Volume %", -50, 50, int(vp["vol"]), 1, key=f"{p}_vo_{sig}", help=h("vol"))
        cfg["params"] = fx_panel(f"{p}_fx_{sig}", vp["preset"])
    if not use_media:
        with st.expander("🔍 Voir comment le texte sera lu", expanded=False):
            plan = reader.build_plan(cfg["text"], cfg["voice"], cfg["style"], cfg["rate"], cfg["pitch"],
                                     cfg["vol"], cfg["pro"], cfg["caps"])
            st.caption(h("plan"))
            if plan:
                st.dataframe(reader.describe(plan), hide_index=True, use_container_width=True)
    cfg.update(level=level, pan=pan, thick=thick, place=place, offset=offset, bg=bg)
    return cfg


def _echo_ui(title, d, k, tag):
    with st.expander(title, expanded=d["on"]):
        if not st.toggle("Activer", value=d["on"], key=k(f"{tag}on"), help=h("echo_on")):
            return None
        c1, c2 = st.columns(2)
        dur = c1.slider("Zone d'écho (s)", 0.3, 6.0, float(d["dur"]), 0.1, key=k(f"{tag}du"), help=h("echo_dur"))
        ms = c2.slider("Délai (ms)", 60, 1000, int(d["ms"]), 10, key=k(f"{tag}ms"), help=h("echo_ms2"))
        c1, c2 = st.columns(2)
        fb = c1.slider("Répétitions", 0.1, 0.85, float(d["fb"]), 0.05, key=k(f"{tag}fb"), help=h("echo_fb2"))
        db = c2.slider("Niveau (dB)", -24.0, 0.0, float(d["db"]), 0.5, key=k(f"{tag}db"), help=h("echo_db"))
        tone = st.slider("Ton des répétitions (Hz)", 1500, 12000, int(d["tone"]), 100, key=k(f"{tag}tn"), help=h("echo_tone"))
        pp = st.checkbox("Ping-pong (gauche / droite)", value=bool(d["pp"]), key=k(f"{tag}pp"), help=h("echo_pp2"))
        return dict(dur=dur, ms=ms, fb=fb, db=db, tone=tone, pp=pp)


def render() -> None:
    theme.header("Studio jingle", "Voix superposées, effets, écho, musique et mastering — étape par étape.",
                 ["Voix superposées", "Import de sons", "Écho début / fin", "Stems"])
    t_proj, t_voix, t_sfx, t_echo, t_mus, t_exp = st.tabs(
        ["① Projet", "② Voix", "③ Effets & sons", "④ Écho", "⑤ Musique", "⑥ Mixage & export"])

    with t_proj:
        st.info("**Comment ça marche ?** Choisis un modèle, règle tes voix (②), ajoute des sons (③) et de la musique (⑤), "
                "puis termine par l'onglet ⑥ pour produire ton jingle. Chaque réglage a une icône **?** qui t'explique à quoi il sert.")
        tpl = st.selectbox("Modèle de départ", list(TEMPLATES), key="studio_tpl", help=h("template"))
        T, ti = TEMPLATES[tpl], list(TEMPLATES).index(tpl)

    def k(n):
        return f"s{ti}_{n}"

    with t_voix:
        st.caption("Chaque voix a son texte (ou son enregistrement), son style et ses effets. Superpose-les librement.")
        n = st.slider("Nombre de voix", 1, MAX_VOICES, len(T["tracks"]), key=k("ntr"), help=h("ntr"))
        cfgs = []
        for i, tab in enumerate(st.tabs([f"🎙️ Voix {j + 1}" for j in range(n)])):
            with tab:
                cfgs.append(_track_ui(i, T["tracks"][i] if i < len(T["tracks"]) else DEFAULT_TRACK, k))

    with t_sfx:
        st.caption("Scratch, sirènes, impacts… ou tes propres sons importés : place-les sur la timeline.")
        with st.expander("➕ Importer mes propres effets sonores"):
            import_box("effet", k("imp_fx"), "Effets (wav, mp3, flac, ogg)")
        n_sfx = st.slider("Nombre de sons", 0, MAX_SFX, len(T["sfx"]), key=k("nsfx"), help=h("sfx_n"))
        events = _sfx_ui(n_sfx, T, k)

    with t_echo:
        st.caption("Ajoute un écho sur les premiers mots et/ou sur les derniers mots du jingle.")
        echo_in = _echo_ui("🔊 Écho sur le début du jingle", T["echo_in"], k, "ei")
        echo_out = _echo_ui("🔊 Écho sur la fin du jingle", T["echo_out"], k, "eo")

    with t_mus:
        gen, upload, music_db, duck_db = _music_ui(T, k)

    with t_exp:
        lab_l = next(lb for lb, v in LUFS.items() if v == T["lufs"])
        c1, c2 = st.columns(2)
        target = LUFS[c1.selectbox("Loudness cible", list(LUFS), index=list(LUFS).index(lab_l), key=k("lufs"), help=h("lufs"))]
        ceiling = c2.slider("Plafond crête (dBFS)", -3.0, -0.1, -1.0, 0.1, key=k("ceil"), help=h("ceiling"))
        c1, c2, c3 = st.columns(3)
        lead_in = c1.slider("Avant la voix (s)", 0.0, 6.0, float(T["lead_in"]), 0.1, key=k("lead"), help=h("lead"))
        tail = c2.slider("Après la voix (s)", 0.0, 6.0, float(T["tail"]), 0.1, key=k("tail"), help=h("tail"))
        fade_out = c3.slider("Fondu musique (s)", 0.0, 6.0, float(T["fade_out"]), 0.1, key=k("fo"), help=h("fade_out"))
        c1, c2 = st.columns(2)
        glue = c1.checkbox("Compression de bus (glue)", True, key=k("glue"), help=h("glue"))
        air = c2.checkbox("Brillance « air »", True, key=k("air"), help=h("air"))
        stems_on = st.checkbox("Exporter les pistes séparées (stems)", True, key=k("stems"), help=h("stems"))
        name = st.text_input("Nom du fichier", "oxygene-jingle", key=k("name"), help=h("name"))
        if st.button("✨ Produire le jingle", type="primary", use_container_width=True, help=h("produce")):
            if not (cfgs[0]["media_id"] or cfgs[0]["text"].strip()):
                st.warning("Écris le texte de la voix 1 (onglet ②) ou choisis une voix importée.")
            else:
                _produce(cfgs, gen, upload, music_db, duck_db, events, echo_in, echo_out, dict(
                    lead_in=lead_in, tail=tail, fade_out=fade_out, target=target, ceiling=ceiling,
                    glue=glue, air=air, stems=stems_on, name=name))
        item = st.session_state.get("last_jingle")
        if item:
            theme.section(f"Résultat · {item['name']}")
            player(item, "last")


def _sfx_ui(n_sfx, T, k):
    labels = [NONE] + list(sfx.EFFECTS)
    presets = list(fx.PRESETS)
    events = []
    for j in range(n_sfx):
        d = T["sfx"][j] if j < len(T["sfx"]) else (NONE, "Au début", 0.0, -4.0)
        with st.expander(f"Son {j + 1}" + (f" · {d[0]}" if d[0] != NONE else ""), expanded=j < 2):
            imported = store.media("effet")
            src = "Effet intégré"
            if imported:
                src = st.radio("Source", ["Effet intégré", "Effet importé"], horizontal=True, key=k(f"sx{j}s"), help=h("sfx_src"))
            ev = dict(label=None, audio=None)
            if src == "Effet intégré":
                lab = st.selectbox("Effet", labels, index=labels.index(d[0]), key=k(f"sx{j}l"), help=h("sfx_label"))
                if lab != NONE:
                    ev = dict(label=lab, audio=sfx.get(lab))
            else:
                mid = st.selectbox("Effet importé", [m["id"] for m in imported], key=k(f"sx{j}m"), help=h("sfx_media"),
                                   format_func=lambda x: f"{store.get_media(x)['name']} · {store.get_media(x)['seconds']:.1f} s")
                m = store.get_media(mid)
                a = m["audio"]
                c1, c2 = st.columns(2)
                pr = c1.selectbox("Retouche (preset)", presets, key=k(f"sx{j}pr"), help=h("sfx_preset"))
                ps = c2.slider("Hauteur (demi-tons)", -12.0, 12.0, 0.0, 0.5, key=k(f"sx{j}ps"), help=h("sfx_pitch"))
                if pr != "Naturel" or ps:
                    a = audio.normalize(fx.process(a, {**fx.PRESETS[pr], "pitch_st": ps + fx.PRESETS[pr].get("pitch_st", 0.0)}), -3.0)
                ev = dict(label=f"📥 {m['name']}", audio=a)
            c1, c2 = st.columns(2)
            mode = c1.selectbox("Placement", SFX_POS, index=SFX_POS.index(d[1]), key=k(f"sx{j}p"), help=h("sfx_mode"))
            db = c2.slider("Niveau (dB)", -24.0, 6.0, float(d[3]), 0.5, key=k(f"sx{j}d"), help=h("sfx_db"))
            t = st.slider("À t = (s)", 0.0, 30.0, float(d[2]), 0.1, key=k(f"sx{j}t"), help=h("sfx_t")) if mode == "À t secondes" else 0.0
            if ev["audio"] is not None:
                events.append(dict(ev, mode=mode, t=t, db=db))
    return events


def _music_ui(T, k):
    M = T["music"]
    srcs = ["Générée", "Médiathèque", "Aucune"]
    src = st.radio("Source de la musique", srcs, horizontal=True, index=srcs.index(M["src"]), key=k("msrc"), help=h("msrc"))
    gen, upload, music_db, duck_db = None, None, T["music_db"], T["duck_db"]
    if src == "Générée":
        c1, c2 = st.columns(2)
        styles = list(beds.STYLES)
        style = c1.selectbox("Style", styles, index=styles.index(M["style"]), key=k("mst"), help=h("mstyle"))
        note = c2.selectbox("Tonalité", beds.NOTES, index=beds.NOTES.index(M["key"]), key=k("mkey"), help=h("mkey"))
        bpm_def = M["bpm"] if style == M["style"] else beds.STYLES[style]["bpm"]
        bpm = st.slider("Tempo (BPM)", 60, 150, int(bpm_def), key=k(f"mbpm_{style}"), help=h("bpm"))
        e1, e2, e3 = st.columns(3)
        drums = e1.checkbox("Rythmique", True, key=k("md"), help=h("drums"))
        bass = e2.checkbox("Basse", True, key=k("mb"), help=h("bass"))
        pad = e3.checkbox("Accords", True, key=k("mp"), help=h("pad"))
        gen = (style, bpm, note, drums, bass, pad)
    elif src == "Médiathèque":
        with st.expander("➕ Importer une musique"):
            import_box("musique", k("imp_mus"), "Musique (wav, mp3, flac, ogg)", "import_music")
        songs = store.media("musique")
        if songs:
            mid = st.selectbox("Musique", [m["id"] for m in songs], key=k("mup"), help=h("msrc"),
                               format_func=lambda x: f"{store.get_media(x)['name']} · {store.get_media(x)['seconds']:.0f} s")
            upload = store.get_media(mid)["audio"]
        else:
            st.info("Aucune musique importée pour l'instant : utilise le bloc « Importer une musique » ci-dessus.")
    if src != "Aucune":
        c1, c2 = st.columns(2)
        music_db = c1.slider("Niveau musique (dB)", -30.0, 0.0, float(T["music_db"]), 1.0, key=k("mdb"), help=h("music_db"))
        duck_db = c2.slider("Ducking sous la voix (dB)", -30.0, 0.0, float(T["duck_db"]), 1.0, key=k("mdk"), help=h("duck_db"))
    return gen, upload, music_db, duck_db


def _produce(cfgs, gen, upload, music_db, duck_db, events, echo_in, echo_out, o) -> None:
    with st.status("Production en cours…", expanded=True) as status:
        try:
            tracks = []
            for i, c in enumerate(cfgs):
                media = store.get_media(c["media_id"]) if c["media_id"] else None
                if media is None and not c["text"].strip():
                    continue
                label = f"Voix {i + 1}" + (f" · {media['name']}" if media else "")
                st.write(f"🎙️ {label} : {'enregistrement' if media else 'lecture du texte'}, effets, épaisseur")
                cfg = {**c, "clip": media["audio"] if media else None}
                tracks.append(dict(name=f"voix_{i + 1}", label=label, audio=voices.build_voice(cfg, c["bg"]),
                                   place=c["place"], offset=c["offset"], bg=c["bg"]))
            st.write("🥁 Musique & sons")
            music = None
            if gen:
                style, bpm, note, drums, bass, pad = gen
                music = lambda secs: beds.render(style, bpm, note, secs, drums, bass, pad)  # noqa: E731
            elif upload is not None:
                music = upload
            st.write("🎛️ Mixage, ducking & échos")
            final, stems, layout = mixer.build_project(tracks, music, music_db, duck_db, True, events,
                                                       o["lead_in"], o["tail"], o["fade_out"], echo_in, echo_out)
            st.write("🎚️ Mastering")
            final = master.master(final, o["target"], o["ceiling"], o["glue"], o["air"])
            st.session_state["last_jingle"] = store.add(o["name"], final, stems if o["stems"] else None, layout)
            status.update(label="Jingle prêt ✅", state="complete", expanded=False)
        except Exception as e:  # noqa: BLE001
            status.update(label="Échec de la production", state="error")
            st.error(f"Production impossible : {e}")
