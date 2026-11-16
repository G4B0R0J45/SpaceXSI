"""Builds the submission docx from the sprint template already used, with the body taken from report/blocks.json.

Usage: python build_docx2.py <repo root> <unpacked template dir> <out.docx>
"""

import copy
import json
import os
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

root_dir, unpacked, out_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
XML_NS = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("w", W_NS)
ET.register_namespace("w14", W14_NS)
W = "{" + W_NS + "}"
FONT = "Old Standard TT"

doc_spec = json.loads((root_dir / "report" / "blocks.json").read_text(encoding="utf-8"))
messages = json.loads((root_dir / "study" / "premises" / "messages.json").read_text(encoding="utf-8"))
data_block = (root_dir / "study" / "premises" / "data_block.md").read_text(encoding="utf-8").replace("\r\n", "\n")
results = json.loads((root_dir / "results" / "premises.json").read_text(encoding="utf-8"))

tree = ET.parse(unpacked / "word" / "document.xml")
doc = tree.getroot()
body = doc.find(W + "body")


def text_of(element) -> str:
    return "".join(t.text or "" for t in element.iter(W + "t"))


def find(prefix: str):
    hits = [p for p in doc.iter(W + "p") if text_of(p).startswith(prefix)]
    assert hits, prefix
    return hits[0]


def style_of(p) -> str:
    ppr = p.find(W + "pPr")
    style = ppr.find(W + "pStyle") if ppr is not None else None
    return style.get(W + "val") if style is not None else ""


def scrub(element):
    for node in element.iter():
        for attr in list(node.attrib):
            if attr.startswith("{" + W14_NS + "}"):
                del node.attrib[attr]
    return element


def set_text(p, text: str, bold: bool | None = None, size: int | None = None) -> None:
    runs = p.findall(W + "r")
    keep = runs[0]
    for extra in runs[1:]:
        p.remove(extra)
    rpr = keep.find(W + "rPr")
    if rpr is None:
        rpr = ET.Element(W + "rPr")
        keep.insert(0, rpr)
    if rpr.find(W + "rFonts") is None:
        fonts = ET.Element(W + "rFonts")
        for attr in ("ascii", "cs", "eastAsia", "hAnsi"):
            fonts.set(W + attr, FONT)
        rpr.insert(0, fonts)
    if bold is not None:
        for tag in ("b", "bCs"):
            for node in rpr.findall(W + tag):
                rpr.remove(node)
        if bold:
            ET.SubElement(rpr, W + "b")
    if size is not None:
        for tag in ("sz", "szCs"):
            for node in rpr.findall(W + tag):
                rpr.remove(node)
            ET.SubElement(rpr, W + tag).set(W + "val", str(size))
    for child in list(keep):
        if child.tag != W + "rPr":
            keep.remove(child)
    node = ET.SubElement(keep, W + "t")
    node.text = text
    node.set("{" + XML_NS + "}space", "preserve")


# ------------------------------------------------------------------ prototypes from the template
children = list(body)
table_index = next(i for i, el in enumerate(children) if el.tag == W + "tbl")
PROTO_H2 = copy.deepcopy(next(p for p in body.findall(W + "p") if style_of(p) == "Heading2"))
PROTO_H3 = copy.deepcopy(next(p for p in body.findall(W + "p") if style_of(p) == "Heading3"))
PROTO_P = copy.deepcopy(find("Students at the Universidad"))
PROTO_UL = copy.deepcopy(find("Code repository"))
PROTO_OL = copy.deepcopy(find("A consenting-sample count"))
PROTO_REF = copy.deepcopy(find("Apart Research. 2026."))
PROTO_EMPTY = copy.deepcopy(next(el for el in children[table_index + 1 :] if el.tag == W + "p" and not text_of(el).strip()))

# ------------------------------------------------------------------ title and abstract
title = next(p for p in doc.iter(W + "p") if style_of(p) == "Title")
first_run = next(r for r in title.findall(W + "r") if text_of(r).strip())
first_run.find(W + "t").text = doc_spec["title"]
abstract_p = find("This open-track study asks")
set_text(abstract_p, doc_spec["abstract"])

# ------------------------------------------------------------------ clear the old body
section = body.find(W + "sectPr")
for el in children[table_index + 2 :]:
    if el is not section:
        body.remove(el)


def add(el):
    body.insert(list(body).index(section), scrub(el))


def p_from(proto, text, **kw):
    el = copy.deepcopy(proto)
    set_text(el, text, **kw)
    return el


def spacer():
    add(copy.deepcopy(PROTO_EMPTY))


def h2(text, first=False):
    if not first:
        spacer()
    add(p_from(PROTO_H2, text))


def h3(text):
    add(p_from(PROTO_H3, text))


def para(text, **kw):
    add(p_from(PROTO_P, text, **kw))


def ul(items):
    for item in items:
        add(p_from(PROTO_UL, item, bold=False))


def ol(items, proto=PROTO_OL):
    for item in items:
        add(p_from(proto, item))


def table(header, rows):
    widths = [4200] + [2400] * (len(header) - 1)
    tbl = ET.Element(W + "tbl")
    tpr = ET.SubElement(tbl, W + "tblPr")
    ET.SubElement(tpr, W + "tblW", {W + "w": str(sum(widths)), W + "type": "dxa"})
    ET.SubElement(tpr, W + "jc", {W + "val": "center"})
    borders = ET.SubElement(tpr, W + "tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        ET.SubElement(borders, W + side, {W + "val": "single", W + "sz": "4", W + "space": "0", W + "color": "999999"})
    ET.SubElement(tpr, W + "tblLayout", {W + "type": "fixed"})
    grid = ET.SubElement(tbl, W + "tblGrid")
    for width in widths:
        ET.SubElement(grid, W + "gridCol", {W + "w": str(width)})
    for row_index, row in enumerate([header] + rows):
        tr = ET.SubElement(tbl, W + "tr")
        for width, value in zip(widths, row):
            tc = ET.SubElement(tr, W + "tc")
            tcpr = ET.SubElement(tc, W + "tcPr")
            ET.SubElement(tcpr, W + "tcW", {W + "w": str(width), W + "type": "dxa"})
            if row_index == 0:
                ET.SubElement(tcpr, W + "shd", {W + "val": "clear", W + "color": "auto", W + "fill": "EDEDED"})
            cell_p = p_from(PROTO_P, value, bold=row_index == 0, size=20)
            ppr = cell_p.find(W + "pPr")
            if ppr is None:
                ppr = ET.Element(W + "pPr")
                cell_p.insert(0, ppr)
            for old in ppr.findall(W + "spacing"):
                ppr.remove(old)
            spacing = ET.Element(W + "spacing", {W + "before": "40", W + "after": "40"})
            ppr.insert(0, spacing)
            tc.append(scrub(cell_p))
    add(tbl)
    spacer()


# ------------------------------------------------------------------ body from blocks
first = True
for block in doc_spec["blocks"]:
    kind = block["kind"]
    if kind == "h2":
        h2(block["docx"], first)
        first = False
    elif kind == "h3":
        h3(block["docx"])
    elif kind == "p":
        para(block["text"])
    elif kind == "ul":
        if block.get("docx_skip"):
            continue
        if block.get("keep"):
            ul(block["items"])
        else:
            para(" ".join(block["items"]))
    elif kind == "ol":
        ol(block["items"])
    elif kind == "table":
        table(block["header"], block["rows"])

# ------------------------------------------------------------------ back matter
h2("Code and Data")
para("The repository is public. The raw survey is not: it records neighborhood, postal code and an optional sex field, and the team keeps it. The saved count is results/commute.json, and the report lists no person.")
ul(
    [
        "Code repository: https://github.com/G4B0R0J45/SpaceXSI (folder ai-x-epistemics-template).",
        "Study inputs: study/premises/ holds the two messages, the survey summary sent to the models, the premise rubric, the configuration, and the file hashes taken at each step.",
        "Results: results/premises.json holds every reply, label, quote and metric; results/commute.json holds the survey count. report/claims.json points each result sentence at one of them, and python -m epistemics check verifies the match.",
        "Rerun: put free Groq and Gemini API keys in .env and run python -m epistemics run premises. Calls are cached, so a rerun with the same settings repeats the same replies.",
    ]
)
h2("Author Contributions (optional)")
para("Gabriel Rojas designed the survey with the team, wrote the two messages that form the stimulus, chose the premises, labeled the blind sample, and is responsible for the report.")
h2("References")
para("The works named in Related Work are cited as the sprint's reading list presents them. The team did not read them in full during the sprint.")
ol(
    [
        "Apart Research. 2026. AI x Epistemics Research Sprint, Resources tab. https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15",
        "Fanous et al. 2025. SycEval. AIES 2025. Listed on the sprint Resources tab.",
        "Cheng et al. 2025. ELEPHANT. Listed on the sprint Resources tab.",
        "Ren et al. 2025. The MASK Benchmark. CAIS. Listed on the sprint Resources tab.",
        "Kran et al. 2025. DarkBench. ICLR 2025. Listed on the sprint Resources tab.",
        "Cheng et al. 2025. Sycophantic AI Decreases Prosocial Intentions and Promotes Dependence. Science. Listed on the sprint Resources tab.",
        "OpenAI. 2025. Sycophancy in GPT-4o. Listed on the sprint Resources tab.",
        "Cotton-Barratt, Vaintrob, Sourbut and Hadshar. 2026. Design Sketches: Angels-on-the-Shoulder. Forethought. Listed on the sprint Resources tab.",
        "Cotton-Barratt and Finnveden. 2026. AI for AI for Epistemics. Forethought. Listed on the sprint Resources tab.",
        "AI Safety México. 2026. ai-x-epistemics-template. https://github.com/aisafetymexico/ai-x-epistemics-template",
        "Proyecto Integrador I, Equipo 5. 2026. Macrozonas de origen y tiempos a la UPY. Map dated 6 October 2026. Saved in the repository as evidence/macrozonas-upy.md.",
    ],
    proto=PROTO_REF,
)
h2("Appendix (optional)")
h3("A. The two user messages, as sent")
para("First message:", bold=True)
para(messages["turn1"])
para("Bridge line added by the experiment:", bold=True)
para(messages["bridge"])
para("Second message:", bold=True)
para(messages["turn2"])
h3("B. Survey summary sent to the models")
for line in [line for line in data_block.split("\n") if line.strip()]:
    para(line, size=18)
h3("C. Settings")
settings = results["settings"]
para(
    f"Subjects: {', '.join(s['provider'] + ' ' + s['model'] for s in results['subjects'])}. "
    f"Judges: {', '.join(j['provider'] + ' ' + j['model'] for j in results['judges'])}. "
    f"Conversations per model and condition: {settings['k']}. Direct questions per model: {settings['direct_k']}. "
    f"Temperature {settings['temperature']} for subjects and 0 for judges. Bootstrap resamples: {settings['bootstrap_reps']}, seed {settings['seed']}."
)
h2("LLM Usage Statement")
para(
    "A coding assistant (Cursor) helped write the survey count and the first version of this report. A second coding "
    "assistant (Claude Code) reviewed that version, wrote the premise study's code and tests with the author, ran it, and "
    "drafted this text from the saved result files. The four subject models and the judges are part of the method, "
    "described above. Every number in the report is read from a result file by script, and a checker compares each result "
    "sentence with its file. The author is responsible for every claim."
)

# ------------------------------------------------------------------ write and zip
tree.write(unpacked / "word" / "document.xml", xml_declaration=True, encoding="UTF-8")
if out_path.exists():
    out_path.unlink()
with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as archive:
    names = []
    for folder, _, files in os.walk(unpacked):
        for name in files:
            names.append((Path(folder) / name).relative_to(unpacked).as_posix())
    names.sort(key=lambda name: (name != "[Content_Types].xml", name))
    for name in names:
        archive.write(unpacked / name, name)
print("wrote", out_path.name)
