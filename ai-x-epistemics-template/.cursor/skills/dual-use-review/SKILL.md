---
name: dual-use-review
description: Fills the required Limitations and Dual-Use section with what the result does not show, misuse to persuade, and personal-data handling. Use before submission, or when the user invokes /dual-use-review.
---

# Dual-use review

The sprint requires this appendix. Edit the Limitations and Dual-Use sections of `report/REPORT.md`. Do not add a new research claim.

Cover three things in plain sentences:

- What the result does not establish. Name the metric, the n, and whether the respondents were fixtures, a live model, or real people.
- How the tool or the finding could be used to persuade rather than inform. A flip score can be misread as a way to lean on a model until it agrees. A short quote can make a source look more supportive than it is. State that limit. Do not write steps for pressuring a person, escalating a dispute, winning an argument, or concealing a source.
- Personal data. The template interviews and notes are fictional. If the team collected anything from a person, say how they asked, what was stored, and what will be deleted. If they collected nothing, say that.

Keep the section short enough that the report stays within 8 pages before references and appendices. When you finish, run `python -m epistemics check`.
