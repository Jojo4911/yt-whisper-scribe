Examples

- Create a vocabulary file (one term per line), e.g. `vocab_example.txt`.
- Use it with `--vocab_file examples/vocab_example.txt`.

Note: media files and generated outputs should be placed in `data/` (gitignored).

Colab quickstart

- Open `examples/colab.ipynb` in Google Colab.
- In Colab: Runtime > Change runtime type > Hardware accelerator: GPU.
- Follow the cells to install dependencies, mount Google Drive, set `PROJECT_DIR` and `OUTPUT_DIR` (on Drive), clone or place the project, then run:
  - `python scripts/transcribe.py "URL_YOUTUBE" --output_dir "$OUTPUT_DIR"`
- Defaults: model=`turbo`, device=`cuda`, language=`en`, replace-map=`SWOOD_Glossary.json`, outputs in `data/`.

Cookies (YouTube auth)

- If YouTube asks to sign in / not-a-bot, export a `cookies.txt` from your browser and place it in `data/cookies.txt`.
- The project auto-detects `data/cookies.txt`. Alternatively, pass `--cookies-file <path>`.
