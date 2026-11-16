"""Counts from the UPY morning-commute survey joined to macrozones. Not a fixture."""

from __future__ import annotations

import csv
import math
import unicodedata
from datetime import datetime
from pathlib import Path

from epistemics.run import build_result, find_root, ratio, write_result

STUDY = "commute"
SOURCE = Path("study") / "sources" / "encuesta_traslado_upy.csv"
ZONES = Path("study") / "sources" / "macrozonas.csv"
COLONIAS = Path("study") / "sources" / "colonias_zona.csv"
POSTALS = Path("study") / "sources" / "cp_zona.csv"
PROMPT = """Consenting sample: the acceptance column equals Sí, acepto, and the cuatrimestre cell does not contain "no es para ti".
share_willing_yes counts a meeting-point answer of Sí. share_willing_maybe counts Tal vez and share_willing_no counts No.
willing_yes_ci95_low and willing_yes_ci95_high are the Wilson 95% interval for share_willing_yes.
n_term_0 counts Cuatrimestre 0 and n_term_3 counts a cuatrimestre cell that starts with 3.
share_own_car counts mode Auto propio.
share_bus counts a mode that starts with Camión.
share_late_any_day counts a last-week answer that parses as an integer of at least 1.
share_usual_after_0700 counts a usual arrival that parses as HH:MM and is strictly later than 07:00.
n_willing_driver counts Auto propio and Sí.
n_willing_not_own_car counts a mode other than Auto propio and Sí. n_willing_bus counts a mode that starts with Camión and Sí. n_willing_passenger counts a mode that starts with Me llevan en auto and Sí.
Zone join, first rule that fires: a normalized colonia that matches one zona among rows whose certeza starts with alta, which includes alta (punto OSM); if that postal code also has certeza alta, fraccion_en_zona >= 0.95, and a different zona, the row is a conflict and gets no zone. Else a postal code with certeza alta and fraccion_en_zona >= 0.95. Else municipio Umán is Z11, Kanasín is Z12, and Otro municipio is Z99. Anything else is unassigned. A revisar colonia does not assign a zone.
share_outside_z06 counts assigned zones Z01-Z05 and Z07-Z12 over the consenting sample. Z06 is the Caucel exterior zone. Z99 is not counted as outside. No kilometers are imputed. The PDF times are not copied onto respondents.
n_no_zone counts every row without a zone Z01-Z12: Z99, unassigned, conflict, and ambiguous. share_outside_z06 is a lower bound because those rows stay in the denominator. share_outside_z06_upper counts every row that is not placed in Z06 over the consenting sample.
n_not_z06_mention_caucel counts rows not placed in Z06 whose colonia or named municipality contains caucel, or whose postal code is 97314.
n_willing_driver_z06 counts Auto propio, Sí, and zone Z06. n_willing_not_own_z06 counts Sí, a mode other than Auto propio, and zone Z06.
n_board_prepa_10 counts a boarding answer that contains Preparatoria Número 10. n_board_humanitas counts Universidad Humanitas. The same two with the _z06 suffix also require zone Z06.
n_name_americas counts a normalized colonia that contains america. n_name_americas_yes also requires Sí. Empty seats are not a column. Do not multiply drivers by an assumed seat count inside the metrics.
Rates use epistemics.run.ratio, rounded to two decimals.
"""

CONSENT = "¿Aceptas contestar la encuesta en estas condiciones?"
TERM = "¿En qué cuatrimestre estás?"
MUNI = "¿En qué municipio está el lugar de donde sales hacia el campus la mayoría de los días?"
OTHER_MUNI = "¿Cuál es ese municipio?"
COLONIA = "Colonia o fraccionamiento de donde sales"
CP = "Código postal de esa colonia (opcional)"
MODE = "¿Cómo llegas normalmente al campus?"
LATE = "La semana pasada, ¿cuántos días llegaste al campus después de las 7:00?"
ARRIVE = "¿A qué hora llegas normalmente al campus?"
WILLING = "Si hubiera un punto de encuentro cerca de donde sales para compartir el traslado con otros estudiantes de la UPY, ¿lo usarías?"
ROUTES = "¿Qué rutas de camión o combi usas normalmente?"
BOARD = "¿Dónde subes normalmente a la R-92 o a la R-805?"
STAMP = "Timestamp"
SEVEN = 7 * 60
PLACED = tuple(f"Z{i:02d}" for i in range(1, 13))


def parse_clock(value: str) -> int | None:
    text = value.strip()
    if not text or ":" not in text:
        return None
    hour, minute = text.split(":", 1)
    return int(hour) * 60 + int(minute)


def parse_stamp(value: str) -> datetime | None:
    try:
        return datetime.strptime(value.strip(), "%Y/%m/%d %I:%M:%S %p CST")
    except ValueError:
        return None


def normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.strip().casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    chars = [ch if ch.isalnum() else " " for ch in text]
    return " ".join("".join(chars).split())


def wilson(hits: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion, rounded like epistemics.run.ratio."""
    if total == 0:
        raise ValueError("cannot rate an empty set")
    share = hits / total
    denominator = 1 + z * z / total
    center = (share + z * z / (2 * total)) / denominator
    half = z * math.sqrt(share * (1 - share) / total + z * z / (4 * total * total)) / denominator
    return round(center - half, 2), round(center + half, 2)


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def consenting(rows: list[dict]) -> list[dict]:
    kept: list[dict] = []
    for row in rows:
        if row[CONSENT].strip() != "Sí, acepto":
            continue
        if "no es para ti" in row[TERM]:
            continue
        kept.append(row)
    return kept


def zone_tables(root: Path) -> tuple[dict[str, set[str]], dict[str, dict]]:
    by_name: dict[str, set[str]] = {}
    for row in load_rows(root / COLONIAS):
        if not row["certeza"].strip().startswith("alta"):
            continue
        by_name.setdefault(normalize(row["colonia"]), set()).add(row["zona"].strip())
    postals = {row["cp"].strip(): row for row in load_rows(root / POSTALS)}
    return by_name, postals


def assign_zone(row: dict, by_name: dict[str, set[str]], postals: dict[str, dict]) -> str:
    alta = by_name.get(normalize(row[COLONIA]), set())
    postal = postals.get(row[CP].strip())
    postal_sure = (
        postal is not None
        and postal["certeza"].strip() == "alta"
        and float(postal["fraccion_en_zona"]) >= 0.95
    )
    if len(alta) == 1:
        zone = next(iter(alta))
        if postal_sure and postal["zona"].strip() != zone:
            return "conflict"
        return zone
    if len(alta) > 1:
        return "ambiguous"
    if postal_sure:
        return postal["zona"].strip()
    muni = row[MUNI].strip()
    if muni == "Umán":
        return "Z11"
    if muni == "Kanasín":
        return "Z12"
    if muni == "Otro municipio":
        return "Z99"
    return "unassigned"


def metrics_for(rows: list[dict], zones: list[str]) -> dict:
    n = len(rows)
    willing_yes = [row for row in rows if row[WILLING].strip() == "Sí"]
    willing_maybe = [row for row in rows if row[WILLING].strip() == "Tal vez"]
    willing_no = [row for row in rows if row[WILLING].strip() == "No"]
    ci_low, ci_high = wilson(len(willing_yes), n)
    own_car = [row for row in rows if row[MODE].strip() == "Auto propio"]
    bus = [row for row in rows if row[MODE].strip().startswith("Camión")]
    late_any = []
    for row in rows:
        text = row[LATE].strip()
        if text.isdigit() and int(text) >= 1:
            late_any.append(row)
    usual_after = []
    for row in rows:
        clock = parse_clock(row[ARRIVE])
        if clock is not None and clock > SEVEN:
            usual_after.append(row)
    willing_driver = [row for row in own_car if row[WILLING].strip() == "Sí"]
    willing_not_own = [row for row in willing_yes if row[MODE].strip() != "Auto propio"]
    stamps = [stamp for row in rows if (stamp := parse_stamp(row[STAMP])) is not None]
    placed = [zone for zone in zones if zone in PLACED]
    mention_caucel = sum(
        zones[index] != "Z06"
        and (
            "caucel" in normalize(row[COLONIA])
            or "caucel" in normalize(row.get(OTHER_MUNI, ""))
            or row[CP].strip() == "97314"
        )
        for index, row in enumerate(rows)
    )
    outside = [zone for zone in placed if zone != "Z06"]
    metrics = {
        "share_willing_yes": ratio(len(willing_yes), n),
        "willing_yes_ci95_low": ci_low,
        "willing_yes_ci95_high": ci_high,
        "share_willing_maybe": ratio(len(willing_maybe), n),
        "share_willing_no": ratio(len(willing_no), n),
        "share_own_car": ratio(len(own_car), n),
        "share_bus": ratio(len(bus), n),
        "share_late_any_day": ratio(len(late_any), n),
        "share_usual_after_0700": ratio(len(usual_after), n),
        "n_willing_yes": len(willing_yes),
        "n_willing_maybe": len(willing_maybe),
        "n_willing_no": len(willing_no),
        "n_term_0": sum(row[TERM].strip() == "Cuatrimestre 0" for row in rows),
        "n_term_3": sum(row[TERM].strip().startswith("3") for row in rows),
        "n_own_car": len(own_car),
        "n_bus": len(bus),
        "n_late_any_day": len(late_any),
        "n_usual_after_0700": len(usual_after),
        "n_willing_driver": len(willing_driver),
        "n_willing_not_own_car": len(willing_not_own),
        "n_willing_bus": sum(row[MODE].strip().startswith("Camión") for row in willing_yes),
        "n_willing_passenger": sum(row[MODE].strip().startswith("Me llevan en auto") for row in willing_yes),
        "n_mention_r92": sum("R-92" in row[ROUTES] for row in rows),
        "n_mention_r805": sum("R-805" in row[ROUTES] for row in rows),
        "n_board_calle_67": sum("Calle 67 x 62" in row[BOARD] for row in rows),
        "n_board_lejos": sum(row[BOARD].strip().startswith("Otro paradero, lejos") for row in rows),
        "first_response": min(stamps).strftime("%Y-%m-%dT%H:%M") if stamps else "",
        "last_response": max(stamps).strftime("%Y-%m-%dT%H:%M") if stamps else "",
        "n_z06": sum(zone == "Z06" for zone in zones),
        "n_outside_z06": len(outside),
        "n_placed": len(placed),
        "n_z99": sum(zone == "Z99" for zone in zones),
        "n_unassigned": sum(zone == "unassigned" for zone in zones),
        "n_conflict": sum(zone == "conflict" for zone in zones),
        "n_ambiguous": sum(zone == "ambiguous" for zone in zones),
        "n_no_zone": n - len(placed),
        "n_not_z06_mention_caucel": mention_caucel,
        "share_z06": ratio(sum(zone == "Z06" for zone in zones), n),
        "share_no_zone": ratio(n - len(placed), n),
        "share_outside_z06": ratio(len(outside), n),
        "share_outside_z06_upper": ratio(n - sum(zone == "Z06" for zone in zones), n),
        "share_outside_among_placed": ratio(len(outside), len(placed)),
        "n_willing_driver_z06": sum(
            zones[index] == "Z06" and row[MODE].strip() == "Auto propio" and row[WILLING].strip() == "Sí"
            for index, row in enumerate(rows)
        ),
        "n_willing_not_own_z06": sum(
            zones[index] == "Z06" and row[MODE].strip() != "Auto propio" and row[WILLING].strip() == "Sí"
            for index, row in enumerate(rows)
        ),
        "n_board_prepa_10": sum("Preparatoria Número 10" in row[BOARD] for row in rows),
        "n_board_humanitas": sum("Universidad Humanitas" in row[BOARD] for row in rows),
        "n_board_prepa_10_z06": sum(
            zones[index] == "Z06" and "Preparatoria Número 10" in row[BOARD]
            for index, row in enumerate(rows)
        ),
        "n_board_humanitas_z06": sum(
            zones[index] == "Z06" and "Universidad Humanitas" in row[BOARD]
            for index, row in enumerate(rows)
        ),
        "n_name_americas": sum("america" in normalize(row[COLONIA]) for row in rows),
        "n_name_americas_yes": sum(
            "america" in normalize(row[COLONIA]) and row[WILLING].strip() == "Sí" for row in rows
        ),
    }
    for code in PLACED:
        metrics[f"n_{code.lower()}"] = sum(zone == code for zone in zones)
    return metrics


def evaluate(root: Path | None = None) -> dict:
    root = root or find_root()
    path = root / SOURCE
    if not path.is_file():
        raise FileNotFoundError(
            f"{SOURCE.as_posix()} is not in this repository: the raw survey is private and stays with the team. "
            "results/commute.json holds the saved count."
        )
    rows = consenting(load_rows(path))
    if not rows:
        raise ValueError("consenting sample is empty")
    by_name, postals = zone_tables(root)
    known = {item["codigo"].strip() for item in load_rows(root / ZONES)}
    zones = [assign_zone(row, by_name, postals) for row in rows]
    unknown = {zone for zone in zones if zone.startswith("Z") and zone not in known}
    if unknown:
        raise ValueError(f"unknown zone codes: {sorted(unknown)}")
    metrics = metrics_for(rows, zones)
    return build_result(
        study=STUDY,
        provider="survey",
        model="commute-counter",
        prompt_template=PROMPT,
        n=len(rows),
        items=[
            {
                "id": "consenting-sample",
                "prompt_id": "encuesta-traslado-upy",
                "raw_output": str(len(rows)),
                "grade": {"n": len(rows)},
            }
        ],
        metrics=metrics,
        baseline={"name": "mayoria", "threshold": 0.5},
        demo=False,
        preexisting=False,
    )


def run(root: Path | None = None) -> dict:
    root = root or find_root()
    payload = evaluate(root)
    write_result(root, payload)
    return payload
