"""Page Studio : script -> voix -> effets -> habillage -> jingle."""
import streamlit as st

import theme
from config import VOICES
from engine import audio, fx, mixer, sfx, store, tts
from views.components import fx_panel, player

DEFAULT_SCRIPT = "Oxygène Jingle, la radio qui vous fait respirer la musique !"


def render() -> None:
    theme.header("Studio jingle", "Écris, choisis tes voix, ajoute tes effets : ton jingle est prêt.")
    voices = list(VOICES)

    theme.section("1 · Script & voix")
    script = st.text_area("Script", DEFAULT_SCRIPT, height=120,
                          help="Une ligne = une réplique. B: devant la ligne → voix B. [pause 1] → silence.")
    voice_a = st.selectbox("Voix A", voices, index=0)
    with st.expander("Voix B (dialogue à deux voix)"):
        voice_b = st.selectbox("Voix B", voices, index=1)
        st.caption("Exemple :\n\nSalut les noctambules !\n\nB: Oxygène Jingle, c'est parti !")
    c1, c2, c3 = st.columns(3)
    rate = c1.slider("Vitesse %", -50, 100, 0, 5)
    pitch = c2.slider("Hauteur Hz", -50, 50, 0, 5)
    vol = c3.slider("Volume %", -50, 50, 0, 5)

    theme.section("2 · Effets de voix")
    with st.expander("Écho, gain, reverb, EQ…", expanded=True):
        params = fx_panel("studio", "Club / Dancefloor")

    theme.section("3 · Habillage")
    with st.expander("Musique, effets DJ, fondus"):
        music_file = st.file_uploader("Nappe / musique de fond (optionnel)",
                                      type=["wav", "mp3", "flac", "ogg"])
        m1, m2 = st.columns(2)
        music_db = m1.slider("Niveau musique (dB)", -30.0, 0.0, -8.0, 1.0)
        duck_db = m2.slider("Ducking sous la voix (dB)", -30.0, 0.0, -12.0, 1.0)
        loop = st.checkbox("Boucler la musique", value=True)
        choices = ["Aucun"] + list(sfx.EFFECTS)
        s1, s2 = st.columns(2)
        intro = s1.selectbox("Effet d'intro", choices)
        outro = s2.selectbox("Effet de fin", choices)
        sfx_db = st.slider("Niveau des effets (dB)", -20.0, 0.0, -4.0, 1.0)
        t1, t2, t3 = st.columns(3)
        lead_in = t1.slider("Avant la voix (s)", 0.0, 5.0, 1.0, 0.1)
        tail = t2.slider("Après la voix (s)", 0.0, 5.0, 1.0, 0.1)
        fade_out = t3.slider("Fondu final (s)", 0.0, 4.0, 0.8, 0.1)

    name = st.text_input("Nom du fichier", "oxygene-jingle")

    if st.button("✨ Générer le jingle", type="primary", use_container_width=True):
        if not script.strip():
            st.warning("Écris un script d'abord.")
        else:
            try:
                with st.spinner("Synthèse des voix…"):
                    voice = tts.render_script(script, voice_a, voice_b, rate, pitch, vol)
                with st.spinner("Effets & mixage…"):
                    voice = audio.normalize(fx.process(voice, params), -3.0)
                    music = audio.decode(music_file.getvalue()) if music_file else None
                    final = mixer.build_jingle(
                        voice, music=music, music_db=music_db, duck_db=duck_db, loop=loop,
                        intro=sfx.get(intro), outro=sfx.get(outro), sfx_db=sfx_db,
                        lead_in=lead_in, tail=tail, fade_out=fade_out)
                    st.session_state["last_jingle"] = store.add(name, final)
            except Exception as e:  # noqa: BLE001
                st.error(f"Génération impossible : {e}")

    item = st.session_state.get("last_jingle")
    if item:
        theme.section(f"Résultat · {item['seconds']:.1f} s")
        player(item, "last")
