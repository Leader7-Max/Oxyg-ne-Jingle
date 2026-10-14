# 🫧 Oxygène Jingle — v3

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
engine/           audio.py tts.py fx.py layers.py voices.py synth.py sfx.py beds.py mixer.py master.py store.py denoise.py edit.py (+ __init__.py)
views/            studio.py voice_lab.py sounds.py library.py components.py (+ __init__.py)
```

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
