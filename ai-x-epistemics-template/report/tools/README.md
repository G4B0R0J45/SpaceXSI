# Report tools

These scripts turn the saved results into the report. They read only files in this repository.

1. `python report/tools/write_report.py .` writes `report/REPORT.md`, `report/claims.json`, `report/blocks.json` and `evidence/ejemplos-de-respuestas.md` from `results/premises.json` and `results/commute.json`.
2. `python report/tools/write_notes.py .` rewrites `report/SKEPTIC.md` and `report/DEMO.md` from the same files.
3. Unzip `report/submission.docx` (the official template, as first submitted) into a folder, then run `python report/tools/build_docx.py . <that folder> report/submission-final.docx`. Export that file to PDF from Word.
4. `python report/tools/make_labeling_page.py study/premises/human_sample.json <out.html>` builds the blind labeling page.

Run `python -m epistemics check` after step 1.
