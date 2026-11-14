from pathlib import Path

from epistemics.studies.notes_delay import delay_metrics, evaluate, load_notes

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_delay_metric():
    text = (ROOT / "examples" / "notes_delay" / "sample_notes.csv").read_text(encoding="utf-8")
    assert "SYNTHETIC" in text
    metrics = delay_metrics(load_notes(text))
    assert metrics["median_hours"] == 30
    assert metrics["share_after_24h"] == 0.6
    assert metrics["n"] == 5
    assert metrics["synthetic"] is True


def test_evaluate_marks_the_result_synthetic():
    payload = evaluate(ROOT)
    assert payload["metrics"]["median_hours"] == 30
    assert payload["demo"] is True
    assert payload["preexisting"] is True
