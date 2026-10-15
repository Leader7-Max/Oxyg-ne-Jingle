# 🫧 Oxygène Jingle — v4

Studio de jingles et de voix off pour DJs : gratuit, sans clé API.

## Lancer
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Arborescence (tout à la racine du dépôt)
```
app.py            routeur minimal
theme.py          thème « studio néon », hero, chips, forme d'onde
config.py         nom de l'app + catalogue de 26 voix
requirements.txt
.streamlit/config.toml
engine/           audio.py tts.py reader.py characters.py fx.py layers.py voices.py synth.py sfx.py beds.py mixer.py master.py store.py denoise.py edit.py (+ __init__.py)
views/            studio.py voiceover.py voice_lab.py media.py sounds.py library.py guide.py components.py helps.py (+ __init__.py)
```

## Nouveautés v4
- **Lecture « pro »** (`engine/reader.py`) : le texte collé est nettoyé (liens, émojis, « 20h30 », « 15 % »…), découpé en phrases, lu avec une intonation par phrase (questions qui montent, fins qui descendent, exclamations), des pauses de ponctuation et de paragraphe, des mots accentués (`*mot*`) et des respirations optionnelles. 8 styles : journal, radio, pub, littéraire, documentaire, suspense, chuchoté…
- **Personnages vocaux** (`engine/characters.py`) : « Grosse voix DJ (grasse) », « Agressive / Hype », « MC », « Speaker de stade », « Narrateur cinéma », « Démon », « ASMR »… (voix + lecture + effets + épaisseur en un clic). 6 nouveaux presets d'effets.
- **Choix de voix** : filtres langue / genre, 46 voix, écoute d'un échantillon, aperçu complet avec effets.
- **Imports** : voix, effets et musiques importés (page Médiathèque ou directement dans le Studio) et placés sur la timeline ; les effets importés apparaissent avec l'icône 📥.
- **Organisation** : navigation groupée (Créer / Ressources / Projets & aide), Studio en onglets (Voix · Musique · Effets DJ · Échos & mix · Produire), page **Voix off** dédiée, page **Guide & aide**.
- **Aides « ? »** en langage simple sur chaque réglage (`views/helps.py`).

## Nouveautés v4
- **Navigation par catégories** : Créer (Studio jingle, Voix off) · Préparer (Labo voix, Médiathèque, Sons & nappes) · Mes créations · Aide. Le Studio est découpé en onglets ①–⑥.
- **Import de voix, d'effets et de musiques** (Médiathèque ou directement dans le Studio) : ils se placent sur la timeline comme les sons intégrés, avec retouche (preset d'effets, hauteur).
- **Voix de caractère** : Gras & puissant, Agressif / Hard, Boss final, Hype Hip-Hop, Annonceur de stade, Nuit radio, Diva club, Narrateur littéraire… avec écoute d'un extrait. Catalogue filtrable par langue et genre.
- **Lecteur de texte « pro »** : normalisation (20h30, %, €, abréviations), pauses selon la ponctuation, voix qui monte aux questions et descend en fin de paragraphe, phrases longues respirées, mots mis en valeur (`*mot*`), 8 styles de lecture.
- **Voix off** : page dédiée (texte long → voix → effets → musique de fond → WAV/MP3 + sous-titres .srt).
- **Changeur de voix** dans le Labo : donne un caractère (grasse, agressive, robot…) à une voix enregistrée.
- **Aide « ? »** sur chaque réglage + page Guide débutant (démarrage, lexique, FAQ).

## Nouveautés v3
- **Voix superposées** : jusqu'à 6 voix (texte synthétisé ou clip enregistré), chacune avec ses effets, son niveau, son panoramique, son placement (« en même temps » ou « après la précédente ») et son décalage.
- **Effets complets par voix** : EQ, de-esser, compression, saturation, pitch, chorus, flanger, phaser, trémolo, modulation en anneau, largeur stéréo, voix inversée, écho ping-pong, reverb.
- **Écho de début et de fin** du jingle : zone, délai, répétitions, niveau, ton, ping-pong.
- **Anti-bruit** (Labo voix) : réduction spectrale (profil automatique ou appris au début de la prise) + filtre anti-ronflement 50/60 Hz.
- **Montage** (Labo voix) : supprimer une partie, garder une sélection, raccourcir les silences, annuler, fondus.
- **Clips** : une voix traitée dans le Labo s'utilise ensuite comme voix du Studio.

## Ce que fait le Studio
- **Casting** : voix principale, voix 2 (dialogue) et voix de fond (chœur, chuchotement, nappe vocale).
- **Épaisseur** : double voix, double + octave grave, chœur 3 voix.
- **Son studio** : presets « Studio Pro », « Trailer », « Annonceur FM »… (EQ, de-esser, compression, saturation douce, reverb de pièce).
- **Nappes générées** : House, Hip-Hop, Techno, Pop, Lo-fi, Cinématique (rythmique, basse, accords, side-chain).
- **Effets DJ** : scratch, sirènes, airhorn, tape stop, rewind, risers, impacts…
- **Mastering** : cible LUFS (-16 / -14 / -11), plafond crête, export WAV 24-bit, MP3, stems ZIP.

## Notes
- La synthèse vocale utilise le service gratuit de Microsoft Edge (`edge-tts`) : connexion internet requise, service non officiel — vérifie les conditions avant un usage commercial.
- Une voix de synthèse reste une voix de synthèse : pour un rendu 100 % « humain », enregistre ta voix et passe-la dans le **Labo voix**.
