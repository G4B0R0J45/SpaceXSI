"""Shared helpers for loading items and writing a study result."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def find_root() -> Path:
    override = os.environ.get("EPISTEMICS_ROOT", "").strip()
    if override:
        return Path(override)
    package_root = Path(__file__).resolve().parents[1]
    if (package_root / "report" / "REPORT.md").is_file():
        return package_root
    cwd = Path.cwd()
    if (cwd / "report" / "REPORT.md").is_file():
        return cwd
    return package_root


def load_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        item = json.loads(stripped)
        if not isinstance(item, dict):
            raise ValueError(f"{path} contains a non-object JSONL row")
        items.append(item)
    return items


def prompt_hash(template: str) -> str:
    return hashlib.sha256(template.encode("utf-8")).hexdigest()[:16]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_result(
    *,
    study: str,
    provider: str,
    model: str,
    prompt_template: str,
    n: int,
    items: list[dict],
    metrics: dict,
    baseline: dict | None = None,
    demo: bool = True,
    preexisting: bool = True,
) -> dict:
    payload: dict = {
        "study": study,
        "created_at": utc_now(),
        "provider": provider,
        "model": model,
        "prompt_hash": prompt_hash(prompt_template),
        "n": n,
        "demo": demo,
        "preexisting": preexisting,
        "items": items,
        "metrics": metrics,
    }
    if baseline is not None:
        payload["baseline"] = baseline
    return payload


def write_result(root: Path, payload: dict) -> Path:
    path = root / "results" / f"{payload['study']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def ratio(hits: int, total: int) -> float:
    if total == 0:
        raise ValueError("cannot rate an empty set")
    return round(hits / total, 2)
