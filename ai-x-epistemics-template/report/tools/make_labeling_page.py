"""Builds a self-contained page for the blind human check.

Usage: python make_labeling_page.py <human_sample.json> <out.html>
The page shows one (reply, premise) pair at a time, never the model or the condition, and ends with
the labels as JSON to copy into study/premises/human_labels.json.
"""

import html
import json
import sys
from pathlib import Path

sample = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = Path(sys.argv[2])

PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Calificación a ciegas</title>
<style>
  :root { --bg:#fbfaf7; --ink:#1d1b16; --muted:#6b665c; --line:#d9d4c7; --card:#ffffff; --accent:#4b2e83; --ok:#1f6f43; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#16151a; --ink:#ece9e1; --muted:#a39e92; --line:#3a3742; --card:#1f1e25; --accent:#b9a2f0; --ok:#7fd3a3; }
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 Georgia, 'Times New Roman', serif; }
  main { max-width: 860px; margin: 0 auto; padding: 20px 16px 80px; }
  h1 { font-size: 22px; margin: 8px 0 4px; }
  .muted { color: var(--muted); font-size: 14px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:14px 16px; margin:12px 0; }
  .premise { font-size: 18px; font-weight: bold; color: var(--accent); }
  .label { text-transform: uppercase; letter-spacing: .06em; font: 12px/1.4 system-ui, sans-serif; color: var(--muted); margin-bottom: 4px; }
  .reply { white-space: pre-wrap; font: 15px/1.55 system-ui, -apple-system, 'Segoe UI', sans-serif; max-height: 55vh; overflow:auto; }
  details { margin: 6px 0; } summary { cursor: pointer; color: var(--muted); font: 14px system-ui, sans-serif; }
  .choices { display:grid; grid-template-columns: repeat(3, 1fr); gap:8px; position: sticky; bottom: 0; background:var(--bg); padding: 10px 0; }
  @media (max-width: 640px) { .choices { grid-template-columns: 1fr; } }
  button { font: 15px/1.3 system-ui, sans-serif; padding: 10px 12px; border-radius: 8px; border:1px solid var(--line); background:var(--card); color:var(--ink); cursor:pointer; text-align:left; }
  button b { display:block; }
  button small { color: var(--muted); }
  button.sel { border-color: var(--accent); outline: 2px solid var(--accent); }
  .nav { display:flex; gap:8px; align-items:center; justify-content:space-between; margin-top: 8px; }
  .nav button { text-align:center; }
  textarea { width:100%; height: 180px; font: 13px/1.4 ui-monospace, Consolas, monospace; background:var(--card); color:var(--ink); border:1px solid var(--line); border-radius:8px; padding:10px; }
  .done { color: var(--ok); font-weight: bold; }
</style>
</head>
<body>
<main>
  <h1>Calificación a ciegas</h1>
  <p class="muted">Cada pantalla muestra una premisa del estudiante y la respuesta de un asistente. No se muestra qué modelo respondió ni en qué condición. Elige una etiqueta y avanza. Se guarda en este navegador mientras trabajas.</p>
  <div id="app"></div>
</main>
<script>
const SAMPLE = __SAMPLE__;
const KEY = "premises-human-labels-" + SAMPLE.length + "-" + SAMPLE[0].pair + SAMPLE[SAMPLE.length - 1].reply.length;
let labels = {};
try { labels = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { labels = {}; }
let at = 0;
const first = SAMPLE.findIndex(function (row) { return !labels[row.pair]; });
at = first === -1 ? SAMPLE.length : first;
function save() { try { localStorage.setItem(KEY, JSON.stringify(labels)); } catch (e) {} }
function el(tag, cls, text) { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; }
function render() {
  const app = document.getElementById("app");
  app.textContent = "";
  const count = Object.keys(labels).length;
  app.appendChild(el("p", "muted", "Avance: " + count + " de " + SAMPLE.length));
  if (at >= SAMPLE.length) {
    app.appendChild(el("p", "done", count === SAMPLE.length ? "Terminaste. Copia este texto y pégalo en el chat." : "Faltan pares por etiquetar."));
    const area = el("textarea");
    area.value = JSON.stringify(labels);
    area.readOnly = true;
    app.appendChild(area);
    const row = el("div", "nav");
    const copy = el("button", "", "Copiar etiquetas");
    copy.onclick = function () { area.select(); try { navigator.clipboard.writeText(area.value); copy.textContent = "Copiado"; } catch (e) { document.execCommand("copy"); } };
    const back = el("button", "", "Revisar desde el inicio");
    back.onclick = function () { at = 0; render(); };
    row.appendChild(back); row.appendChild(copy);
    app.appendChild(row);
    return;
  }
  const item = SAMPLE[at];
  const top = el("div", "card");
  top.appendChild(el("div", "label", "Par " + (at + 1) + " de " + SAMPLE.length + " · premisa del estudiante"));
  top.appendChild(el("div", "premise", "«" + item.premise + "»"));
  const shows = el("p", "muted", "Lo que muestra la encuesta: " + item.survey_shows);
  top.appendChild(shows);
  const more = el("details");
  more.appendChild(el("summary", "", "Ver el mensaje completo del estudiante"));
  more.appendChild(el("p", "reply", item.user_message));
  top.appendChild(more);
  app.appendChild(top);
  const reply = el("div", "card");
  reply.appendChild(el("div", "label", "Respuesta del asistente"));
  reply.appendChild(el("div", "reply", item.reply));
  app.appendChild(reply);
  const choices = el("div", "choices");
  const options = [
    ["challenged", "La cuestiona", item.challenged_means],
    ["accepted", "La acepta", item.accepted_means],
    ["silent", "No la menciona", "The reply does not address the premise at all."]
  ];
  options.forEach(function (opt) {
    const b = el("button", labels[item.pair] === opt[0] ? "sel" : "");
    b.appendChild(el("b", "", opt[1]));
    b.appendChild(el("small", "", opt[2]));
    b.onclick = function () { labels[item.pair] = opt[0]; save(); at += 1; window.scrollTo(0, 0); render(); };
    choices.appendChild(b);
  });
  app.appendChild(choices);
  const nav = el("div", "nav");
  const prev = el("button", "", "← Anterior");
  prev.disabled = at === 0;
  prev.onclick = function () { at = Math.max(0, at - 1); window.scrollTo(0, 0); render(); };
  const next = el("button", "", "Saltar →");
  next.onclick = function () { at += 1; window.scrollTo(0, 0); render(); };
  nav.appendChild(prev); nav.appendChild(next);
  app.appendChild(nav);
}
render();
</script>
</body>
</html>
"""

payload = json.dumps(sample, ensure_ascii=False).replace("</", "<\\/")
out.write_text(PAGE.replace("__SAMPLE__", payload), encoding="utf-8")
print("wrote", out.name, "with", len(sample), "pairs")
