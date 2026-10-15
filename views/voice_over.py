"""Page Voix off : lecture professionnelle d'un texte (radio, littérature, vidéo) + musique + sous-titres."""
import streamlit as st

import theme
from engine import beds, master, mixer, reader, store, voices
from engine.casting import CHARACTERS
from views.components import fx_panel, import_box, player, voice_picker
from views.helptexts import h

LUFS = {"-16 LUFS · vidéo / podcast": -16.0, "-14 LUFS · streaming / radio": -14.0, "-11 LUFS · club / festival": -11.0}
EXAMPLE = ("Bienvenue à la grande soirée Oxygène.\n\nUne nuit, une énergie, une seule destination ! "
           "Rendez-vous samedi à 22h30, entrée gratuite avant minuit.\n\n"
           "Alors... préparez-vous : ça va être *inoubliable*.")


def render() -> None:
    theme.header("Voix off", "Colle ton texte : il est lu comme par un pro de la radio ou de la littérature.",
                 ["Lecture pro", "Pauses & intonations", "Sous-titres .srt", "Musique de fond"])
    t_txt, t_voix, t_fx, t_mus, t_exp = st.tabs(["① Texte", "② Voix & lecture", "③ Effets", "④ Musique de fond", "⑤ Export"])

    with t_txt:
        st.info("Colle ou écris ton texte. Une **ligne vide** = nouveau paragraphe (pause plus longue). "
                "`[pause 1]` ajoute 1 seconde de silence. `*mot*` met un mot en valeur.")
        text = st.text_area("Ton texte", EXAMPLE, height=280, key="vo_text", help=h("vo_text"))
        words = len(text.split())
        st.caption(f"{words} mots · environ {words / 2.6:.0f} secondes de lecture")
        if len(text) > 6000:
            st.warning("Texte très long : découpe-le en plusieurs voix off pour une production plus rapide.")

    with t_voix:
        d = dict(char="🎙️ Narrateur littéraire", voice="", preset="Studio Pro — voix off", thick="Aucune", level=0.0)
        vp = voice_picker("vo", d)
        styles = list(reader.STYLES)
        style = st.selectbox("Style de lecture", styles, index=styles.index(vp["style"]), key=f"vo_style_{vp['sig']}", help=h("style"))
        st.caption(reader.STYLE_HELP[style])
        c1, c2 = st.columns(2)
        pro = c1.toggle("Lecture professionnelle", value=True, key="vo_pro", help=h("pro"))
        caps = c2.toggle("Accentuer les MAJUSCULES", value=False, key="vo_caps", help=h("caps"))
        c1, c2, c3 = st.columns(3)
        rate = c1.slider("Vitesse %", -50, 100, int(vp["rate"]), 1, key=f"vo_ra_{vp['sig']}", help=h("rate"))
        pitch = c2.slider("Hauteur Hz", -50, 50, int(vp["pitch"]), 1, key=f"vo_pi_{vp['sig']}", help=h("pitch"))
        vol = c3.slider("Volume %", -50, 50, int(vp["vol"]), 1, key=f"vo_vo_{vp['sig']}", help=h("vol"))
        thick = st.selectbox("Épaisseur de voix", ["Aucune", "Double voix", "Double + octave grave", "Chœur 3 voix"],
                             index=["Aucune", "Double voix", "Double + octave grave", "Chœur 3 voix"].index(vp["thick"]),
                             key=f"vo_th_{vp['sig']}", help=h("thick"))
        with st.expander("🔍 Voir comment le texte sera lu"):
            plan = reader.build_plan(text, vp["voice"], style, rate, pitch, vol, pro, caps)
            st.caption(h("plan"))
            if plan:
                st.dataframe(reader.describe(plan), hide_index=True, use_container_width=True)

    with t_fx:
        st.caption("Les effets de la voix. Le preset du caractère choisi est déjà appliqué.")
        params = fx_panel(f"vo_fx_{vp['sig']}", vp["preset"])

    with t_mus:
        srcs = ["Aucune", "Générée", "Médiathèque"]
        src = st.radio("Musique de fond", srcs, horizontal=True, key="vo_msrc", help=h("vo_music"))
        gen, music = None, None
        if src == "Générée":
            c1, c2 = st.columns(2)
            style_m = c1.selectbox("Style", list(beds.STYLES), index=list(beds.STYLES).index("Cinématique"), key="vo_mst", help=h("mstyle"))
            note = c2.selectbox("Tonalité", beds.NOTES, index=2, key="vo_mkey", help=h("mkey"))
            bpm = st.slider("Tempo (BPM)", 60, 150, int(beds.STYLES[style_m]["bpm"]), key=f"vo_bpm_{style_m}", help=h("bpm"))
            gen = (style_m, bpm, note)
        elif src == "Médiathèque":
            with st.expander("➕ Importer une musique"):
                import_box("musique", "vo_imp_mus", "Musique (wav, mp3, flac, ogg)", "import_music")
            songs = store.media("musique")
            if songs:
                mid = st.selectbox("Musique", [m["id"] for m in songs], key="vo_mup", help=h("msrc"),
                                   format_func=lambda x: f"{store.get_media(x)['name']} · {store.get_media(x)['seconds']:.0f} s")
                music = store.get_media(mid)["audio"]
            else:
                st.info("Aucune musique importée pour l'instant.")
        c1, c2 = st.columns(2)
        music_db = c1.slider("Niveau musique (dB)", -30.0, 0.0, -14.0, 1.0, key="vo_mdb", help=h("music_db"))
        duck_db = c2.slider("Ducking sous la voix (dB)", -30.0, 0.0, -14.0, 1.0, key="vo_mdk", help=h("duck_db"))

    with t_exp:
        c1, c2 = st.columns(2)
        target = LUFS[c1.selectbox("Loudness cible", list(LUFS), key="vo_lufs", help=h("lufs"))]
        ceiling = c2.slider("Plafond crête (dBFS)", -3.0, -0.1, -1.0, 0.1, key="vo_ceil", help=h("ceiling"))
        c1, c2 = st.columns(2)
        lead = c1.slider("Silence avant la voix (s)", 0.0, 6.0, 1.0, 0.1, key="vo_lead", help=h("vo_lead"))
        tail = c2.slider("Après la voix (s)", 0.0, 6.0, 1.5, 0.1, key="vo_tail", help=h("tail"))
        make_srt = st.checkbox("Créer aussi les sous-titres (.srt)", True, key="vo_srt", help=h("srt"))
        name = st.text_input("Nom du fichier", "voix-off", key="vo_name", help=h("name"))
        if st.button("🎬 Produire la voix off", type="primary", use_container_width=True, help=h("produce")):
            if not text.strip():
                st.warning("Écris ou colle un texte dans l'onglet ①.")
            else:
                if gen:
                    sm, nt, bp = gen
                    music = lambda secs: beds.render(sm, bp, nt, secs, True, True, True)  # noqa: E731
                cfg = dict(text=text, voice=vp["voice"], rate=rate, pitch=pitch, vol=vol, style=style, pro=pro,
                           caps=caps, params=params, level=0.0, pan=0.0, thick=thick, repeat=1, clip=None)
                _produce(cfg, music, music_db, duck_db, lead, tail, target, ceiling, make_srt, name)
        item = st.session_state.get("last_voiceover")
        if item:
            theme.section(f"Résultat · {item['name']}")
            player(item, "vo")


def _produce(cfg, music, music_db, duck_db, lead, tail, target, ceiling, make_srt, name) -> None:
    with st.status("Production de la voix off…", expanded=True) as status:
        try:
            st.write("🗣️ Lecture du texte (pauses, intonations)")
            a, timings = voices.build_voice(cfg, with_timings=True)
            st.write("🎛️ Mixage")
            tracks = [dict(name="voix_off", label="Voix off", audio=a, place="En même temps", offset=0.0, bg=False)]
            final, stems, layout = mixer.build_project(tracks, music, music_db, duck_db, True, [], lead, tail, 1.5)
            st.write("🎚️ Mastering")
            final = master.master(final, target, ceiling, glue=True, air=True)
            item = store.add(name, final, stems, layout)
            if make_srt and timings:
                item["srt"] = reader.to_srt(timings, offset=lead)
            st.session_state["last_voiceover"] = item
            status.update(label="Voix off prête ✅", state="complete", expanded=False)
        except Exception as e:  # noqa: BLE001
            status.update(label="Échec de la production", state="error")
            st.error(f"Production impossible : {e}")
