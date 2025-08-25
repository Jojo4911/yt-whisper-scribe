from __future__ import annotations

import sys
from pathlib import Path

# Ensure 'src' is on sys.path for the src-layout
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from yt_whisper_scribe.replace import apply_glossary_replacements


def _glossary(correct: str, variants: list[str]) -> dict:
    return {"glossary": [{"correct_term": correct, "detected_variants": variants}]}


def test_replace_within_segment_basic():
    segments = [
        {"start": 0.0, "end": 1.0, "text": "we use s wood design today"},
    ]
    glossary = _glossary("SWOOD", ["s wood"])  # case-insensitive, word-boundaries
    new_segments, events = apply_glossary_replacements(segments, glossary)

    assert new_segments[0]["text"] == "we use SWOOD design today"
    assert any(e.kind == "segment" for e in events)


def test_replace_cross_boundary_spanning_two_segments():
    # Variant spans the boundary between two segments: "s" | " wood"
    segments = [
        {"start": 0.0, "end": 1.0, "text": "this is s"},
        {"start": 1.0, "end": 2.0, "text": " wood box module"},
    ]
    glossary = _glossary("SWOOD", ["s wood"])  # spaces should be treated as \s+
    new_segments, events = apply_glossary_replacements(segments, glossary)

    assert new_segments[0]["text"].endswith("SWOOD")  # replacement placed in left segment
    assert new_segments[1]["text"].startswith(" box module")  # overlap removed from right
    assert any(e.kind == "cross_boundary" for e in events)
