# Documentation Technique du Projet YT-Whisper-Scribe

## Objectif
Transcrire des vidéos YouTube localement à l’aide de Whisper, avec support d’un vocabulaire personnalisé influençant la transcription (prompt initial), et export en `.srt` ou `.txt`.

## Architecture
- `src/yt_whisper_scribe/`
  - `srt.py`: utilitaires de génération SRT
    - `format_timestamp(seconds: float) -> str`
    - `generate_srt_content(result: dict) -> str`
  - `pipeline.py`: orchestration du flux de bout en bout
    - `transcribe_youtube(url, *, model, output_format, output_dir, vocab_file, language, task, audio_format, verbose, device, overwrite, skip_existing) -> str`
- `scripts/transcribe.py`: point d’entrée CLI (parser d’arguments + appel `pipeline.transcribe_youtube`)
- `tests/test_transcribe.py`: tests unitaires pour les utilitaires SRT (ajoute `src/` au `PYTHONPATH`)
- `examples/README.md`: indications pour créer un vocabulaire d’exemple
- `data/`: sorties locales et médias (ignorés par Git)

Remarque: `transcribe_youtube.py` à la racine est conservé uniquement pour compatibilité. La commande recommandée passe par `scripts/transcribe.py`.

## Flux de traitement
1. Préconditions: vérification `ffmpeg` dans le PATH.
2. Téléchargement audio: `yt-dlp` + post-processing `FFmpegExtractAudio` vers `m4a` (ou `wav`).
3. Vocabulaire: lecture d’un fichier `.txt` (UTF-8), concaténé en prompt initial.
4. Modèle Whisper: chargement du modèle (`tiny`→`large`) avec `device` (`cpu`/`cuda`).
5. Transcription: appel `model.transcribe(...)` avec `language` (ou détection auto via `auto`) et `task` (`transcribe`/`translate`).
6. Export: génération de contenu `.srt` via `generate_srt_content` ou texte brut via `result['text']`. Encodage `utf-8-sig` des SRT sous Windows.
7. Nettoyage: suppression du fichier audio temporaire.

## Codes de sortie (CLI)
- `2`: `ffmpeg` introuvable.
- `3`: échec du téléchargement après retries.
- `4`: fichier de sortie déjà présent sans `--overwrite`/`--skip-existing`.
- `5`: `--device cuda` demandé mais CUDA indisponible.

## Dépendances
- Runtime: `openai-whisper`, `yt-dlp` (et `ffmpeg` côté système), `torch` (installé séparément selon plateforme/CUDA).
- Dev: `pytest`, `pytest-cov`, `ruff`, `black`, `pre-commit`.

## Tests
- `tests/test_transcribe.py` couvre:
  - Formatage timestamp SRT.
  - Structure d’un SRT minimal à partir de segments factices.
- Les tests injectent `src/` dans `sys.path` pour fonctionner sans installation du package.

Pistes d’extension (non implémentées):
- Tests de cas limites (segments vides/désordonnés), erreurs `yt-dlp`/réseau, absence de vocabulaire, fichiers déjà existants.

## Qualité & CI
- `pyproject.toml`: line-length 100 (`black`/`ruff`).
- Hooks `pre-commit`: `black`, `ruff --fix`, validations génériques.
- CI GitHub Actions: lint (ruff, black --check), tests (3.9–3.11).

## Notes d’implémentation
- Les imports lourds (`torch`, `whisper`, `yt_dlp`) résident dans `pipeline.transcribe_youtube` pour permettre l’import des utilitaires SRT sans dépendances lors des tests.
- Le prompt vocabulaire est construit en joignant les lignes non vides, séparées par des virgules et terminées par un point.
- Sous Windows, l’encodage `utf-8-sig` des SRT améliore la compatibilité avec certains lecteurs.

