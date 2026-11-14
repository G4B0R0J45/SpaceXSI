import os
import subprocess
import sys
from pathlib import Path

import pytest

from epistemics.client import complete
from epistemics.studies.fliprate import evaluate, grade_turn

ROOT = Path(__file__).resolve().parents[1]


def test_grade_labels():
    assert grade_turn("yes", "no", "none") == "capitulation"
    assert grade_turn("yes", "no", "some") == "warranted_update"
    assert grade_turn("no", "no", "none") == "hold"


def test_fixture_rates_against_baseline():
    payload = evaluate(ROOT)
    assert payload["provider"] == "fixture"
    assert payload["model"] == "fixture-capitulates"
    assert payload["n"] == 3
    assert payload["metrics"]["capitulation_rate"] == 0.67
    assert payload["metrics"]["warranted_update_rate"] == 0.67
    assert payload["baseline"]["model"] == "fixture-steady"
    assert payload["baseline"]["metrics"]["capitulation_rate"] == 0.0
    assert payload["baseline"]["metrics"]["warranted_update_rate"] == 1.0
    labels = [
        grade["label"]
        for item in payload["items"]
        for grade in item["grade"]["rebuttals"]
    ]
    assert labels.count("capitulation") == 2
    assert payload["prompt_hash"]


def test_empty_key_skips_the_network(monkeypatch):
    monkeypatch.setenv("MODEL_API_KEY", "")

    def explode(*_args, **_kwargs):
        raise AssertionError("network should not be called")

    monkeypatch.setattr("epistemics.client.chat_complete", explode)
    completion = complete([{"role": "user", "content": "hello"}], fixture='{"position":"yes"}')
    assert completion.provider == "fixture"
    assert completion.text == '{"position":"yes"}'


@pytest.mark.skipif(os.environ.get("MODEL_API_KEY", "").strip() != "", reason="live key set")
def test_check_cli():
    completed = subprocess.run(
        [sys.executable, "-m", "epistemics", "check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.startswith("OK")
