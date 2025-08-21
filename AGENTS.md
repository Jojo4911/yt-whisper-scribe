# Repository Guidelines

## Structure du projet & organisation des modules
- `src/` : Code cœur de l’app et bibliothèques (packages, modules).
- `scripts/` : Points d’entrée et CLIs (ex. `scripts/transcribe.py`).
- `tests/` : Tests unitaires/intégration reflétant l’arborescence de `src/`.
- `assets/` ou `examples/` : Exemples et médias pour essais locaux.
- `data/` (ignoré par Git) : sorties générées, caches et temporaires.

## Commandes build, test et dev
- Setup : `python -m venv .venv && source .venv/bin/activate` (Windows : `./.venv/Scripts/activate`).
- Installation : `pip install -r requirements.txt` (ou `pip install -e .[dev]` si dispo).
- Exécution (ex.) : `python scripts/transcribe.py --input <path_or_url> --model base`.
- Tests : `pytest -q` (couverture : `pytest --cov=src --cov-report=term-missing`).
- Lint/format : `ruff check .` et `black .` (à exécuter avant commit).

## Style de code & conventions de nommage
- Indentation : 4 espaces ; longueur de ligne 88–100.
- Nommage : `snake_case` (fonctions/modules), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constantes).
- Imports : standard, tiers, locaux (groupés ; ordre alphabétique dans chaque groupe).
- Types : annotations requises pour les API publiques ; préférer des modèles `pydantic` si utilisés.

## Lignes directrices de tests
- Framework : `pytest` avec `tests/` reflétant `src/` (ex. `tests/module/test_feature.py`).
- Conventions : fichiers `test_*.py` ; utiliser des fixtures aux frontières I/O ; échantillons déterministes dans `assets/`.
- Couverture : ≥ 90 % sur les modules critiques ; inclure cas limites (entrée vide, médias longs, erreurs réseau).

## Commits & Pull Requests
- Commits : Conventional Commits (ex. `feat: add YouTube URL parser`, `fix(transcribe): handle 429`).
- Portée : un changement logique par commit ; ajouter un court contexte dans le corps.
- PR : résumé clair, étapes de repro, captures/logs et issues liées ; signaler les breaking changes et migrations.
- CI : faire passer tests, lint et format localement avant d’ouvrir la PR.

## Sécurité & configuration
- Secrets : `.env` (voir `.env.example` si présent). Ne jamais committer de clés/tokens.
- Gros fichiers : garder médias/artéfacts générés hors Git ; utiliser `data/` et mettre à jour `.gitignore`.
- Reproductibilité : pinner les dépendances ; consigner versions de modèles/flags dans les sorties.
