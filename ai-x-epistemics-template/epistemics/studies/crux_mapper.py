"""Crux mapper: shared claims, cruxes, and within-person inconsistencies from marked transcripts."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from epistemics.run import build_result, find_root, write_result

STUDY = "crux_mapper"
THRESHOLD = 0.25
CLAIM_LINE = re.compile(r"^CLAIM:\s*(.+?)\s*\|\s*P:\s*([0-9]*\.?[0-9]+)\s*$", re.IGNORECASE)
PROMPT = "Deterministic CLAIM and P parser. No model call."


def parse_transcript(text: str) -> list[dict]:
    statements: list[dict] = []
    for line in text.splitlines():
        match = CLAIM_LINE.match(line.strip())
        if not match:
            continue
        statements.append({"claim": match.group(1).strip(), "p": float(match.group(2))})
    return statements


def normalize(claim: str) -> str:
    return re.sub(r"\s+", " ", claim).strip().casefold()


def latest_by_claim(statements: list[dict]) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for statement in statements:
        latest[normalize(statement["claim"])] = statement
    return latest


def inconsistencies(statements: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for statement in statements:
        grouped.setdefault(normalize(statement["claim"]), []).append(statement)
    found: list[dict] = []
    for key, group in grouped.items():
        probs = [item["p"] for item in group]
        if max(probs) - min(probs) >= THRESHOLD:
            found.append(
                {
                    "claim": group[0]["claim"],
                    "key": key,
                    "probabilities": probs,
                    "spread": round(max(probs) - min(probs), 2),
                }
            )
    return found


def build_map(person_a: list[dict], person_b: list[dict]) -> dict:
    latest_a = latest_by_claim(person_a)
    latest_b = latest_by_claim(person_b)
    shared: list[dict] = []
    cruxes: list[dict] = []
    only_a: list[dict] = []
    only_b: list[dict] = []
    for key, left in latest_a.items():
        right = latest_b.get(key)
        if right is None:
            only_a.append({"claim": left["claim"], "p": left["p"]})
            continue
        gap = round(abs(left["p"] - right["p"]), 2)
        row = {
            "claim": left["claim"],
            "p_a": left["p"],
            "p_b": right["p"],
            "gap": gap,
        }
        if gap >= THRESHOLD:
            cruxes.append(row)
        else:
            shared.append(row)
    for key, right in latest_b.items():
        if key not in latest_a:
            only_b.append({"claim": right["claim"], "p": right["p"]})
    inconsistent = {
        "person_a": inconsistencies(person_a),
        "person_b": inconsistencies(person_b),
    }
    return {
        "threshold": THRESHOLD,
        "shared": shared,
        "cruxes": cruxes,
        "only_a": only_a,
        "only_b": only_b,
        "inconsistencies": inconsistent,
    }


def render_html(disagreement: dict) -> str:
    payload = json.dumps(disagreement, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Disagreement map</title>
  <style>
    :root {{
      color-scheme: light dark;
      --ink: #1c1915;
      --paper: #f6f3ec;
      --line: #d9d1c3;
      --shared: #1f6b4a;
      --crux: #8a4b08;
      --gap: #7a2e2e;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --ink: #f3efe6;
        --paper: #1c1915;
        --line: #3a342c;
        --shared: #8fceb0;
        --crux: #e2b36a;
        --gap: #f0a3a3;
      }}
    }}
    body {{
      margin: 0;
      font: 16px/1.5 "Segoe UI", sans-serif;
      background: var(--paper);
      color: var(--ink);
    }}
    main {{
      max-width: 44rem;
      margin: 0 auto;
      padding: 2rem 1.25rem 3rem;
    }}
    .banner {{
      margin: 0 0 1rem;
      padding: 0.6rem 0.8rem;
      border: 1px solid var(--line);
      border-radius: 6px;
    }}
    h1 {{ font-size: 1.8rem; line-height: 1.2; margin: 0 0 0.4rem; }}
    h2 {{ font-size: 1.1rem; margin: 1.6rem 0 0.4rem; }}
    ul {{ padding-left: 1.2rem; }}
    li {{ margin: 0.35rem 0; }}
    .shared h2 {{ color: var(--shared); }}
    .crux h2 {{ color: var(--crux); }}
    .gap h2 {{ color: var(--gap); }}
  </style>
</head>
<body>
  <main>
    <p class="banner">Template example. The interviews are fictional. This page is not a field finding.</p>
    <h1>Disagreement map</h1>
    <p>A crux is a claim both people stated whose probabilities differ by at least {disagreement["threshold"]}. Shared claims differ by less than that. An inconsistency is the same person stating one claim at probabilities that spread by at least {disagreement["threshold"]}.</p>
    {render_shared(disagreement)}
    {render_cruxes(disagreement)}
    {render_inconsistencies(disagreement)}
    {render_only("Only person A", disagreement["only_a"])}
    {render_only("Only person B", disagreement["only_b"])}
  </main>
  <script type="application/json" id="disagreement-map">
{payload}
  </script>
</body>
</html>
"""


def render_shared(disagreement: dict) -> str:
    items = disagreement["shared"]
    if not items:
        body = "<p>None.</p>"
    else:
        rows = "".join(
            f"<li>{html.escape(row['claim'])}: A {row['p_a']}, B {row['p_b']} (gap {row['gap']})</li>"
            for row in items
        )
        body = f"<ul>{rows}</ul>"
    return f'<section class="shared"><h2>Shared ground</h2>{body}</section>'


def render_cruxes(disagreement: dict) -> str:
    items = disagreement["cruxes"]
    if not items:
        body = "<p>None.</p>"
    else:
        rows = "".join(
            f"<li>{html.escape(row['claim'])}: A {row['p_a']}, B {row['p_b']} (gap {row['gap']})</li>"
            for row in items
        )
        body = f"<ul>{rows}</ul>"
    return f'<section class="crux"><h2>Cruxes</h2>{body}</section>'


def render_inconsistencies(disagreement: dict) -> str:
    blocks = []
    for label, key in (("Person A", "person_a"), ("Person B", "person_b")):
        rows = disagreement["inconsistencies"][key]
        if not rows:
            blocks.append(f"<h3>{label}</h3><p>None.</p>")
            continue
        listed = "".join(
            f"<li>{html.escape(row['claim'])}: probabilities {', '.join(str(p) for p in row['probabilities'])}</li>"
            for row in rows
        )
        blocks.append(f"<h3>{label}</h3><ul>{listed}</ul>")
    return f'<section class="gap"><h2>Within-person inconsistencies</h2>{"".join(blocks)}</section>'


def render_only(title: str, rows: list[dict]) -> str:
    if not rows:
        body = "<p>None.</p>"
    else:
        listed = "".join(
            f"<li>{html.escape(row['claim'])}: {row['p']}</li>" for row in rows
        )
        body = f"<ul>{listed}</ul>"
    return f"<section><h2>{html.escape(title)}</h2>{body}</section>"


def load_people(root: Path) -> tuple[list[dict], list[dict]]:
    folder = root / "examples" / "crux_mapper"
    person_a = parse_transcript((folder / "person_a.txt").read_text(encoding="utf-8"))
    person_b = parse_transcript((folder / "person_b.txt").read_text(encoding="utf-8"))
    return person_a, person_b


def evaluate(root: Path | None = None) -> dict:
    root = root or find_root()
    person_a, person_b = load_people(root)
    disagreement = build_map(person_a, person_b)
    inconsistency_count = len(disagreement["inconsistencies"]["person_a"]) + len(
        disagreement["inconsistencies"]["person_b"]
    )
    return build_result(
        study=STUDY,
        provider="fixture",
        model="claim-parser",
        prompt_template=PROMPT,
        n=2,
        items=[
            {"id": "person_a", "prompt_id": "person_a", "raw_output": json.dumps(person_a), "grade": person_a},
            {"id": "person_b", "prompt_id": "person_b", "raw_output": json.dumps(person_b), "grade": person_b},
        ],
        metrics={
            "crux_count": len(disagreement["cruxes"]),
            "shared_count": len(disagreement["shared"]),
            "inconsistency_count": inconsistency_count,
            "threshold": THRESHOLD,
        },
        baseline=None,
    ) | {"disagreement": disagreement}


def run(root: Path | None = None) -> dict:
    root = root or find_root()
    payload = evaluate(root)
    disagreement = payload.pop("disagreement")
    write_result(root, payload)
    html_path = root / "examples" / "crux_mapper" / "map.html"
    html_path.write_text(render_html(disagreement), encoding="utf-8")
    (root / "examples" / "crux_mapper" / "disagreement.json").write_text(
        json.dumps(disagreement, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload
