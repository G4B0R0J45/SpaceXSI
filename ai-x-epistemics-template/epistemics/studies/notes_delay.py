"""Note delay on a synthetic CSV. This is not a Community Notes measurement."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from epistemics.run import build_result, find_root, ratio, write_result

STUDY = "notes_delay"
PROMPT = "Deterministic delay calculator for a synthetic CSV. No model call."
AFTER_HOURS = 24


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_notes(text: str) -> list[dict]:
    lines = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    reader = csv.DictReader(lines)
    notes: list[dict] = []
    for row in reader:
        post = parse_time(row["post_at"])
        note = parse_time(row["note_at"])
        hours = (note - post).total_seconds() / 3600
        notes.append({"note_id": row["note_id"], "delay_hours": hours})
    return notes


def median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def delay_metrics(notes: list[dict]) -> dict:
    hours = [note["delay_hours"] for note in notes]
    middle = median(hours)
    median_hours = int(middle) if float(middle).is_integer() else round(middle, 2)
    late = sum(1 for value in hours if value > AFTER_HOURS)
    return {
        "median_hours": median_hours,
        "share_after_24h": ratio(late, len(hours)),
        "n": len(hours),
        "synthetic": True,
    }


def evaluate(root: Path | None = None) -> dict:
    root = root or find_root()
    text = (root / "examples" / "notes_delay" / "sample_notes.csv").read_text(encoding="utf-8")
    if "SYNTHETIC" not in text:
        raise ValueError("sample notes file must be marked SYNTHETIC")
    notes = load_notes(text)
    metrics = delay_metrics(notes)
    return build_result(
        study=STUDY,
        provider="fixture",
        model="delay-calculator",
        prompt_template=PROMPT,
        n=len(notes),
        items=[
            {
                "id": note["note_id"],
                "prompt_id": note["note_id"],
                "raw_output": json_hours(note["delay_hours"]),
                "grade": note,
            }
            for note in notes
        ],
        metrics=metrics,
    )


def json_hours(value: float) -> str:
    return str(int(value) if float(value).is_integer() else round(value, 2))


def run(root: Path | None = None) -> dict:
    root = root or find_root()
    payload = evaluate(root)
    write_result(root, payload)
    return payload
