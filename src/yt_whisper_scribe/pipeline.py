from __future__ import annotations

import os
import re
import sys
import time
import logging
import shutil
import platform
from typing import Optional
import threading
import itertools

from .srt import generate_srt_content


def transcribe_youtube(
    url: str,
    *,
    model: str = "base",
    output_format: str = "srt",
    output_dir: str = ".",
    vocab_file: Optional[str] = None,
    language: Optional[str] = "en",
    task: str = "transcribe",
    audio_format: str = "m4a",
    verbose: bool = False,
    device: str = "auto",
    temperature: float = 0.0,
    condition_on_previous_text: bool = True,
    # VAD-based segmentation
    vad_filter: bool = False,
    vad_min_silence_ms: Optional[int] = None,
    vad_threshold: Optional[float] = None,
    overwrite: bool = False,
    skip_existing: bool = False,
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
    temp_audio_file = f"{temp_stem}.{preferredcodec}"

    # Vocabulary prompt
    initial_prompt = None
    if vocab_file:
        try:
            with open(vocab_file, "r", encoding="utf-8") as f:
                vocab_terms = []
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    vocab_terms.append(s)
                initial_prompt = ", ".join(vocab_terms) if vocab_terms else None
            if initial_prompt:
                logging.info(
                    "Vocabulaire chargé depuis %s (%d termes)", vocab_file, len(vocab_terms)
                )
                preview = initial_prompt if len(initial_prompt) <= 300 else initial_prompt[:300] + "…"
                logging.info("Prompt initial (aperçu): %s", preview)
        except FileNotFoundError:
            logging.warning(f"Le fichier de vocabulaire '{vocab_file}' n'a pas été trouvé.")

    # Transcription
    try:
        use_faster = False
        fw_model = None
        if vad_filter:
            try:
                from faster_whisper import WhisperModel  # type: ignore

                use_faster = True
                print(f"Chargement du modèle Faster-Whisper '{model}'...")
                compute_type = "float16" if run_device == "cuda" else "int8"
                fw_model = WhisperModel(model, device=run_device, compute_type=compute_type)
            except Exception:
                print(
                    "Erreur: --vad-filter nécessite faster-whisper. Installez-le: 'pip install faster-whisper'"
                )
                raise SystemExit(6)
        if not use_faster:
            print(f"Chargement du modèle Whisper '{model}'...")
            wmodel = whisper.load_model(model, device=run_device)

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

        print("Lancement de la transcription (cela peut prendre du temps)...")
        t0 = time.monotonic()
        spinner_thread = threading.Thread(target=_spinner, daemon=True)
        spinner_thread.start()

        logging.info(
            "Appel Whisper.transcribe: model=%s, device=%s, language=%s, task=%s, fp16=%s, temp=%.2f, cond_prev=%s, vad=%s",
            model,
            run_device,
            language if language is not None else "auto",
            task,
            (run_device == "cuda"),
            temperature,
            condition_on_previous_text,
            vad_filter,
        )

        # Build VAD parameters if any provided
        vad_params = None
        if vad_min_silence_ms is not None or vad_threshold is not None:
            vad_params = {}
            if vad_min_silence_ms is not None:
                vad_params["min_silence_duration_ms"] = int(vad_min_silence_ms)
            if vad_threshold is not None:
                vad_params["vad_threshold"] = float(vad_threshold)

        if use_faster and fw_model is not None:
            segments_iter, info = fw_model.transcribe(
                temp_audio_file,
                initial_prompt=initial_prompt,
                language=language,
                task=task,
                vad_filter=True,
                vad_parameters=vad_params,
                temperature=temperature,
                condition_on_previous_text=condition_on_previous_text,
            )
            # Materialize segments to a dict similar to openai-whisper
            segs = []
            texts = []
            for seg in segments_iter:
                segs.append({"start": float(seg.start), "end": float(seg.end), "text": seg.text})
                texts.append(seg.text)
            result = {"segments": segs, "text": " ".join(t.strip() for t in texts).strip()}
        else:
            result = wmodel.transcribe(
                temp_audio_file,
                initial_prompt=initial_prompt,
                fp16=(run_device == "cuda"),
                language=language,
                task=task,
                temperature=temperature,
                condition_on_previous_text=condition_on_previous_text,
            )
        t1 = time.monotonic()
        stop_event.set()
        spinner_thread.join(timeout=1)
        print(f"Durée de transcription: {_format_elapsed(t1 - t0)}")

        # Output path
        safe_title = re.sub(r"[\\/*?:\"<>|]", "", video_title).strip()
        safe_title = safe_title or "transcription"
        output_path = os.path.join(output_dir, f"{safe_title}.{output_format}")

        # Existing file behavior
        if os.path.exists(output_path):
            if skip_existing:
                print(f"Fichier existant détecté, opération ignorée: {output_path}")
                return output_path
            if not overwrite:
                print(
                    f"Fichier existe déjà. Relancez avec --overwrite ou --skip-existing: {output_path}"
                )
                raise SystemExit(4)

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
