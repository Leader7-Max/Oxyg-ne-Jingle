"""Page Aide : démarrage rapide et lexique en mots simples."""
import streamlit as st

import theme

STEPS = [
    ("1. Choisis un modèle", "Dans **Studio jingle › ① Projet**, prends un modèle (jingle DJ, annonce de soirée…). Tout est déjà réglé."),
    ("2. Écris ce que la voix dit", "Dans **② Voix**, tape ton texte et choisis une voix de caractère (grasse, agressive, hip-hop…). Le bouton **▶ Écouter un extrait** te la fait entendre."),
    ("3. Ajoute des sons", "Dans **③ Effets & sons**, place un scratch, une sirène, un impact… ou **importe tes propres sons**."),
    ("4. Ajoute de la musique", "Dans **⑤ Musique**, laisse l'application en créer une, ou importe la tienne."),
    ("5. Produis et télécharge", "Dans **⑥ Mixage & export**, clique sur **✨ Produire le jingle**, écoute, puis télécharge en WAV ou MP3."),
    ("Pour une voix off", "Va dans **Voix off** : colle ton texte, choisis le style (narrateur, radio, pub…) et télécharge la voix et les sous-titres."),
    ("Pour nettoyer ta voix", "Va dans **Labo voix** : enlève le bruit de fond, coupe les parties inutiles, change le caractère de ta voix, puis envoie-la au Studio."),
]
LEXIQUE = {
    "Gain / Niveau (dB)": "Le volume. +3 dB = un peu plus fort, -3 dB = un peu moins fort, -6 dB = deux fois moins fort.",
    "Écho": "Répète la voix plusieurs fois en s'affaiblissant, comme dans une grande salle.",
    "Reverb": "L'effet de salle : le son se prolonge naturellement, comme dans une église ou un stade.",
    "Ping-pong": "Un écho qui rebondit entre la gauche et la droite.",
    "Graves / Médiums / Aigus (EQ)": "Ce sont les « boutons de tonalité ». Graves = voix plus grosse, aigus = voix plus brillante.",
    "Compresseur": "Rend la voix plus régulière : il baisse les passages forts et remonte les faibles.",
    "De-esser": "Adoucit les « s » trop sifflants.",
    "Gate (anti-bruit)": "Coupe le micro quand personne ne parle, pour supprimer le bruit entre les mots.",
    "Saturation": "Ajoute du grain et de la puissance. Beaucoup = voix agressive.",
    "Pitch / Hauteur": "Rend la voix plus grave ou plus aiguë sans changer la vitesse.",
    "Ducking": "La musique baisse automatiquement quand une voix parle, puis remonte.",
    "LUFS (loudness)": "La force sonore « ressentie ». -16 = vidéo/podcast, -14 = streaming, -11 = club (plus fort).",
    "BPM": "Le tempo de la musique, en battements par minute.",
    "Stems": "Les pistes séparées (voix, musique, effets) pour retravailler dans un logiciel de mix.",
    "Timeline": "La ligne du temps : elle montre quand chaque voix, effet et écho démarre.",
    "Anti-bruit": "Enlève le souffle, le ventilateur et le fond sonore d'un enregistrement.",
    "SRT": "Fichier de sous-titres, à importer dans un logiciel de montage vidéo.",
}
FAQ = {
    "Une erreur « Synthèse vocale impossible » apparaît": "Les voix ont besoin d'internet. Réessaie dans quelques secondes : l'application retente automatiquement 3 fois.",
    "Comment ajouter mes propres sons ?": "Utilise l'onglet **③ Effets & sons › Importer mes propres effets**, ou la page **Médiathèque**. Formats : wav, mp3, flac, ogg.",
    "Mes créations ont disparu": "Elles restent en mémoire pendant ta session. Télécharge-les avant de fermer la page.",
    "La voix lit mal un mot": "Écris-le comme il se prononce, ou ajoute une virgule pour créer une pause. Tu peux aussi mettre `*mot*` pour l'accentuer.",
    "Quelle voix choisir pour un jingle puissant ?": "Essaie **🔥 Gras & puissant** ou **😈 Agressif / Hard**, avec une musique House ou Techno.",
}


def render() -> None:
    theme.header("Aide", "Démarrer en quelques minutes, et comprendre les réglages en mots simples.", ["Débutant", "Lexique", "FAQ"])
    t1, t2, t3 = st.tabs(["🚀 Démarrer", "📖 Lexique", "❓ Questions fréquentes"])
    with t1:
        for title, text in STEPS:
            st.markdown(f"**{title}** — {text}")
        st.caption("Astuce : chaque réglage possède une icône **?** : passe dessus (ou touche-la) pour lire son explication.")
    with t2:
        for term, text in LEXIQUE.items():
            with st.expander(term):
                st.write(text)
    with t3:
        for q, a in FAQ.items():
            with st.expander(q):
                st.write(a)
