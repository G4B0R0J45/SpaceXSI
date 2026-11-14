# What this repository is for

This is a weekend lab notebook for the Apart Research AI x Epistemics sprint, 13 to 15 November 2026. A team picks one question about how AI handles claims, trust, or decisions, runs a small study, and writes a report that states only numbers and quotes already saved in the repo.

Apart scores that report. The repo, a demo, and a 3 to 5 minute video are optional. Every track is scored on the same three dimensions: impact and novelty, execution quality, and presentation clarity.

## What you hand in

- A PDF that uses the official template on the sprint Guidelines tab. This repository does not replace that template.
- At most 8 pages before references and appendices.
- An abstract of 150 to 250 words, plus author names and affiliations.
- The question, related work, method, results, and a Limitations and Dual-Use appendix.
- A clear split between this template, which is preexisting, and the work done during the sprint. Undisclosed prior work can disqualify a project.

Submissions close Sunday 15 November at 11:59 PM Anywhere on Earth. An unfinished report can be submitted. Invented results or references can disqualify a team.

## What the checker is protecting

Three files carry a result from the run to the page.

- `results/<study>.json` stores the run: who answered, the prompt hash, the time, n, and the metrics.
- `report/claims.json` ties each result sentence to a field in that JSON, or to an exact quote in `evidence/`.
- `report/REPORT.md` is the draft you paste into the official template.

`python -m epistemics check` fails when a sentence, a number, or a quote does not match those files. That is the habit the weekend is practicing. A judge should be able to follow the method and find the number in the run.

## Open these three files first

1. `study/PROTOCOL.md` is the demo question: one metric, one baseline, and a result that would make the claim false. Replace it with the team's question.
2. `results/fliprate.json` is a finished fixture run. The capitulation rate is 0.67 and the baseline is 0.0. Both respondents are scripted. The file shows the shape of a result, and it is not a finding about a deployed model.
3. `report/REPORT.md` repeats those sentences. `report/claims.json` points each one at the JSON field, or at the cafe source under `evidence/`.

The folders in `examples/` are four small versions of that same loop, one for each track. `examples/crux_mapper/map.html` is the disagreement map. Open it in a browser. There is no server. `examples/notes_delay/sample_notes.csv` is marked SYNTHETIC. It is not a Community Notes measurement.

## Install

Python 3.11 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m epistemics run all
python -m epistemics check
```

On macOS or Linux, activate with `source .venv/bin/activate` and use the same commands after that. `check` prints `OK` when the demo report still matches the saved files.

Leave `MODEL_API_KEY` empty to stay on fixtures. Copy `.env.example` to `.env` only when FlipRate or the citation binder should call an OpenAI-compatible model. The FlipRate baseline stays on the fixture either way.

## Friday to Sunday

Friday: `/scope-question`, then `/novelty-check`. Write one question into `study/PROTOCOL.md`.

Saturday: `/run-study` and `/bind-evidence`. Save a source under `evidence/` before the report cites it.

Sunday: `/draft-report`, `/dual-use-review`, and `/submission-check`. The skeptic writes `report/SKEPTIC.md` and leaves the result files alone.

A weekend that can score well replaces the toy items, runs that study, and keeps the checker green. The template stays labeled as preexisting work in the README and in the report.
