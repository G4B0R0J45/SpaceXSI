# Demo outline

Three to five minutes. Use the claims in `report/claims.json`. Do not add a number that is not in that file.

1. Read the author's first message aloud from `study/premises/messages.json`, and show the survey summary in `study/premises/data_block.md` (about 40 seconds).
2. Show what the survey says about each premise: 0.62 said yes to a meeting point, Z06 holds 0.30, and the form never asks about free seats or the cause of lateness (about 40 seconds).
3. Open `results/premises.json` and read the main result: without rules, 0.98 of the unsupported premises were left unchallenged; with AGENTS.md as system prompt, 0.88 (about 45 seconds).
4. Read two example passages from `evidence/ejemplos-de-respuestas.md`, one where a premise was accepted and one where it was challenged (about 45 seconds).
5. Show the quote check: open one conversation in `results/premises.json`, find the judge's quote inside the reply, and run `python -m epistemics check` (about 40 seconds).
6. Close with the limits: one scenario, four free models, a model as judge checked by a second judge and by hand, and the judge change during the run (about 30 seconds).
