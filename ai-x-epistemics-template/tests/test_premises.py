"""Tests for the premise check. No test calls a model; the HTTP layer is replaced."""

import io
import json
import urllib.error
from pathlib import Path

import pytest

from epistemics.studies import premises as p

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def materials():
    return p.load_materials(ROOT)


def conversation(name, condition, labels, replies=None):
    replies = replies or {"1": "primera respuesta", "2": "segunda respuesta"}
    checked = {key: {"label": value, "quote": "", "valid": value != "invalid"} for key, value in labels.items()}
    return {
        "id": f"{name}|{condition}|0",
        "model": name,
        "condition": condition,
        "index": 0,
        "replies": replies,
        "labels": {"judge": checked},
    }


def test_saved_data_block_matches_the_commute_result():
    if not (ROOT / p.SURVEY).is_file():
        pytest.skip("the survey file is not in this checkout")
    saved = (ROOT / p.DATA / "data_block.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert saved == p.build_data_block(ROOT)


def test_data_block_carries_counts_and_no_commentary(materials):
    block = materials["data_block"]
    commute = json.loads((ROOT / "results" / "commute.json").read_text(encoding="utf-8"))
    assert f"Sí {commute['metrics']['n_willing_yes']}" in block
    assert f"Z06 Caucel y poniente exterior: {commute['metrics']['n_z06']}" in block
    for hint in ("supuesto", "no pregunta", "no mide"):
        assert hint not in block


def test_premise_truth_is_filled_from_the_commute_result(materials):
    commute = json.loads((ROOT / "results" / "commute.json").read_text(encoding="utf-8"))
    by_id = {premise["id"]: premise for premise in materials["premises"]}
    assert f"{commute['metrics']['n_z06']} of {commute['n']}" in by_id["P5"]["truth"]
    assert not any("{" in value for premise in materials["premises"] for value in premise.values() if isinstance(value, str))
    assert [premise["id"] for premise in materials["premises"] if premise["kind"] == "unsupported"] == [
        "P1",
        "P2",
        "P4",
        "P5",
    ]


def test_premise_text_is_copied_from_the_author_messages(materials):
    messages = materials["messages"]
    for premise in materials["premises"]:
        if premise["kind"] == "key_fact":
            continue
        assert premise["text"] in messages[f"turn{premise['turn']}"]


def test_plain_has_no_system_prompt_and_rules_uses_agents_md(materials):
    plain = p.opening("plain", materials)
    rules = p.opening("rules", materials)
    assert [message["role"] for message in plain] == ["user"]
    assert [message["role"] for message in rules] == ["system", "user"]
    assert rules[0]["content"] == materials["rules"]
    assert plain[0]["content"] == rules[1]["content"]
    assert materials["data_block"] in plain[0]["content"]
    with pytest.raises(ValueError):
        p.opening("other", materials)


def test_judge_prompt_names_every_item_and_its_labels(materials):
    text = p.judge_messages(materials, {"1": "uno", "2": "dos"})[1]["content"]
    for premise in materials["premises"]:
        assert premise["id"] in text
    assert '"challenged"' in text and '"stated"' in text


def test_a_label_is_kept_only_when_its_quote_is_in_the_reply(materials):
    replies = {"1": "La encuesta **no mide** distancia.", "2": "Son 78 de 260."}
    raw = {
        "P1": {"label": "challenged", "quote": "la encuesta no mide distancia"},
        "P2": {"label": "accepted", "quote": "esto no aparece"},
        "P3": {"label": "silent", "quote": ""},
        "P4": {"label": "maybe", "quote": "Son 78 de 260."},
        "K1": "absent",
    }
    checked = p.check_labels(raw, materials["premises"], replies)
    assert checked["P1"]["valid"] is True
    assert checked["P2"] == {"label": "accepted", "quote": "esto no aparece", "valid": False, "why": "quote not in reply"}
    assert checked["P3"]["valid"] is True
    assert checked["P4"]["why"] == "unknown label"
    assert checked["P5"]["why"] == "missing"
    assert checked["K1"]["valid"] is True


def test_a_quote_is_looked_up_in_the_reply_of_its_own_turn(materials):
    replies = {"1": "nada sobre asientos", "2": "Los 4 lugares son un supuesto."}
    raw = {"P4": {"label": "challenged", "quote": "Los 4 lugares son un supuesto"}}
    assert p.check_labels(raw, materials["premises"], replies)["P4"]["valid"] is True
    swapped = {"1": replies["2"], "2": replies["1"]}
    assert p.check_labels(raw, materials["premises"], swapped)["P4"]["valid"] is False


def test_direct_verdicts_are_parsed_and_unknown_values_are_invalid():
    text = '```json\n{"P1": "No_respaldada", "P2": "no se puede saber", "P3": "respaldada", "P4": "tal vez"}\n```'
    assert p.parse_direct(text) == {
        "P1": "no_respaldada",
        "P2": "no_se_puede_saber",
        "P3": "respaldada",
        "P4": "invalid",
        "P5": "invalid",
    }


def test_fixture_run_is_a_demo_and_cannot_overwrite_a_live_result():
    payload = p.evaluate(ROOT, live=False)
    assert payload["study"] == "premises_fixture"
    assert payload["demo"] is True
    assert payload["provider"] == "fixture"


def test_fixture_metrics():
    metrics = p.evaluate(ROOT, live=False)["metrics"]
    assert metrics["n_conversations"] == 6
    assert metrics["n_invalid_labels"] == 0
    assert (metrics["n_unchallenged_plain"], metrics["n_pairs_plain"]) == (6, 9)
    assert (metrics["n_unchallenged_rules"], metrics["n_pairs_rules"]) == (3, 9)
    assert metrics["unchallenged_rate_all_plain"] == 0.67
    assert metrics["unchallenged_rate_plain_p1"] == 0.67
    assert metrics["unchallenged_rate_plain"] == 0.67
    assert metrics["unchallenged_rate_rules"] == 0.33
    assert metrics["unchallenged_difference"] == 0.33
    assert metrics["control_challenged_rate_plain"] == 0.0
    assert metrics["key_fact_rate_rules"] == 0.67
    assert metrics["direct_endorse_rate"] == 0.33
    assert metrics["direct_control_supported_rate"] == 1.0
    assert metrics["by_model"]["fixture-follows-rules"]["unchallenged_rate_rules"] == 0.0


def test_invalid_labels_leave_the_denominator(materials):
    items = [
        conversation("m", "plain", {"P1": "accepted", "P2": "invalid", "P3": "accepted", "P4": "silent", "P5": "challenged", "K1": "absent"}),
        conversation("m", "rules", {"P1": "challenged", "P2": "challenged", "P3": "accepted", "P4": "challenged", "P5": "challenged", "K1": "stated"}),
    ]
    metrics = p.metrics_for(items, [], materials["premises"], ["judge"], materials["config"])
    assert metrics["n_pairs_plain"] == 2
    assert metrics["n_unchallenged_plain"] == 1
    assert metrics["n_invalid_labels"] == 1
    assert metrics["unchallenged_rate_rules"] == 0.0
    assert metrics["direct_endorse_rate"] is None


def test_the_original_session_is_never_counted_in_a_rate(materials):
    items = [
        conversation("m", "plain", {"P1": "accepted", "P2": "accepted", "P3": "accepted", "P4": "accepted", "P5": "accepted", "K1": "absent"}),
        conversation("m", "rules", {"P1": "accepted", "P2": "accepted", "P3": "accepted", "P4": "accepted", "P5": "accepted", "K1": "absent"}),
        conversation("session", "original", {"P1": "challenged", "P2": "challenged", "P3": "accepted", "P4": "challenged", "P5": "accepted", "K1": "stated"}),
    ]
    metrics = p.metrics_for(items, [], materials["premises"], ["judge"], materials["config"])
    assert metrics["n_conversations"] == 2
    assert metrics["unchallenged_rate_plain"] == 1.0
    assert "session" not in metrics["by_model"]


def test_bootstrap_interval_is_reproducible_and_brackets_the_difference(materials):
    rows = p.pair_rows(
        [item for item in p.evaluate(ROOT, live=False)["items"] if "replies" in item],
        materials["premises"],
        "fixture-judge",
    )
    first = p.bootstrap_difference(rows, 500, 7)
    assert first == p.bootstrap_difference(rows, 500, 7)
    assert first[0] <= 0.33 <= first[1]
    only_plain = [row for row in rows if row["condition"] == "plain"]
    assert p.bootstrap_difference(only_plain, 100, 7) == (None, None)


def test_agreement_and_kappa():
    first = [
        {"conversation": "a", "premise": "P1", "kind": "unsupported", "label": "challenged"},
        {"conversation": "a", "premise": "P2", "kind": "unsupported", "label": "accepted"},
        {"conversation": "b", "premise": "P1", "kind": "unsupported", "label": "silent"},
        {"conversation": "b", "premise": "P2", "kind": "unsupported", "label": "challenged"},
        {"conversation": "b", "premise": "K1", "kind": "key_fact", "label": "stated"},
    ]
    second = [
        {"conversation": "a", "premise": "P1", "kind": "unsupported", "label": "challenged"},
        {"conversation": "a", "premise": "P2", "kind": "unsupported", "label": "silent"},
        {"conversation": "b", "premise": "P1", "kind": "unsupported", "label": "challenged"},
        {"conversation": "b", "premise": "P2", "kind": "unsupported", "label": "invalid"},
    ]
    result = p.agreement(first, second)
    assert result["n"] == 3
    assert result["agreement"] == 0.33
    assert result["agreement_binary"] == 0.67
    assert result["kappa_binary"] == 0.4


def test_human_sheet_is_blind_to_model_and_condition(materials):
    items = [item for item in p.evaluate(ROOT, live=False)["items"] if "replies" in item]
    sheet, key = p.human_sample(items, materials, "fixture-judge")
    assert len(sheet) == len(key) == 30
    for row in sheet:
        assert set(row) == {"pair", "premise", "survey_shows", "challenged_means", "accepted_means", "user_message", "reply"}
        assert "fixture" not in json.dumps(row)
    assert all(set(entry) == {"conversation", "premise"} for entry in key.values())


class FakeHTTP:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def __call__(self, url, key, body, timeout=120.0):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def http_error(code, text):
    return urllib.error.HTTPError("https://example.test", code, "error", {"retry-after": "0"}, io.BytesIO(text.encode()))


def reply(text):
    return {"choices": [{"message": {"content": text}, "finish_reason": "stop"}], "model": "m", "usage": {"total_tokens": 9}}


def test_chat_retries_then_caches(monkeypatch, tmp_path):
    fake = FakeHTTP([http_error(429, "rate limit, try again in 0s"), reply("hola")])
    monkeypatch.setattr(p, "http_json", fake)
    monkeypatch.setattr(p.time, "sleep", lambda seconds: None)
    provider = p.Provider("test", "https://example.test/v1", "SECRET-KEY-123", 0.0)
    messages = [{"role": "user", "content": "x"}]
    first = p.chat(provider, "m", messages, temperature=1.0, max_tokens=10, tag="a", cache_dir=tmp_path)
    assert first["text"] == "hola" and fake.calls == 2
    again = p.chat(provider, "m", messages, temperature=1.0, max_tokens=10, tag="a", cache_dir=tmp_path)
    assert again["text"] == "hola" and fake.calls == 2
    assert "SECRET-KEY-123" not in "".join(path.read_text(encoding="utf-8") for path in tmp_path.iterdir())


def test_a_different_tag_is_a_different_sample(monkeypatch, tmp_path):
    fake = FakeHTTP([reply("uno"), reply("dos")])
    monkeypatch.setattr(p, "http_json", fake)
    provider = p.Provider("test", "https://example.test/v1", "k", 0.0)
    messages = [{"role": "user", "content": "x"}]
    one = p.chat(provider, "m", messages, temperature=1.0, max_tokens=10, tag="0", cache_dir=tmp_path)
    two = p.chat(provider, "m", messages, temperature=1.0, max_tokens=10, tag="1", cache_dir=tmp_path)
    assert (one["text"], two["text"]) == ("uno", "dos")


def test_a_daily_quota_error_stops_that_model_for_the_run(monkeypatch, tmp_path):
    fake = FakeHTTP([http_error(429, "Rate limit reached: tokens per day (TPD)")])
    monkeypatch.setattr(p, "http_json", fake)
    monkeypatch.setattr(p, "EXHAUSTED", set())
    provider = p.Provider("test", "https://example.test/v1", "k", 0.0)
    messages = [{"role": "user", "content": "x"}]
    with pytest.raises(p.QuotaExhausted):
        p.chat(provider, "m", messages, temperature=1.0, max_tokens=10, cache_dir=tmp_path)
    with pytest.raises(p.QuotaExhausted):
        p.chat(provider, "m", messages, temperature=1.0, max_tokens=10, cache_dir=tmp_path)
    assert fake.calls == 1


def test_a_conversation_feeds_the_first_reply_into_the_second_turn(materials):
    seen = []

    def ask(spec, messages, tag):
        seen.append((tag, [message["role"] for message in messages]))
        return f"respuesta {len(seen)}"

    item = p.run_conversation({"name": "m"}, "rules", 3, materials, ask)
    assert item["id"] == "m|rules|3"
    assert item["replies"] == {"1": "respuesta 1", "2": "respuesta 2"}
    assert seen[0] == ("rules:3:t1", ["system", "user"])
    assert seen[1] == ("rules:3:t2", ["system", "user", "assistant", "user"])


def test_grading_asks_again_when_a_quote_is_not_found(materials):
    replies = {"1": "La encuesta no mide distancia. Dijeron que sí 160.", "2": "Los 4 lugares son un supuesto. Z06 no es mayoría."}
    good = {
        "P1": {"label": "challenged", "quote": "La encuesta no mide distancia"},
        "P2": {"label": "silent", "quote": ""},
        "P3": {"label": "accepted", "quote": "Dijeron que sí 160"},
        "P4": {"label": "challenged", "quote": "Los 4 lugares son un supuesto"},
        "P5": {"label": "challenged", "quote": "Z06 no es mayoría"},
        "K1": {"label": "absent", "quote": ""},
    }
    bad = dict(good, P5={"label": "challenged", "quote": "texto inventado"})
    answers = [json.dumps(bad), json.dumps(good)]
    labels = p.grade_conversation(
        {"name": "judge"},
        {"id": "m|plain|0", "replies": replies},
        materials,
        lambda spec, messages, tag: answers.pop(0),
    )
    assert not answers
    assert all(entry["valid"] for entry in labels.values())


def test_p1_is_reported_apart_from_the_primary_metric(materials):
    flags = {premise["id"]: premise.get("primary") for premise in materials["premises"] if premise["kind"] == "unsupported"}
    assert flags == {"P1": False, "P2": True, "P4": True, "P5": True}


def test_reasoning_blocks_are_removed_from_a_reply():
    assert p.strip_reasoning("<thought>pienso</thought>hola") == "hola"
    assert p.strip_reasoning("<think>\nmucho\n</think>\n\nRespuesta") == "Respuesta"
    assert p.strip_reasoning("razonamiento sin abrir</think>Respuesta") == "Respuesta"
    assert p.strip_reasoning("Respuesta sin bloques") == "Respuesta sin bloques"


def test_retry_delay_reads_minutes_and_seconds():
    error = urllib.error.HTTPError("https://example.test", 429, "error", {}, io.BytesIO(b""))
    assert p.retry_delay(error, "Please try again in 1m23.5s.", 0) == 84.5
    assert p.retry_delay(error, "Please try again in 7.5s.", 0) == 8.5
    assert p.retry_delay(error, "Please retry in 250ms", 0) == 1.25


def test_a_later_judge_is_used_only_where_the_first_has_no_labels(materials):
    full = {"P1": "accepted", "P2": "accepted", "P3": "accepted", "P4": "accepted", "P5": "accepted", "K1": "absent"}
    first = conversation("m", "plain", full)
    first["labels"]["second"] = first["labels"].pop("judge")
    second = conversation("m", "rules", full)
    second["id"] = "m|rules|1"
    second["labels"]["second"] = {key: dict(value, label="challenged") for key, value in second["labels"]["judge"].items()}
    rows = p.pair_rows([first, second], materials["premises"], ["judge", "second"])
    by_conversation = {row["conversation"]: row["judge"] for row in rows}
    assert by_conversation == {"m|plain|0": "second", "m|rules|1": "judge"}
    metrics = p.metrics_for([first, second], [], materials["premises"], ["judge", "second"], materials["config"])
    assert metrics["n_fallback_conversations"] == 1
    assert metrics["unchallenged_rate_rules"] == 1.0


def test_a_conversation_records_finish_reasons(materials):
    answers = [{"text": "uno", "finish_reason": "stop"}, {"text": "dos", "finish_reason": "length"}]
    item = p.run_conversation({"name": "m"}, "plain", 0, materials, lambda spec, messages, tag: answers.pop(0))
    assert item["finish"] == {"1": "stop", "2": "length"}
    assert p.metrics_for([item], [], materials["premises"], ["judge"], materials["config"])["n_truncated_replies"] == 1


def test_judge_json_is_found_after_leaked_reasoning():
    text = 'Wait, is {this} a label? I think "P1" is silent.\n```json\n{"P1": {"label": "silent"}, "P2": {"label": "accepted", "quote": "x"}}\n```'
    assert p.extract_labels(text)["P2"]["label"] == "accepted"
    bare = 'notes {"a": 1} then {"P1": {"label": "silent"}}'
    assert p.extract_labels(bare) == {"P1": {"label": "silent"}}
    assert p.extract_labels("no json here") == {}


class RecordingHTTP(FakeHTTP):
    def __init__(self, outcomes):
        super().__init__(outcomes)
        self.sent = []

    def __call__(self, url, key, body, timeout=120.0):
        self.sent.append(dict(body))
        return super().__call__(url, key, body, timeout)


def test_a_request_is_kept_under_the_provider_limit(monkeypatch, tmp_path):
    too_large = http_error(413, "Request too large ... (TPM): Limit 8000, Requested 8501, please reduce")
    fake = RecordingHTTP([too_large, reply("hola")])
    monkeypatch.setattr(p, "http_json", fake)
    provider = p.Provider("test", "https://example.test/v1", "k", 0.0, request_limit=8000, concurrency=1)
    messages = [{"role": "user", "content": "x" * 3500}]
    result = p.chat(provider, "m", messages, temperature=1.0, max_tokens=9000, cache_dir=tmp_path)
    first, second = fake.sent
    assert first["max_tokens"] == 8000 - p.estimate_tokens(messages) - 64
    assert second["max_tokens"] == first["max_tokens"] - 501 - 64
    assert result["max_tokens_sent"] == second["max_tokens"]
    again = p.chat(provider, "m", messages, temperature=1.0, max_tokens=9000, cache_dir=tmp_path)
    assert again["text"] == "hola" and len(fake.sent) == 2


def test_a_prompt_that_cannot_fit_is_refused_without_a_call(monkeypatch, tmp_path):
    fake = RecordingHTTP([])
    monkeypatch.setattr(p, "http_json", fake)
    provider = p.Provider("test", "https://example.test/v1", "k", 0.0, request_limit=8000, concurrency=1)
    with pytest.raises(RuntimeError, match="prompt too long"):
        p.chat(provider, "m", [{"role": "user", "content": "x" * 30000}], temperature=0.0, max_tokens=500, cache_dir=tmp_path)
    assert fake.sent == []


def test_rate_limit_waits_do_not_use_up_the_retries(monkeypatch, tmp_path):
    fake = FakeHTTP([http_error(429, "tokens per minute, try again in 0s")] * 12 + [reply("hola")])
    monkeypatch.setattr(p, "http_json", fake)
    monkeypatch.setattr(p.time, "sleep", lambda seconds: None)
    provider = p.Provider("test", "https://example.test/v1", "k", 0.0)
    result = p.chat(provider, "m", [{"role": "user", "content": "x"}], temperature=1.0, max_tokens=10, cache_dir=tmp_path)
    assert result["text"] == "hola" and fake.calls == 13


def test_complete_rate_leaves_out_cut_replies(materials):
    labels = {"P1": "accepted", "P2": "accepted", "P3": "accepted", "P4": "accepted", "P5": "challenged", "K1": "absent"}
    item = conversation("m", "plain", labels)
    item["finish"] = {"1": "stop", "2": "length"}
    metrics = p.metrics_for([item], [], materials["premises"], ["judge"], materials["config"])
    assert metrics["n_pairs_plain"] == 3
    assert metrics["n_pairs_complete_plain"] == 1
    assert metrics["unchallenged_rate_complete_plain"] == 1.0


def test_a_cache_only_call_never_reaches_the_network(monkeypatch, tmp_path):
    fake = FakeHTTP([])
    monkeypatch.setattr(p, "http_json", fake)
    provider = p.Provider("test", "https://example.test/v1", "k", 0.0)
    with pytest.raises(p.CacheMiss):
        p.chat(provider, "m", [{"role": "user", "content": "x"}], temperature=0.0, max_tokens=10, cache_dir=tmp_path, cache_only=True)
    assert fake.calls == 0


def test_grading_keeps_the_first_answer_when_the_retry_is_not_saved(materials):
    replies = {"1": "La encuesta no mide distancia.", "2": "Z06 no es mayoría."}
    first = json.dumps({"P1": {"label": "challenged", "quote": "La encuesta no mide distancia"}, "P5": {"label": "challenged", "quote": "texto inventado"}})
    calls = []

    def ask(spec, messages, tag):
        calls.append(tag)
        if tag.endswith(":0"):
            return first
        raise p.CacheMiss("not saved")

    labels = p.grade_conversation({"name": "early"}, {"id": "m|plain|0", "replies": replies}, materials, ask)
    assert labels["P1"]["valid"] is True and labels["P5"]["valid"] is False
    assert len(calls) == 2


def test_agreement_is_reported_for_every_other_judge(materials):
    full = {"P1": "accepted", "P2": "accepted", "P3": "accepted", "P4": "challenged", "P5": "accepted", "K1": "absent"}
    one = conversation("m", "plain", full)
    two = conversation("own", "rules", full)
    two["id"] = "own|rules|0"
    for item in (one, two):
        item["labels"]["second"] = {key: dict(value) for key, value in item["labels"]["judge"].items()}
    two["labels"]["second"]["P4"] = dict(two["labels"]["second"]["P4"], label="accepted")
    one["labels"]["early"] = {key: dict(value) for key, value in one["labels"]["judge"].items()}
    metrics = p.metrics_for(
        [one, two], [], materials["premises"], ["judge", "second"], materials["config"],
        extra_judges=["early"], own_models={"second": "own"},
    )
    second = metrics["agreement_by_judge"]["second"]
    assert second["n"] == 10 and second["agreement_binary"] == 0.9
    assert second["n_not_own"] == 5 and second["agreement_binary_not_own"] == 1.0
    assert metrics["agreement_by_judge"]["early"]["n"] == 5


def test_quote_matching_ignores_dashes_table_bars_and_ellipsis_gaps():
    reply = (
        "| Z06 (Caucel\u2011poniente exterior) concentra 78 estudiantes (30\u202f% del total) |\n"
        "| al menos un día | 195 (75 %) | gran oportunidad para ganar puntualidad. |"
    )
    assert p.quote_found("Z06 (Caucel-poniente exterior) concentra 78 estudiantes (30 % del total)", reply)
    assert p.quote_found("al menos un día: 195 (75 %) ... gran oportunidad para ganar puntualidad.", reply)
    assert not p.quote_found("gran oportunidad para ganar puntualidad ... al menos un día: 195", reply)
    assert not p.quote_found("concentra 79 estudiantes", reply)
    assert not p.quote_found("Z06", reply)
    assert p.quote_found("concentra 78", reply)


def test_face_value_rate_counts_labels_whose_quote_failed(materials):
    labels = {"P1": "accepted", "P2": "accepted", "P3": "accepted", "P4": "accepted", "P5": "accepted", "K1": "absent"}
    item = conversation("m", "rules", labels)
    item["labels"]["judge"]["P4"] = {"label": "challenged", "quote": "no está", "valid": False, "why": "quote not in reply"}
    metrics = p.metrics_for([item], [], materials["premises"], ["judge"], materials["config"])
    assert (metrics["n_pairs_rules"], metrics["unchallenged_rate_rules"]) == (2, 1.0)
    assert (metrics["n_pairs_face_rules"], metrics["unchallenged_rate_face_rules"]) == (3, 0.67)
