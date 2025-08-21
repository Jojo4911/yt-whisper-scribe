from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ReplaceEvent:
    kind: str  # "segment" or "cross_boundary"
    segment_index: int
    next_segment_index: Optional[int]
    variant: str
    correct_term: str
    before: str
    after: str


def _variant_regex(variant: str) -> re.Pattern[str]:
    # Build a case-insensitive, word-boundary regex; normalize spaces to \s+
    esc = re.escape(variant.strip())
    esc = esc.replace("\\ ", r"\s+")
    pattern = rf"\b{esc}\b"
    return re.compile(pattern, flags=re.IGNORECASE)


def _apply_within_segment(text: str, pat: re.Pattern[str], replacement: str) -> Tuple[str, int]:
    def repl(m: re.Match[str]) -> str:
        return replacement

    new_text, n = pat.subn(repl, text)
    return new_text, n


def _apply_cross_boundary(prev_text: str, next_text: str, pat: re.Pattern[str], replacement: str) -> Tuple[str, str, int]:
    # Examine boundary region
    tail = prev_text[-40:]
    head = next_text[:40]
    bridge = tail + " " + head
    m = pat.search(bridge)
    if not m:
        return prev_text, next_text, 0
    s, e = m.span()
    sep_pos = len(tail)
    # Ensure the match crosses the boundary
    if not (s < sep_pos and e > sep_pos):
        return prev_text, next_text, 0
    # Compute portions in prev and next
    prev_rel_s = max(0, s - (sep_pos - len(tail)))  # within tail
    prev_rel_e = min(len(tail), e - (sep_pos - len(tail)))
    # Map tail slice to absolute indices in prev_text
    abs_prev_s = max(0, len(prev_text) - len(tail) + prev_rel_s)
    abs_prev_e = max(0, len(prev_text) - len(tail) + prev_rel_e)
    # Portion in head/next
    next_rel_s = max(0, s - (sep_pos + 1))
    next_rel_e = max(0, e - (sep_pos + 1))
    abs_next_s = next_rel_s
    abs_next_e = next_rel_e
    # Apply: place full replacement in prev, remove overlapped part in next
    new_prev = prev_text[:abs_prev_s] + replacement + prev_text[abs_prev_e:]
    new_next = next_text[:abs_next_s] + next_text[abs_next_e:]
    return new_prev, new_next, 1


def load_glossary(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_glossary_replacements(
    segments: List[Dict[str, Any]],
    glossary: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[ReplaceEvent]]:
    entries: List[Dict[str, Any]] = glossary.get("glossary", [])
    events: List[ReplaceEvent] = []

    # Prepare regexes per entry
    compiled: List[Tuple[str, List[re.Pattern[str]]]] = []
    for entry in entries:
        correct = entry.get("correct_term", "")
        variants = entry.get("detected_variants", []) or []
        pats: List[re.Pattern[str]] = []
        for v in variants:
            try:
                pats.append(_variant_regex(v))
            except re.error:
                continue
        if correct and pats:
            compiled.append((correct, pats))

    # Work on a copy
    new_segments = [
        {"start": seg["start"], "end": seg["end"], "text": (seg.get("text") or "")}
        for seg in segments
    ]

    # Pass 1: within-segment replacements
    for idx, seg in enumerate(new_segments):
        text = seg["text"]
        for correct, pats in compiled:
            for pat in pats:
                new_text, n = _apply_within_segment(text, pat, correct)
                if n > 0:
                    events.append(
                        ReplaceEvent(
                            kind="segment",
                            segment_index=idx,
                            next_segment_index=None,
                            variant=pat.pattern,
                            correct_term=correct,
                            before=text,
                            after=new_text,
                        )
                    )
                    text = new_text
        seg["text"] = text

    # Pass 2: cross-boundary replacements (adjacent segments only)
    for i in range(len(new_segments) - 1):
        left = new_segments[i]["text"]
        right = new_segments[i + 1]["text"]
        changed = False
        for correct, pats in compiled:
            for pat in pats:
                new_left, new_right, n = _apply_cross_boundary(left, right, pat, correct)
                if n > 0:
                    events.append(
                        ReplaceEvent(
                            kind="cross_boundary",
                            segment_index=i,
                            next_segment_index=i + 1,
                            variant=pat.pattern,
                            correct_term=correct,
                            before=left + " | " + right,
                            after=new_left + " | " + new_right,
                        )
                    )
                    left, right = new_left, new_right
                    changed = True
        if changed:
            new_segments[i]["text"] = left
            new_segments[i + 1]["text"] = right

    return new_segments, events

