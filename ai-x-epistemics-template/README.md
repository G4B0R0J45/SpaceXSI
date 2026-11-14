# AI x Epistemics Cursor template

Read [GUIDE.md](GUIDE.md) first. It is the walkthrough for participants: what Apart scores, what the checker protects, and which three files to open. Cursor follows the same expectations from [AGENTS.md](AGENTS.md).

The figures in `report/REPORT.md` are demo output from committed fixtures. The notes CSV is synthetic. The runner, examples, fixtures, and this report skeleton are preexisting work. Say that in your own write-up if you build on them. Undisclosed prior work can disqualify a sprint project.

## Setup

Python 3.11 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m epistemics run all
python -m epistemics check
python -m pytest
```

On macOS or Linux, activate with `source .venv/bin/activate` and use the same commands after that.

`python -m epistemics check` prints `OK` when `report/claims.json` matches the result files and the saved cafe quote. It also reminds you to paste the report into the official PDF template on the sprint Guidelines tab.

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

## What to replace

`study/PROTOCOL.md` is a demo question. Replace it with one question your team can finish by Sunday. Keep one metric, one baseline, and a result that would make the claim false. Then replace the toy items. Run `python -m epistemics check` before you export the PDF.
