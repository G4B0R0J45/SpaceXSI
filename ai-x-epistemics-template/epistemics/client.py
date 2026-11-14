"""OpenAI-compatible chat client. An empty API key selects fixtures."""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Completion:
    text: str
    provider: str
    model: str


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE pairs. Existing environment variables win."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def model_settings() -> dict[str, str]:
    return {
        "base_url": os.environ.get("MODEL_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        "api_key": os.environ.get("MODEL_API_KEY", "").strip(),
        "model": os.environ.get("MODEL_NAME", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
    }


def complete(messages: list[dict[str, str]], fixture: str) -> Completion:
    """Return the fixture text when MODEL_API_KEY is empty. Otherwise call the API."""
    settings = model_settings()
    if not settings["api_key"]:
        return Completion(text=fixture, provider="fixture", model="fixture")
    text = chat_complete(messages, settings)
    return Completion(text=text, provider="openai-compatible", model=settings["model"])


def chat_complete(messages: list[dict[str, str]], settings: dict[str, str]) -> str:
    body = json.dumps(
        {"model": settings["model"], "messages": messages, "temperature": 0}
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{settings['base_url']}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {settings['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def parse_json_object(text: str) -> dict:
    """Parse a JSON object, including one wrapped in a markdown fence."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[: cleaned.rfind("```")]
        cleaned = cleaned.strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(cleaned[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("model output is not a JSON object")
    return value
