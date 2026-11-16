# Skeptic note

This note is about the premise study in `results/premises.json`. It does not edit the results. Every number here is copied from that file or from `results/commute.json`.

## What would flip the conclusion

The main claim is that, without rules, replies left a share of 0.98 of the unsupported premises unchallenged. It rests on one model's labels. The blind hand labels agreed with the metric's labels on whether a premise was challenged at a rate of not yet measured. If the judge reads "accepted" into replies that only repeat a number, the share is too high. The rubric tries to separate those cases per premise, and the line is still a judgment call.

The rules claim is a difference of 0.10, with a 95% interval from 0.02 to 0.20. That interval covers resampling of these conversations only. Another scenario, another user's wording, or other models could move it either way. AGENTS.md was written for this repository, not for advice, so the test is of one particular rules file.

## Weaker points

- Each model held 5 conversations per condition, at temperature 1. The models are free-tier models, not the chat apps a student would open.
- The primary judge planned in the protocol ran out of daily quota during the run and was replaced before its successor labeled anything. The change is dated in the protocol, and the earlier judge's labels are kept as an agreement check.
- The pilot changed token limits after the pilot outcome was known. The rubric, premises and metric did not change.
- P1 was moved out of the primary metric after reading the stimulus and before the run, because its truth depends on reading zones as distance.
- 24 replies were cut at the token limit. The rate without them is reported, and a cut reply can hide a late caveat.
- The judge does not see the system prompt, but a reply in the rules condition can reveal it by talking about evidence files or claims.
- The second judge is also one of the four evaluated models, so its agreement is reported with and without its own conversations.

## What still stands

The survey supports one of the five premises and not the others: 0.62 said they would use a meeting point, Z06 holds 0.30 of the sample, and the form asks nothing about free seats or the cause of arriving after 07:00. Each sentence in the report's result lists points at a saved number through `report/claims.json`, and every reply and label behind the rates is in `results/premises.json` for anyone to reread.
