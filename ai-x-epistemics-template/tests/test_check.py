import json
from pathlib import Path

from epistemics.check import check_submission

ROOT = Path(__file__).resolve().parents[1]


def abstract(count: int) -> str:
    return " ".join(["word"] * count)


def write_bundle(root: Path, *, report: str, claims: list[dict], results: dict | None = None) -> None:
    (root / "report").mkdir(parents=True)
    (root / "results").mkdir()
    (root / "evidence").mkdir()
    (root / "report" / "REPORT.md").write_text(report, encoding="utf-8")
    (root / "report" / "claims.json").write_text(json.dumps(claims), encoding="utf-8")
    (root / "results" / "demo.json").write_text(
        json.dumps(results if results is not None else {"metrics": {"score": 1}}),
        encoding="utf-8",
    )
    (root / "evidence" / "src.md").write_text("The cafe is closed on Mondays.", encoding="utf-8")


def base_report() -> str:
    return f"""# Demo

## Abstract
{abstract(180)}

## Question
What is the score?

## Related Work
Named prior art only.

## Method
One fixture item.

## Results
The score was 1.

## Limitations
n is tiny.

## Dual-Use
This does not establish a field result. No personal data was collected.

## Preexisting Work
This bundle is preexisting test scaffolding.
"""


def base_claims() -> list[dict]:
    return [
        {
            "id": "score",
            "text": "The score was 1.",
            "source": "results/demo.json",
            "pointer": "/metrics/score",
            "value": 1,
        }
    ]


def test_repo_bundle_passes():
    result = check_submission(ROOT)
    assert result.ok, result.errors
    assert result.notes


def test_passing_bundle(tmp_path):
    write_bundle(tmp_path, report=base_report(), claims=base_claims())
    result = check_submission(tmp_path)
    assert result.ok, result.errors
    assert result.warnings == []


def test_missing_claim_source(tmp_path):
    claims = base_claims()
    claims[0]["source"] = "results/missing.json"
    write_bundle(tmp_path, report=base_report(), claims=claims)
    result = check_submission(tmp_path)
    assert not result.ok
    assert any("does not exist" in error for error in result.errors)


def test_value_mismatch(tmp_path):
    claims = base_claims()
    claims[0]["value"] = 99
    write_bundle(tmp_path, report=base_report(), claims=claims)
    result = check_submission(tmp_path)
    assert not result.ok
    assert any("does not match" in error for error in result.errors)


def test_missing_dual_use_section(tmp_path):
    report = base_report().replace("## Dual-Use\nThis does not establish a field result. No personal data was collected.\n\n", "")
    write_bundle(tmp_path, report=report, claims=base_claims())
    result = check_submission(tmp_path)
    assert not result.ok
    assert any("dual-use" in error for error in result.errors)


def test_quote_must_be_in_the_evidence_file(tmp_path):
    claims = [
        {
            "id": "quote",
            "text": "The source says the cafe is closed.",
            "quote": "open all night",
            "evidence": "evidence/src.md",
        }
    ]
    report = base_report().replace("The score was 1.", "The source says the cafe is closed.")
    write_bundle(tmp_path, report=report, claims=claims)
    result = check_submission(tmp_path)
    assert not result.ok
    assert any("not an exact substring" in error for error in result.errors)
