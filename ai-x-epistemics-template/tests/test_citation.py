from pathlib import Path

from epistemics.studies.citation_binder import evaluate, judge_citation

ROOT = Path(__file__).resolve().parents[1]


def test_rejects_quote_that_is_not_in_the_source():
    judged = judge_citation("support", "open all night", "The cafe is closed on Mondays.")
    assert judged["quote_in_source"] is False
    assert judged["verdict"] == "rejected"
    assert judged["quote"] == ""


def test_fixture_quotes_are_in_the_saved_sources():
    payload = evaluate(ROOT)
    assert payload["metrics"]["rejected_quotes"] == 0
    assert payload["metrics"]["support_count"] == 1
    assert payload["metrics"]["contradict_count"] == 1
    for item in payload["items"]:
        source = (ROOT / item["grade"]["evidence"]).read_text(encoding="utf-8")
        assert item["grade"]["quote"] in source
