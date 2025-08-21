from __future__ import annotations


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm).

    Raises AssertionError if ``seconds`` is negative.
    """
    assert seconds >= 0, "Le temps négatif n'est pas autorisé."
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    secs = milliseconds // 1_000
    milliseconds %= 1_000

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def generate_srt_content(result: dict) -> str:
    """Generate SRT content from a Whisper-like result dict.

    Expected structure:
    {"segments": [{"start": float, "end": float, "text": str}, ...]}
    """
    srt_content: list[str] = []
    for i, segment in enumerate(result["segments"], start=1):
        start_time = format_timestamp(segment["start"])  # type: ignore[arg-type]
        end_time = format_timestamp(segment["end"])  # type: ignore[arg-type]
        text = segment["text"].strip()
        srt_content.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
    return "\n".join(srt_content)

