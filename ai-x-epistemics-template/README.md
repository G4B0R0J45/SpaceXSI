# Do chatbots check a student's premises? Built on the AI x Epistemics Cursor template

The main sprint study in this clone asks whether chatbots let a student's unsupported premises stand when the survey that tests them is in the same message, with and without this template's AGENTS.md as the system prompt. `epistemics/studies/premises.py` runs it and writes `results/premises.json`. The ground truth is the team's survey count: `epistemics/studies/commute.py` joins the preexisting survey to the preexisting macrozones and writes `results/commute.json`. The report is [report/REPORT.md](report/REPORT.md). The runner, the four examples, the fixtures, and most of this README shipped with the template and are preexisting scaffolding.

Read [GUIDE.md](GUIDE.md) first. It is the walkthrough for participants: what Apart scores, what the checker protects, and which three files to open. Cursor follows the same expectations from [AGENTS.md](AGENTS.md).

The figures in `report/REPORT.md` come from `results/premises.json` and `results/commute.json`. They are not fixture output. The four example studies still run on committed fixtures, and their result files are demo output, not findings. The notes CSV is synthetic.

## Sprint work and prior work

| What | Where | When |
| --- | --- | --- |
| Premise study: code, inputs, tests | `epistemics/studies/premises.py`, `study/premises/`, `tests/test_premises.py` | Sprint, 15 November 2026 |
| Premise study result | `results/premises.json`; `results/premises_fixture.json` is a scripted offline demo, not a finding | Sprint |
| Evidence notes for the premise study | `evidence/sesion-asistente.md`, `evidence/lista-de-lectura-sprint.md` | Sprint |
| Join of the survey to the macrozones, and its tests | `epistemics/studies/commute.py`, `tests/test_commute.py` | Sprint, 13 to 15 November 2026 |
| Result files | `results/commute.json`, and `results/commute_first_submission.json` for the first submitted version | Sprint |
| Protocol, report, claims, evidence notes | `study/PROTOCOL.md`, `report/`, `evidence/encuesta-traslado-upy.md`, `evidence/macrozonas-upy.md` | Sprint |
| Registering the study in the runner | small edits in `epistemics/run.py`, `epistemics/__main__.py`, `epistemics/studies/__init__.py` | Sprint |
| Survey responses | Not published. The raw CSV stays with the team; `results/commute.json` holds the saved count | Prior team work, collected 6 to 13 November 2026 |
| Macrozones, map, travel-time PDF | `study/sources/*.csv`, `../Macrozonas/` | Prior work, Proyecto Integrador I, Equipo 5, October 2026 |
| Runner, checker, four examples, fixtures, Cursor skills and agents | everything else | Template, preexisting |

Undisclosed prior work can disqualify a sprint project, so the same split is in the report.

## Setup

Python 3.11 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m epistemics run premises
python -m epistemics check
python -m pytest
```

On macOS or Linux, activate with `source .venv/bin/activate` and use the same commands after that.

`python -m epistemics run premises` needs free API keys in `.env`: `GROQ_API_KEY` and `GEMINI_API_KEY`. Every model call is cached under `.cache/`, which git ignores, so a rerun with the same settings reuses the same replies. Without keys it runs scripted fixtures and writes `results/premises_fixture.json`, a demo and not a finding. The raw survey is private, so `python -m epistemics run commute` only works with the team's copy at `study/sources/encuesta_traslado_upy.csv`; the saved count is `results/commute.json`, and its tests skip when the file is absent. `python -m epistemics run all` runs only the four template examples and leaves both sprint results alone. `python -m epistemics check` prints `OK` when every sentence in `report/claims.json` appears in the report and matches a result file or a saved quote. It also reminds you to paste the report into the official PDF template on the sprint Guidelines tab.

## Open the examples

| Folder | Track | What the demo does |
| --- | --- | --- |
| `examples/fliprate/` | Model epistemics | Capitulation rate 0.67 on a fixture, against a baseline of 0.0 |
| `examples/citation_binder/` | Trust infrastructure | Keeps a verdict only when the quote is in the source file |
| `examples/crux_mapper/` | Epistemic products | Writes `map.html` from two fictional interviews |
| `examples/notes_delay/` | Open track | Median delay on five synthetic rows |

Open `examples/crux_mapper/map.html` in a browser. There is no server.

Copy `.env.example` to `.env` and set `MODEL_API_KEY` only when you want FlipRate or the citation binder to call an OpenAI-compatible model. The FlipRate baseline stays on the fixture. Leave the key empty and the run stays offline.

## Weekend commands in Cursor

Friday: `/scope-question`, then `/novelty-check`.

Saturday: `/run-study` and `/bind-evidence`.

Sunday: `/draft-report`, `/dual-use-review`, and `/submission-check`.

The methodologist and skeptic agents are in `.cursor/agents/`. The skeptic writes `report/SKEPTIC.md` and does not edit the results. [GUIDE.md](GUIDE.md) is the human walkthrough. [AGENTS.md](AGENTS.md) is what Cursor follows in every chat.

## What changed after the first submission

The first submission reported the survey count alone. This version adds the premise study and uses the count as its ground truth. `study/PROTOCOL.md` holds the premise study's protocol, written before the first model call, with dated sections for the changes after the pilot, the judge change during the run, and the quote matching. The survey protocol, with its own corrections, is the annex. `study/premises/frozen_*.json` hold file hashes taken at each step. The raw survey and the event pass were removed from the repository on 15 November 2026. [report/SKEPTIC.md](report/SKEPTIC.md) lists what would flip each conclusion.
