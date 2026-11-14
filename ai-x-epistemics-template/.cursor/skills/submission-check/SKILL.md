---
name: submission-check
description: Runs the submission checker and explains each failure in plain language. Use before submitting, after editing the report, or when the user invokes /submission-check.
---

# Submission check

1. Run `python -m epistemics check` from the repository root.
2. If the exit code is 0, say the claims match the files. Repeat any warnings, including abstract length. Remind the team to paste the report into the official Apart PDF template and to label preexisting template code.
3. If the exit code is not 0, quote each error and say which file to change. A missing source means the path in `claims.json` is wrong or the study was not run. A value mismatch means the sentence and the JSON disagree. A quote error means those words are not in the evidence file. A missing heading means the report dropped a required section.
4. Repair a mismatch by editing the report or the claim so it matches the saved file, or by re-running the study. Do not change `results/*.json` by hand. Do not delete a failing claim and leave the sentence in the report.
5. After a skeptic pass, the note belongs in `report/SKEPTIC.md`. Ask the skeptic subagent to write it from the claims. Do not treat the skeptic note as a new result.
