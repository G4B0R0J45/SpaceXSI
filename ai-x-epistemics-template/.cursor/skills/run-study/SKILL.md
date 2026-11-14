---
name: run-study
description: Runs one sprint study and summarizes only the metrics in the result JSON. Use on Saturday, when executing an example, or when the user invokes /run-study.
---

# Run a study

1. Confirm `study/PROTOCOL.md` names one metric and one baseline. If it does not, stop and use `/scope-question`.
2. Run `python -m epistemics run <study>` where study is `fliprate`, `citation_binder`, `crux_mapper`, `notes_delay`, or the team's module wired into `epistemics/studies`. `python -m epistemics run all` regenerates the four examples.
3. An empty `MODEL_API_KEY` keeps the run on fixtures. That is the right default for a demo. Set the key in `.env` only when the protocol says a live model is the treatment. FlipRate's baseline stays on the fixture either way.
4. Open `results/<study>.json`. Summarize provider, model, prompt hash, n, and the metric fields that are actually present.
5. Do not invent a rate, a p-value, or a model name. If a field is missing, say it was not run.
6. If the notes study still points at `sample_notes.csv`, call the output synthetic in the summary.
