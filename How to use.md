# Guide d'utilisation

Ce projet permet de transcrire des vidéos YouTube localement avec Whisper, sans API externe.

## Prérequis
- Python 3.9+
- ffmpeg installé et disponible dans le PATH
- PyTorch installé pour CPU ou CUDA (selon votre machine)

## Installation rapide
```
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Installez torch selon votre plateforme/CUDA : https://pytorch.org/get-started/locally/
# Exemple CUDA 11.8 (à adapter)
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

pip install -r requirements.txt
```

## Utilisation de base
```
# SRT avec modèle par défaut
python scripts/transcribe.py "URL_YOUTUBE"

# Modèle plus grand + vocabulaire personnalisé
python scripts/transcribe.py "URL_YOUTUBE" --model medium --vocab_file examples/vocab_example.txt

# Sortie texte brut et dossier dédié
python scripts/transcribe.py "URL_YOUTUBE" --output_format txt --output_dir data/
```

Pendant la transcription, un compteur de temps et un spinner s’affichent. Une fois terminée, la durée de la transcription est affichée.

## Options principales
 - `--model {tiny,base,small,medium,large,large-v2,large-v3}`: modèle Whisper à utiliser. `large` suit l'alias du package installé; utilisez `large-v3` pour forcer la v3.
- `--output_format {srt,txt}`: format de sortie.
- `--output_dir PATH`: dossier de sortie (créé s'il n'existe pas).
- `--vocab_file FILE`: fichier texte (UTF-8) avec un terme par ligne.
- `--language fr|en|auto`: langue forcée (défaut: `en`). `auto` active la détection.
- `--task transcribe|translate`: transcrire la langue source ou traduire en anglais.
- `--device auto|cuda|cpu`: périphérique d'exécution. `auto` choisit `cuda` si dispo, sinon `cpu`.
- `--overwrite` / `--skip-existing`: comportement si le fichier de sortie existe déjà.
- `--verbose`: logs plus détaillés.

## Notes
- Les fichiers générés (.srt/.txt) et médias doivent être placés dans `data/` (ignoré par Git).
- Sous Windows, les SRT sont encodés en `utf-8-sig` pour une meilleure compatibilité.

## Dépréciation
`transcribe_youtube.py` (racine) est conservé pour compatibilité, mais l'entrée officielle est `scripts/transcribe.py`.
