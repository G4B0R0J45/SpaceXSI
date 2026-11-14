---
name: novelty-check
description: States what a sprint study adds beyond the named prior art, without inventing papers. Use after scoping, when checking novelty, or when the user invokes /novelty-check.
---

# Novelty check

Write `study/NOVELTY.md`. Say what is new this weekend in one paragraph, and list the prior art the study does not rerun.

Use only these names unless a source has been saved under `evidence/`:

- Track 1, model epistemics: MASK, DarkBench, SycEval, ELEPHANT, ForecastBench, and Forethought's epistemic-virtue sketches. FlipRate in this repo is a three-item fixture, not those benchmarks.
- Track 2, trust infrastructure: C2PA, Community Notes, and the Forethought note that early tools accumulate trust they may not deserve.
- Track 3, epistemic products: the Habermas Machine, which drafts agreement, and Forethought's angels-on-the-shoulder sketches. The crux mapper only maps disagreement.
- Track 4, open track: the Forethought adoption and procurement notes, and the public Community Notes dataset. `examples/notes_delay/sample_notes.csv` is synthetic.

Do not add a paper, author, year, or quotation that is not in the list above or in `evidence/`. If the team needs another source, use `/bind-evidence` first.

End with the sentence: "Work already in this repository is preexisting. The new work this weekend is: " and leave a concrete fill-in the team can edit.
