from __future__ import annotations

import itertools
import logging
import os
import platform
import re
import shutil
import sys
import threading
import time
from typing import Optional

from .replace import apply_glossary_replacements, load_glossary
from .srt import generate_srt_content


def transcribe_youtube(
    url: str,
    *,
    model: str = "small",
    output_format: str = "srt",
    output_dir: str = "data",
    vocab_file: Optional[str] = None,
    language: Optional[str] = "en",
    task: str = "transcribe",
    audio_format: str = "m4a",
    verbose: bool = False,
    device: str = "cuda",
    fp16: Optional[bool] = None,
    temperature: float = 0.0,
    condition_on_previous_text: bool = True,
    replace_map: Optional[str] = "SWOOD_Glossary.json",
    dry_run_replace: bool = False,
    overwrite: bool = False,
    skip_existing: bool = False,
    cookies_file: Optional[str] = None,
) -> str:
    """Download audio from YouTube, run Whisper, and write output.

    Returns the output file path on success. Raises SystemExit with
    distinct codes on fatal precondition failures to keep CLI behavior.
    """
    # Heavy deps imported here to keep module import light for tests
    import torch  # type: ignore
    import whisper  # type: ignore
    import yt_dlp  # type: ignore

    if language and language.lower() == "auto":
        language = None

    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="[%(levelname)s] %(message)s",
    )

    # Device selection
    if device == "auto":
        run_device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        run_device = device
    if run_device == "cuda" and not torch.cuda.is_available():
        print(
            "Erreur: --device cuda demandé mais CUDA n'est pas disponible. Installez PyTorch CUDA et vérifiez les drivers (nvidia-smi)."
        )
        raise SystemExit(5)
    logging.info(f"Utilisation du périphérique : {run_device}")
    if run_device == "cuda":
        try:
            gpu_name = torch.cuda.get_device_name(0)
            logging.info(f"GPU détecté: {gpu_name}")
        except Exception:
            pass

    # ffmpeg precondition
    if shutil.which("ffmpeg") is None:
        print(
            "Erreur: ffmpeg est introuvable dans le PATH. Installez-le et vérifiez 'ffmpeg -version'."
        )
        raise SystemExit(2)

    # Prepare output dir
    os.makedirs(output_dir, exist_ok=True)

    # Download audio
    print(f"Téléchargement de l'audio depuis : {url}")
    temp_stem = os.path.join(output_dir, "temp_audio")
    preferredcodec = audio_format
    # Optional cookies support: use provided path or auto-detect data/cookies.txt
    def _autodetect_cookies() -> Optional[str]:
        candidates = []
        if cookies_file:
            candidates.append(cookies_file)
        # Check environment variable first (secure option)
        env_cookies = os.getenv("YT_COOKIES_FILE")
        if env_cookies:
            candidates.append(env_cookies)
        # Default candidate in CWD
        candidates.append(os.path.join(os.getcwd(), "data", "cookies.txt"))
        # Candidate relative to output_dir
        candidates.append(os.path.join(os.path.abspath(output_dir), "..", "data", "cookies.txt"))
        for c in candidates:
            try:
                if c and os.path.isfile(c):
                    return os.path.abspath(c)
            except Exception:
                pass
        return None

    cookiefile_path = _autodetect_cookies()

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": preferredcodec,
                "preferredquality": "192",
            }
        ],
        "outtmpl": temp_stem,
        "quiet": not verbose,
        "noplaylist": True,
    }
    if cookiefile_path:
        ydl_opts["cookiefile"] = cookiefile_path
        logging.info("[cookies] Utilisation du cookies.txt: %s", cookiefile_path)

    info_dict = None
    for attempt in range(3):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                break
        except Exception as e:  # noqa: BLE001
            logging.warning(f"Tentative {attempt+1}/3 échouée pour le téléchargement: {e}")
            time.sleep(2 * (attempt + 1))
    if info_dict is None:
        print("Erreur lors du téléchargement après plusieurs tentatives.")
        raise SystemExit(3)
    video_title = info_dict.get("title", "video_sans_titre")
    video_id = info_dict.get("id", "unknown")
    temp_audio_file = f"{temp_stem}.{preferredcodec}"

    # Vocabulary prompt
    initial_prompt = None
    if vocab_file:
        try:
            with open(vocab_file, encoding="utf-8") as f:
                vocab_terms = []
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    vocab_terms.append(s)
                if vocab_terms:
                    initial_prompt = ", ".join(vocab_terms)
                    # Harmonisation avec la documentation: terminer par un point si absent
                    if initial_prompt and initial_prompt[-1] not in ".!?…":
                        initial_prompt += "."
                else:
                    initial_prompt = None
            if initial_prompt:
                logging.info(
                    "Vocabulaire chargé depuis %s (%d termes)", vocab_file, len(vocab_terms)
                )
                preview = (
                    initial_prompt if len(initial_prompt) <= 300 else initial_prompt[:300] + "…"
                )
                logging.info("Prompt initial (aperçu): %s", preview)
        except FileNotFoundError:
            logging.warning(f"Le fichier de vocabulaire '{vocab_file}' n'a pas été trouvé.")

    # Transcription
    try:
        # Map shorthand 'turbo' to 'large-v3-turbo' for convenience
        selected_model = "large-v3-turbo" if model == "turbo" else model
        print(f"Chargement du modèle Whisper '{selected_model}'...")
        wmodel = whisper.load_model(selected_model, device=run_device)

        # Progress timer + spinner during transcription
        stop_event = threading.Event()

        def _format_elapsed(elapsed: float) -> str:
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            s = int(elapsed % 60)
            if h:
                return f"{h:02d}:{m:02d}:{s:02d}"
            return f"{m:02d}:{s:02d}"

        def _spinner() -> None:
            frames = itertools.cycle("|/-\\")
            start = time.monotonic()
            while not stop_event.is_set():
                elapsed = time.monotonic() - start
                bar = next(frames)
                msg = f"\rTranscription en cours — {_format_elapsed(elapsed)} {bar}  "
                try:
                    sys.stdout.write(msg)
                    sys.stdout.flush()
                except Exception:
                    pass
                time.sleep(0.1)
            # clear line
            try:
                sys.stdout.write("\r" + " " * 60 + "\r")
                sys.stdout.flush()
            except Exception:
                pass

        t0 = time.monotonic()
        spinner_thread = threading.Thread(target=_spinner, daemon=True)
        spinner_thread.start()

        logging.info(
            "Appel Whisper.transcribe: model=%s, device=%s, language=%s, task=%s, fp16=%s, temp=%.2f, cond_prev=%s",
            selected_model,
            run_device,
            language if language is not None else "auto",
            task,
            (run_device == "cuda"),
            temperature,
            condition_on_previous_text,
        )

        result = wmodel.transcribe(
            temp_audio_file,
            initial_prompt=initial_prompt,
            fp16=(fp16 if fp16 is not None else (run_device == "cuda")),
            language=language,
            task=task,
            temperature=temperature,
            condition_on_previous_text=condition_on_previous_text,
        )
        t1 = time.monotonic()
        stop_event.set()
        spinner_thread.join(timeout=1)
        print(f"Durée de transcription: {_format_elapsed(t1 - t0)}")

        # Output path with pattern: <title>-<video_id>.<lang>.<ext>
        safe_title = re.sub(r"[\\/*?:\"<>|]", "", video_title).strip()
        safe_title = safe_title or "transcription"
        if task == "translate":
            lang_tag = "en"
        else:
            if language:
                lang_tag = str(language).lower()
            else:
                lang_tag = str(result.get("language", "unk")).lower()
        output_filename = f"{safe_title}-{video_id}.{lang_tag}.{output_format}"
        output_path = os.path.join(output_dir, output_filename)

        # Existing file behavior: overwrite by default unless --skip-existing is set
        if os.path.exists(output_path):
            if skip_existing:
                print(f"Fichier existant détecté, opération ignorée: {output_path}")
                return output_path
            if overwrite:
                logging.info("Fichier existant, écrasement demandé: %s", output_path)
            else:
                # Default behavior: overwrite existing file
                print(f"[overwrite] Fichier existant, écrasement par défaut: {output_path}")

        # Optional post-replacements via glossary
        if replace_map:
            try:
                glossary = load_glossary(replace_map)
                new_segments, events = apply_glossary_replacements(result["segments"], glossary)
                total = len(events)
                cross = sum(1 for e in events if e.kind == "cross_boundary")
                if dry_run_replace:
                    logging.info("[replace] DRY RUN: %d suggestions", total)
                    # Always show summary, even without --verbose
                    print(f"[replace] Suggestions: {total} (cross-boundary: {cross})")
                else:
                    result["segments"] = new_segments
                    result["text"] = " ".join(
                        seg.get("text", "").strip() for seg in new_segments
                    ).strip()
                    # Log and print summary
                    if events:
                        logging.info(
                            "[replace] %d remplacements (dont cross-boundary: %d)", total, cross
                        )
                        print(f"[replace] Replacements applied: {total} (cross-boundary: {cross})")
            except Exception as e:  # noqa: BLE001
                logging.warning(
                    f"[replace] Erreur lors du chargement/application du glossaire: {e}"
                )

        if output_format == "txt":
            content = result["text"]
        else:  # srt
            content = generate_srt_content(result)

        # Windows-friendly SRT BOM
        encoding = (
            "utf-8-sig" if (output_format == "srt" and platform.system() == "Windows") else "utf-8"
        )
        with open(output_path, "w", encoding=encoding) as f:
            f.write(content)

        print(f"Transcription terminée ! Fichier sauvegardé sous : {output_path}")
        return output_path

    except Exception as e:  # noqa: BLE001
        print(f"Une erreur est survenue pendant la transcription : {e}")
        raise
    finally:
        # Cleanup
        try:
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
                print(f"Fichier audio temporaire '{temp_audio_file}' supprimé.")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"Impossible de supprimer le fichier temporaire: {e}")
