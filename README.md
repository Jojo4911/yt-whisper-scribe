# YT-Whisper-Scribe

Transcription locale de vidéos YouTube avec Whisper et vocabulaire personnalisé. Fonctionne en ligne de commande, sans API externe.

## Prérequis
- Python 3.9+
- ffmpeg disponible dans le PATH (vérifier: `ffmpeg -version`)
- PyTorch (compatible CPU ou CUDA selon votre machine)

Installation rapide:
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

## Utilisation
Exemples de base:
```
# SRT avec modèle par défaut
python scripts/transcribe.py "URL_YOUTUBE"

# Modèle plus grand + vocabulaire
python scripts/transcribe.py "URL_YOUTUBE" --model medium --vocab_file mon_vocab.txt

# Sortie texte brut et dossier dédié
python scripts/transcribe.py "URL_YOUTUBE" --output_format txt --output_dir data/
```

Pendant la transcription, un compteur de temps et un spinner s’affichent; à la fin, la durée exacte de la transcription est indiquée.

Options clés:
- `--model {tiny,base,small,medium,large,large-v2,large-v3,large-v3-turbo,turbo}`: modèle Whisper (défaut: `turbo`). `large` suit l'alias; `turbo` est un raccourci pour `large-v3-turbo` (selon la version du package installé).
- `--output_format {srt,txt}`: format de sortie.
- `--output_dir PATH`: dossier de sortie (défaut: `data/`, créé si absent).
- `--vocab_file FILE`: vocabulaire personnalisé (1 terme par ligne).
- `--language fr|en|auto`: langue forcée (défaut: `en`). Utilisez `auto` pour détection automatique.
- `--task transcribe|translate`: transcrire la langue source ou traduire en anglais.
- `--verbose`: logs plus détaillés.
- `--overwrite` / `--skip-existing`: comportement si le fichier final existe.
- `--device auto|cuda|cpu`: périphérique d'exécution (défaut: `cuda`). Utilisez `auto` pour sélection automatique si besoin.
 - Post-traitement (glossaire de corrections):
   - `--replace-map FILE.json`: active les remplacements basés sur un glossaire (variants -> terme correct). Par défaut, `SWOOD_Glossary.json` est appliqué.
   - `--dry-run-replace`: suggère sans appliquer (journalise uniquement).

## Structure du projet
- `src/yt_whisper_scribe/`: logique applicative (pipeline, SRT utils).
- `scripts/transcribe.py`: point d’entrée CLI.
- `tests/`: tests unitaires (ajout de `src` au `PYTHONPATH`).
- `data/`: sorties locales (ignoré par Git).

Note: `transcribe_youtube.py` est conservé pour compatibilité, mais l’entrée officielle est `scripts/transcribe.py`.

## Conseils qualité
- Préférez `m4a` comme format audio intermédiaire (qualité/poids). Pour une qualité maximale, utilisez `wav` (fichiers plus gros).
- Sous Windows, les fichiers SRT sont encodés en `utf-8-sig` pour une meilleure compatibilité.
- Les vidéos longues nécessitent du temps/mémoire : ajustez le modèle et vérifiez que ffmpeg et PyTorch sont installés correctement.

## Développement
- Lint/format: `ruff check .` et `black .`
- Tests: `pytest -q`
- Pre-commit: `pip install pre-commit && pre-commit install` (exécute ruff/black/hooks avant chaque commit)

## Intégration continue (CI)
Un workflow GitHub Actions exécute ruff, black (check) et les tests sur Python 3.9–3.11.
Rien à faire de votre côté si le dépôt est sur GitHub.
