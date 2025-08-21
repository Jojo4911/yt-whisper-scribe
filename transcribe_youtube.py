"""Shim de compatibilité pour l'ancien point d'entrée.

Utilisation recommandée: `python scripts/transcribe.py ...`

Ce fichier délègue vers `scripts/transcribe.py` tout en conservant la compatibilité
avec les anciennes commandes. Il affiche un message de dépréciation.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:  # pragma: no cover
    print(
        "[DEPRECATION] Utilisez désormais `python scripts/transcribe.py ...`.\n"
        "Redirection automatique vers le nouveau CLI...",
        file=sys.stderr,
    )

    # Essaye d'importer le nouveau CLI
    try:
        from scripts.transcribe import main as cli_main  # type: ignore

        cli_main()
        return
    except Exception as import_err:  # noqa: BLE001
        # Fallback: exécuter le script par chemin absolu
        try:
            import runpy

            root = Path(__file__).resolve().parent
            runpy.run_path(str(root / "scripts" / "transcribe.py"), run_name="__main__")
            return
        except Exception:
            raise import_err


if __name__ == "__main__":
    main()

