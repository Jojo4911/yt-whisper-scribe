# YT-Whisper-Scribe

Transcription locale de vidéos YouTube avec Whisper et vocabulaire personnalisé. Fonctionne en ligne de commande, sans API externe.

## Prérequis
- Python 3.9+
- ffmpeg disponible dans le PATH (vérifier: `ffmpeg -version`)
- PyTorch (CPU ou CUDA selon votre machine)

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

Pendant la transcription, un compteur et un spinner s’affichent; à la fin, la durée exacte de la transcription et le temps total global sont affichés.

Options clés:
- `--model {tiny,base,small,medium,large,large-v2,large-v3,large-v3-turbo,turbo}`: modèle Whisper (défaut: `small`). `turbo` reste un alias pratique pour `large-v3-turbo`.
- `--output_format {srt,txt}`: format de sortie.
- `--output_dir PATH`: dossier de sortie (défaut: `data/`, créé si absent).
- `--vocab_file FILE`: vocabulaire personnalisé (1 terme par ligne).
- `--language fr|en|auto`: langue forcée (défaut: `en`). Utilisez `auto` pour détection automatique.
- `--task transcribe|translate`: transcrire la langue source ou traduire en anglais.
- `--verbose`: logs détaillés.
- `--overwrite` / `--skip-existing`: comportement vis-à-vis des fichiers existants.
- `--cookies-file FILE`: chemin vers un `cookies.txt` exporté du navigateur pour YouTube. Si non fourni, le projet tente `data/cookies.txt` automatiquement (ou la variable d’env. ci-dessous).
- `--device auto|cuda|cpu`: périphérique d’exécution (défaut: `cuda`). `auto` choisit `cuda` si dispo, sinon `cpu`.
- `--temperature float`: température Whisper (0.0 favorise le vocabulaire).
- `--no-condition-prev`: désactive le contexte du texte précédent.
- Post-traitement (glossaire):
  - `--replace-map FILE.json`: remplacements basés sur un glossaire (variants -> terme correct). Par défaut, `SWOOD_Glossary.json` est appliqué.
  - `--dry-run-replace`: suggère sans appliquer (journalise uniquement).

## Structure du projet
- `src/yt_whisper_scribe/`: logique applicative (pipeline, SRT utils).
- `scripts/transcribe.py`: point d’entrée CLI officiel.
- `tests/`: tests unitaires (ajoute `src` au `PYTHONPATH`).
- `data/`: sorties locales (ignoré par Git).

Note: le shim historique `transcribe_youtube.py` a été retiré; utilisez uniquement `scripts/transcribe.py`.

## Conseils qualité
- Préférez `m4a` comme format audio intermédiaire (qualité/poids). Pour une qualité maximale, utilisez `wav` (fichiers plus gros).
- Sous Windows, les fichiers SRT sont encodés en `utf-8-sig` pour une meilleure compatibilité.
- Les vidéos longues nécessitent du temps/mémoire : ajustez le modèle et vérifiez que ffmpeg et PyTorch sont installés correctement.

## Gestion sécurisée des cookies YouTube

Pour contourner certaines restrictions YouTube sans exposer vos données personnelles :

### Méthode 1 - Nettoyage automatique (Recommandée)
```bash
# Nettoie ton fichier cookies complet pour ne garder que YouTube
python scripts/clean_cookies.py /chemin/vers/cookies_complets.txt data/cookies_youtube.txt

# Utilise les cookies nettoyés
python scripts/transcribe.py "URL" --cookies-file data/cookies_youtube.txt
```

### Méthode 2 - Variable d'environnement
```bash
# Configure la variable (session locale)
export YT_COOKIES_FILE="/chemin/vers/cookies_youtube.txt"
python scripts/transcribe.py "URL"  # Détection automatique
```

Note: les scripts et notebooks d’exemples (Colab) ont été retirés du dépôt.

Sécurité :
- Ne partagez JAMAIS votre fichier cookies complet
- Utilisez toujours le script de nettoyage
- Les cookies YouTube nettoyés ne contiennent pas de données sensibles

## Développement
- Lint/format: `ruff check .` et `black .`
- Tests: `pytest -q`
- Pre-commit: `pip install pre-commit && pre-commit install` (exécute ruff/black/hooks avant chaque commit)

## Intégration continue (CI)
Un workflow GitHub Actions exécute ruff, black (check) et les tests sur Python 3.9–3.11.
## Dépannage GPU / CUDA

Si `--device cpu` fonctionne mais `--device cuda` produit des SRT remplis de ponctuation ("!!!!"), essayez:

- Forcer FP32 sur GPU: `--fp16 false` (ex.: `python scripts/transcribe.py "URL" --device cuda --fp16 false`)
- Mettre à jour le pilote NVIDIA pour correspondre à la version CUDA de PyTorch (voir `nvidia-smi`).
- Réinstaller PyTorch avec une build CUDA adaptée à votre GPU/driver (par ex. cu121) si la build actuelle (ex. cu128) pose problème.

Voir aussi: `TROUBLESHOOTING.md`.
