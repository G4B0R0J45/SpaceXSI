---
name: draft-report
description: Drafts the sprint report, claims file, and a short demo outline from saved results. Use on Sunday, when writing the report, or when the user invokes /draft-report.
---

# Draft the report

Delegate the draft to the report-writer subagent when you can. Otherwise follow these steps yourself.

1. Read `study/PROTOCOL.md`, `results/*.json`, and any file under `evidence/` the team will quote.
2. Update `report/REPORT.md` so it has Authors, Abstract, Question, Related Work, Method, Results, Limitations, Dual-Use, and Preexisting Work.
3. Keep the abstract between 150 and 250 words. Say what the run does not establish.
4. For every result sentence, add an object to `report/claims.json` whose `text` is that sentence. Copy numeric values from the JSON pointer. Copy quotes from evidence files.
5. Related Work may name only MASK, DarkBench, SycEval, ELEPHANT, ForecastBench, Community Notes, the Habermas Machine, and the Forethought sketches, plus files in `evidence/`.
6. Call fixture output and `sample_notes.csv` demo data when those are the sources.
7. Write `report/DEMO.md` as a 3 to 5 minute outline that cites the same claims and no others.
8. Run `python -m epistemics check`. If it fails, change the words or drop the claim. Do not edit a number inside `results/` to make the checker pass.
9. Leave the Dual-Use section for `/dual-use-review` if it is only a placeholder, and say so.
