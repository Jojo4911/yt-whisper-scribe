import re
import sys
from pathlib import Path

# Ensure 'src' is on sys.path for the src-layout
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from yt_whisper_scribe.srt import format_timestamp, generate_srt_content


def test_format_timestamp_basic():
    assert format_timestamp(0.0) == "00:00:00,000"
    assert format_timestamp(1.234) == "00:00:01,234"
    assert format_timestamp(65.789) == "00:01:05,789"
    assert format_timestamp(3661.005) == "01:01:01,005"


def test_generate_srt_content_structure():
    result = {
        "segments": [
            {"start": 0.0, "end": 1.2, "text": " Hello "},
            {"start": 1.2, "end": 2.5, "text": "World"},
        ]
    }
    srt = generate_srt_content(result)
    # Doit contenir deux blocs numérotés, des timestamps et le texte nettoyé
    assert "1\n00:00:00,000 --> 00:00:01,200\nHello\n" in srt
    assert "2\n00:00:01,200 --> 00:00:02,500\nWorld\n" in srt
    # Vérifie présence des séparations entre blocs (double saut de ligne)
    assert re.search(r"\n\n2\n", srt) is not None
