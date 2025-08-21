"""YT-Whisper-Scribe package.

Provides utilities to download audio from YouTube, transcribe with Whisper,
and generate SRT/TXT outputs.
"""

from .srt import format_timestamp, generate_srt_content

__all__ = [
    "format_timestamp",
    "generate_srt_content",
]

