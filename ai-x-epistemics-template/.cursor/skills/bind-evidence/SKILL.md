---
name: bind-evidence
description: Saves a source under evidence/ before any citation is added to the report. Use when citing a page, paper, or quote, or when the user invokes /bind-evidence.
---

# Bind evidence

Do this before a citation enters `report/REPORT.md` or `report/claims.json`.

1. Put the source in `evidence/<slug>.md`.
2. Include the title, the URL or file the text came from, and the date it was saved.
3. Paste the excerpt the report will quote. The quote must be an exact contiguous copy. Do not tidy wording.
4. If the text cannot be retrieved, do not cite it. Say the source is missing.
5. Add a claim only after the file exists:

```json
{
  "id": "short-id",
  "text": "Sentence that appears in the report.",
  "quote": "exact words from the file",
  "evidence": "evidence/<slug>.md"
}
```

6. A numeric result is not a quote. Point those claims at `results/*.json` instead.
7. Do not create a source by paraphrasing a paper from memory.
