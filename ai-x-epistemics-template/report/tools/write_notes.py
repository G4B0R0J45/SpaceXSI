"""Updates README.md, report/SKEPTIC.md and report/DEMO.md for the premise study, from the saved results.

Usage: python write_docs2.py <repo root>
"""

import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
P = json.loads((root / "results" / "premises.json").read_text(encoding="utf-8"))
C = json.loads((root / "results" / "commute.json").read_text(encoding="utf-8"))
m, cm = P["metrics"], C["metrics"]


def f2(value) -> str:
    return "n/a" if value is None else (f"{value:.2f}" if isinstance(value, float) else str(value))


def put(path: str, text: str) -> None:
    (root / path).write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))


def edit(path: str, pairs) -> None:
    text = (root / path).read_bytes().decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        if old not in text and new in text:
            continue
        assert text.count(old) == 1, (path, old[:60], text.count(old))
        text = text.replace(old, new)
    put(path, text)


agree = m.get("agreement_by_judge", {})
human = f"{f2(m.get('human_agreement_binary'))} on {m.get('n_human')} pairs" if m.get("n_human") else "not yet measured"
lines = [
    "# Skeptic note",
    "",
    "This note is about the premise study in `results/premises.json`. It does not edit the results. Every number here is copied from that file or from `results/commute.json`.",
    "",
    "## What would flip the conclusion",
    "",
    f"The main claim is that, without rules, replies left a share of {f2(m['unchallenged_rate_plain'])} of the unsupported premises unchallenged. It rests on one model's labels. The blind hand labels agreed with the metric's labels on whether a premise was challenged at a rate of {human}. If the judge reads \"accepted\" into replies that only repeat a number, the share is too high. The rubric tries to separate those cases per premise, and the line is still a judgment call.",
    "",
    f"The rules claim is a difference of {f2(m['unchallenged_difference'])}, with a 95% interval from {f2(m['unchallenged_difference_ci95_low'])} to {f2(m['unchallenged_difference_ci95_high'])}. That interval covers resampling of these conversations only. Another scenario, another user's wording, or other models could move it either way. AGENTS.md was written for this repository, not for advice, so the test is of one particular rules file.",
    "",
    "## Weaker points",
    "",
    f"- Each model held {P['settings']['k']} conversations per condition, at temperature 1. The models are free-tier models, not the chat apps a student would open.",
    "- The primary judge planned in the protocol ran out of daily quota during the run and was replaced before its successor labeled anything. The change is dated in the protocol, and the earlier judge's labels are kept as an agreement check.",
    "- The pilot changed token limits after the pilot outcome was known. The rubric, premises and metric did not change.",
    "- P1 was moved out of the primary metric after reading the stimulus and before the run, because its truth depends on reading zones as distance.",
    f"- {m['n_truncated_replies']} replies were cut at the token limit. The rate without them is reported, and a cut reply can hide a late caveat.",
    "- The judge does not see the system prompt, but a reply in the rules condition can reveal it by talking about evidence files or claims.",
    "- The second judge is also one of the four evaluated models, so its agreement is reported with and without its own conversations.",
    "",
    "## What still stands",
    "",
    f"The survey supports one of the five premises and not the others: {f2(cm['share_willing_yes'])} said they would use a meeting point, Z06 holds {f2(cm['share_z06'])} of the sample, and the form asks nothing about free seats or the cause of arriving after 07:00. Each sentence in the report's result lists points at a saved number through `report/claims.json`, and every reply and label behind the rates is in `results/premises.json` for anyone to reread.",
    "",
]
put("report/SKEPTIC.md", "\n".join(lines))

demo = [
    "# Demo outline",
    "",
    "Three to five minutes. Use the claims in `report/claims.json`. Do not add a number that is not in that file.",
    "",
    "1. Read the author's first message aloud from `study/premises/messages.json`, and show the survey summary in `study/premises/data_block.md` (about 40 seconds).",
    f"2. Show what the survey says about each premise: {f2(cm['share_willing_yes'])} said yes to a meeting point, Z06 holds {f2(cm['share_z06'])}, and the form never asks about free seats or the cause of lateness (about 40 seconds).",
    f"3. Open `results/premises.json` and read the main result: without rules, {f2(m['unchallenged_rate_plain'])} of the unsupported premises were left unchallenged; with AGENTS.md as system prompt, {f2(m['unchallenged_rate_rules'])} (about 45 seconds).",
    "4. Read two example passages from `evidence/ejemplos-de-respuestas.md`, one where a premise was accepted and one where it was challenged (about 45 seconds).",
    "5. Show the quote check: open one conversation in `results/premises.json`, find the judge's quote inside the reply, and run `python -m epistemics check` (about 40 seconds).",
    "6. Close with the limits: one scenario, four free models, a model as judge checked by a second judge and by hand, and the judge change during the run (about 30 seconds).",
    "",
]
put("report/DEMO.md", "\n".join(demo))
print("README, SKEPTIC and DEMO updated")
