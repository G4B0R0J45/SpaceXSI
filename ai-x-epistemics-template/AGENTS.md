# AI x Epistemics sprint template

This repository is preexisting scaffolding for the Apart Research sprint running Friday 13 November through Sunday 15 November 2026. Submissions close Sunday 15 November at 11:59 PM Anywhere on Earth. The submission is a research report, pasted into the official PDF template from the sprint Guidelines tab. Maximum 8 pages before references and appendices. The abstract is 150 to 250 words. A Limitations and Dual-Use section is required. Made-up results or references can disqualify a team.

Judges score every track on impact and novelty, execution quality, and presentation clarity. Tracks orient the project. They do not change the rubric.

## Steer the team

When a participant is lost, or asks what this repo is for, walk through [GUIDE.md](GUIDE.md) from the top. Do not invent a study for them.

Apart scores a research report in the official PDF template. A repo, a demo, and a video are optional. A weekend that can score well has one question, one metric, one baseline, a result that would make the claim false, and a written limit on what the result does not show. The committed fixtures and the synthetic notes file demonstrate that shape. They are demos.

When the work drifts, steer like this:

- Park a second project under "Not this weekend."
- Ask for the metric before writing an interface that does not measure anything.
- Refuse a result sentence until `results/` contains the number.
- Send a citation through `/bind-evidence` when the source is not already under `evidence/`.
- If the team treats the fixture rate 0.67 as a result about real models, say it is the demo and point them at replacing `study/PROTOCOL.md`.

## Weekend path

Friday: `/scope-question` writes one question, one metric, one baseline, n, and a falsifier into `study/PROTOCOL.md`. Then `/novelty-check`.

Saturday: `/run-study` runs one example or the team's study. `/bind-evidence` saves every source under `evidence/` before it is cited.

Sunday: `/draft-report` fills `report/REPORT.md` and `report/claims.json` from files that already exist. `/dual-use-review` fills the required appendix. `/submission-check` runs `python -m epistemics check`. The skeptic agent writes `report/SKEPTIC.md`.

## Commands

```bash
python -m epistemics run all
python -m epistemics run fliprate
python -m epistemics check
```

An empty `MODEL_API_KEY` uses committed fixtures. Copy `.env.example` to `.env` only when a study should call a model. The baseline in FlipRate stays on fixtures either way.

## Repo map

- `epistemics/` is the runner, the checker, and the four study graders.
- `examples/fliprate/` is Track 1. Capitulation versus a warranted update.
- `examples/citation_binder/` is Track 2. A quote must be a substring of a saved source.
- `examples/crux_mapper/` is Track 3. Open `map.html`.
- `examples/notes_delay/` is Track 4. The CSV is synthetic.
- `results/` is generated JSON. Cite it. Do not hand-edit metrics.
- `report/claims.json` binds each result sentence to a JSON pointer or a quote.
- `study/PROTOCOL.md` is the one question for this weekend.

## Evidence rules

- Every number in `report/REPORT.md` needs a matching entry in `report/claims.json`.
- The claim's `text` must appear in the report, and its `value` must match the JSON pointer.
- A quote must be an exact substring of the file named in `evidence`.
- Record provider, model, prompt hash, timestamp, and n in the result file. The runner does this.
- Do not invent papers, metrics, quotes, or participants.
- Do not add procedures for pressuring a person, escalating a dispute, or hiding a source. Measure benign cases and say how the work could be misused.

## Preexisting work

The runner, examples, fixtures, fictional sources, synthetic CSV, report skeleton, skills, and agents shipped with this template are preexisting. Sprint work is what the team changes after cloning. Label that split in the README and in the report. Undisclosed prior work can disqualify a project.

Fixture numbers and the synthetic notes file are demo data. They are not findings about deployed models or about Community Notes.
