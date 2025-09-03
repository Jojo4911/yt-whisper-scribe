from __future__ import annotations

import argparse
import sys
from pathlib import Path
import time

# Supporte l'exécution directe sans installation (src-layout)
try:  # pragma: no cover - chemin de prod
    from yt_whisper_scribe.pipeline import transcribe_youtube
except ModuleNotFoundError:  # pragma: no cover - chemin dev local
    ROOT = Path(__file__).resolve().parents[1]
    SRC = ROOT / "src"
    if SRC.exists():
        sys.path.insert(0, str(SRC))
    from yt_whisper_scribe.pipeline import transcribe_youtube


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcrire une vidéo YouTube avec Whisper et un vocabulaire personnalisé.",
    )
    parser.add_argument("url", type=str, help="L'URL de la vidéo YouTube.")
    parser.add_argument(
        "--model",
        type=str,
        default="small",
        choices=[
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "large-v2",
            "large-v3",
            "large-v3-turbo",
            "turbo",
        ],
        help=(
            "Modèle Whisper à utiliser (inclut large‑v3‑turbo via 'turbo'). "
            "Note: 'large' suit l'alias du package installé."
        ),
    )
    parser.add_argument(
        "--output_format",
        type=str,
        default="srt",
        choices=["txt", "srt"],
        help="Format de sortie (txt ou srt).",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data",
        help="Dossier de sortie (défaut: data/, créé s'il n'existe pas).",
    )
    parser.add_argument(
        "--vocab_file",
        type=str,
        default=None,
        help="Chemin vers un fichier .txt contenant le vocabulaire spécifique.",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="en",  # Laissez la langue par défaut en anglais
        help="Langue forcée (ex: fr, en, auto). Par défaut: en.",
    )
    parser.add_argument(
        "--task",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="Transcrire la langue source ou traduire en anglais.",
    )
    parser.add_argument(
        "--audio_format",
        type=str,
        default="m4a",
        choices=["m4a", "wav"],
        help="Format audio intermédiaire pour le téléchargement.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Active des logs détaillés.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        choices=["auto", "cuda", "cpu"],
        help="Périphérique d'exécution (auto/cuda/cpu). Par défaut: cuda.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Température Whisper (0.0 pour maximiser l'adhérence au vocabulaire).",
    )
    parser.add_argument(
        "--no-condition-prev",
        action="store_true",
        help=(
            "Désactive l'utilisation du texte précédent comme contexte (condition_on_previous_text=False). "
            "Peut renforcer l'effet du prompt, utile si les termes apparaissent tard."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Écrase le fichier de sortie s'il existe.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Ignore si le fichier de sortie existe déjà.",
    )
    parser.add_argument(
        "--replace-map",
        type=str,
        default="SWOOD_Glossary.json",
        help="Chemin vers un JSON de glossaire pour corrections post-transcription (défaut: SWOOD_Glossary.json).",
    )
    parser.add_argument(
        "--dry-run-replace",
        action="store_true",
        help="N'applique pas les remplacements; logge seulement les suggestions.",
    )
    parser.add_argument(
        "--cookies-file",
        type=str,
        default=None,
        help="Chemin vers un cookies.txt exporté du navigateur (yt-dlp)",
    )
    parser.add_argument(
        "--fp16",
        type=str,
        choices=["auto", "true", "false"],
        default="auto",
        help=(
            "Precision for CUDA: auto (default), true (FP16), false (FP32). "
            "Useful if some GPU/driver/torch combos produce degenerate outputs."
        ),
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    start = time.monotonic()
    transcribe_youtube(
        args.url,
        model=args.model,
        output_format=args.output_format,
        output_dir=args.output_dir,
        vocab_file=args.vocab_file,
        language=args.language,
        task=args.task,
        audio_format=args.audio_format,
        verbose=args.verbose,
        device=args.device,
        fp16=(None if args.fp16 == "auto" else (args.fp16 == "true")),
        temperature=args.temperature,
        condition_on_previous_text=(not args.no_condition_prev),
        replace_map=args.replace_map,
        dry_run_replace=args.dry_run_replace,
        overwrite=args.overwrite,
        skip_existing=args.skip_existing,
        cookies_file=args.cookies_file,
    )

    # Global elapsed time from CLI start to end
    elapsed = time.monotonic() - start
    h = int(elapsed // 3600)
    m = int((elapsed % 3600) // 60)
    s = int(elapsed % 60)
    total_fmt = f"{h:02d}:{m:02d}:{s:02d}"
    print(f"Temps total de la procédure: {total_fmt}")


if __name__ == "__main__":
    main()
