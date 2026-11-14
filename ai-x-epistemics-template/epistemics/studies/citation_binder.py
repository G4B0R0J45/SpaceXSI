"""Citation binder: keep a verdict only when its quote is in the saved source."""

from __future__ import annotations

import json
from pathlib import Path

from epistemics.client import complete, parse_json_object
from epistemics.run import build_result, find_root, load_jsonl, write_result

STUDY = "citation_binder"
PROMPT = """You check whether a saved source supports a claim. Reply with a JSON object only: {"verdict": "support" or "contradict" or "unrelated", "quote": "an exact contiguous substring of the source"}. Copy the quote from the source. Do not paraphrase."""


def judge_citation(verdict: str, quote: str, source_text: str) -> dict:
    accepted = bool(quote) and quote in source_text
    if verdict not in {"support", "contradict", "unrelated"}:
        verdict = "unrelated"
    return {
        "verdict": verdict if accepted else "rejected",
        "quote": quote if accepted else "",
        "quote_in_source": accepted,
        "model_verdict": verdict,
    }


def metrics_for(grades: list[dict]) -> dict:
    return {
        "n": len(grades),
        "support_count": sum(1 for grade in grades if grade["verdict"] == "support"),
        "contradict_count": sum(1 for grade in grades if grade["verdict"] == "contradict"),
        "unrelated_count": sum(1 for grade in grades if grade["verdict"] == "unrelated"),
        "rejected_quotes": sum(1 for grade in grades if not grade["quote_in_source"]),
    }


def evaluate(root: Path | None = None, *, use_live: bool = False) -> dict:
    root = root or find_root()
    items = load_jsonl(root / "examples" / "citation_binder" / "items.jsonl")
    fixtures = json.loads(
        (root / "examples" / "citation_binder" / "fixtures.json").read_text(encoding="utf-8")
    )

    records: list[dict] = []
    grades: list[dict] = []
    provider = "fixture"
    model = "fixture-citer"
    for item in items:
        source_path = root / item["evidence"]
        source_text = source_path.read_text(encoding="utf-8")
        fixture = fixtures[item["id"]]
        fixture_text = json.dumps(fixture)
        messages = [
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": f"Claim: {item['claim']}\n\nSource:\n{source_text}",
            },
        ]
        if use_live:
            completion = complete(messages, fixture_text)
            provider = completion.provider
            model = completion.model
            parsed = parse_json_object(completion.text)
            raw = completion.text
        else:
            parsed = fixture
            raw = fixture_text
        grade = judge_citation(str(parsed.get("verdict", "")), str(parsed.get("quote", "")), source_text)
        grade["evidence"] = item["evidence"]
        grades.append(grade)
        records.append(
            {
                "id": item["id"],
                "prompt_id": item["id"],
                "raw_output": raw,
                "grade": grade,
            }
        )
    return build_result(
        study=STUDY,
        provider=provider,
        model=model,
        prompt_template=PROMPT,
        n=len(items),
        items=records,
        metrics=metrics_for(grades),
    )


def run(root: Path | None = None) -> dict:
    from epistemics.client import model_settings

    root = root or find_root()
    payload = evaluate(root, use_live=bool(model_settings()["api_key"]))
    write_result(root, payload)
    return payload
