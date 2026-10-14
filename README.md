# 🫧 Oxygène Jingle

Studio de jingles et de voix off pour DJs — gratuit, sans clé API.

## Lancer
```bash
pip install -r requirements.txt
streamlit run app.py
```
Déploiement : pousse le dossier sur GitHub puis Streamlit Community Cloud (fichier principal : `app.py`).

## Structure
| Fichier | Rôle |
|---|---|
| `app.py` | Routeur minimal (navigation + chargement de la page active) |
| `theme.py` | Couleurs, CSS, en-têtes |
| `config.py` | Nom de l'app, catalogue des voix |
| `engine/tts.py` | Voix neurales gratuites (edge-tts), scripts multi-voix |
| `engine/fx.py` | Effets voix : gain, écho, reverb, EQ, compresseur, pitch… + presets |
| `engine/sfx.py` | Effets DJ synthétisés (impact, riser, whoosh, laser, bips) |
| `engine/mixer.py` | Mixage voix + musique avec ducking |
| `engine/audio.py` / `store.py` | Utilitaires audio, export WAV/MP3, bibliothèque de session |
| `views/` | Pages : `studio`, `voice_lab`, `library`, composants partagés |

## Script multi-voix
```
Salut les noctambules !
B: Oxygène Jingle, c'est parti !
[pause 1]
Restez avec nous.
```
Les lignes `B:` utilisent la voix B ; `[pause 1]` insère 1 s de silence.

## Notes
- La synthèse vocale demande une connexion internet (service vocal gratuit de Microsoft Edge via `edge-tts`, non officiel) : vérifie les conditions d'usage avant un usage commercial.
- Import de fichiers : wav, mp3, flac, ogg.
