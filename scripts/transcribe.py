from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Modèle Whisper à utiliser.",
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
        default=".",
        help="Dossier de sortie (sera créé s'il n'existe pas).",
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
        default="en",
        help="Langue forcée (ex: fr, en, auto). Par défaut: en. Utilisez 'auto' pour détection automatique.",
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
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Périphérique d'exécution (auto/cuda/cpu). 'cuda' force le GPU si disponible.",
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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
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
        overwrite=args.overwrite,
        skip_existing=args.skip_existing,
    )


if __name__ == "__main__":
    main()
