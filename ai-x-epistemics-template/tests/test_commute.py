"""Tests for the commute count. The rows here are synthetic; no survey answer is copied."""

import json
from pathlib import Path

import pytest

from epistemics.studies import commute as c

ROOT = Path(__file__).resolve().parents[1]

COLONIAS = """colonia,cp,zona,certeza,alternativa
Ciudad Caucel,97314,Z06,alta,
Las Américas,97302,Z07,alta (punto OSM),
El Roble,97255,Z02,revisar,Z06
Los Almendros,97314,Z06,alta,
Los Almendros,97370,Z12,alta,
Centro Demo,97000,Z01,alta,
"""

POSTALS = """cp,zona,fraccion_en_zona,segunda_zona,fraccion_segunda,certeza,n_colonias
97314,Z06,0.95,Z07,0.05,alta,41
97302,Z08,0.50,Z07,0.48,revisar,23
97000,Z01,1.00,,0.00,alta,6
97246,Z02,0.90,Z06,0.10,alta,10
"""


def tables(tmp_path: Path):
    sources = tmp_path / "study" / "sources"
    sources.mkdir(parents=True)
    (sources / "colonias_zona.csv").write_text(COLONIAS, encoding="utf-8")
    (sources / "cp_zona.csv").write_text(POSTALS, encoding="utf-8")
    return c.zone_tables(tmp_path)


def row(colonia="", cp="", muni="Mérida", mode="Auto propio", willing="Sí", term="Cuatrimestre 0", other=""):
    return {
        c.CONSENT: "Sí, acepto",
        c.TERM: term,
        c.MUNI: muni,
        c.OTHER_MUNI: other,
        c.COLONIA: colonia,
        c.CP: cp,
        c.MODE: mode,
        c.LATE: "0",
        c.ARRIVE: "06:50",
        c.WILLING: willing,
        c.ROUTES: "",
        c.BOARD: "",
        c.STAMP: "2026/11/06 9:00:45 AM CST",
    }


def test_normalize_drops_accents_case_and_punctuation():
    assert c.normalize("  Las Américas, II ") == "las americas ii"


def test_consenting_drops_refusals_and_out_of_scope_terms():
    rows = [
        row(),
        {**row(), c.CONSENT: "No acepto"},
        {**row(), c.TERM: "6.º cuatrimestre u otro (la encuesta no es para ti; gracias)"},
    ]
    assert len(c.consenting(rows)) == 1


def test_colonia_with_high_certainty_assigns_its_zone(tmp_path):
    by_name, postals = tables(tmp_path)
    assert c.assign_zone(row("ciudad caucel", "97314"), by_name, postals) == "Z06"


def test_osm_point_certainty_counts_as_high(tmp_path):
    by_name, postals = tables(tmp_path)
    assert c.assign_zone(row("Las Americas", "97302"), by_name, postals) == "Z07"


def test_review_colonia_does_not_assign_a_zone(tmp_path):
    by_name, postals = tables(tmp_path)
    assert c.assign_zone(row("El Roble"), by_name, postals) == "unassigned"


def test_colonia_and_sure_postal_in_different_zones_is_a_conflict(tmp_path):
    by_name, postals = tables(tmp_path)
    assert c.assign_zone(row("Ciudad Caucel", "97000"), by_name, postals) == "conflict"


def test_colonia_in_two_zones_is_ambiguous(tmp_path):
    by_name, postals = tables(tmp_path)
    assert c.assign_zone(row("Los Almendros"), by_name, postals) == "ambiguous"


def test_postal_fallback_needs_high_certainty_and_095(tmp_path):
    by_name, postals = tables(tmp_path)
    assert c.assign_zone(row("sin catálogo", "97314"), by_name, postals) == "Z06"
    assert c.assign_zone(row("sin catálogo", "97246"), by_name, postals) == "unassigned"
    assert c.assign_zone(row("sin catálogo", "97302"), by_name, postals) == "unassigned"


def test_municipality_fallback(tmp_path):
    by_name, postals = tables(tmp_path)
    assert c.assign_zone(row(muni="Umán"), by_name, postals) == "Z11"
    assert c.assign_zone(row(muni="Kanasín"), by_name, postals) == "Z12"
    assert c.assign_zone(row(muni="Otro municipio"), by_name, postals) == "Z99"


def test_wilson_interval_matches_a_known_value():
    assert c.wilson(160, 260) == (0.55, 0.67)
    with pytest.raises(ValueError):
        c.wilson(0, 0)


def test_metrics_report_all_three_answers_and_zone_bounds():
    rows = [
        row(mode="Auto propio", willing="Sí"),
        row(mode="Camión o combi (en cualquier tramo del viaje)", willing="Sí"),
        row(mode="Me llevan en auto (familiar, amigo o aventón)", willing="Tal vez", term="3.er cuatrimestre"),
        row(mode="Motocicleta", willing="No", term="3.º cuatrimestre", muni="Otro municipio", other="Caucel"),
    ]
    zones = ["Z06", "Z02", "unassigned", "Z99"]
    metrics = c.metrics_for(rows, zones)
    assert metrics["n_willing_yes"] == 2
    assert metrics["n_willing_maybe"] == 1
    assert metrics["n_willing_no"] == 1
    assert metrics["n_willing_driver"] == 1
    assert metrics["n_willing_not_own_car"] == 1
    assert metrics["n_willing_bus"] == 1
    assert metrics["n_term_0"] == 2
    assert metrics["n_term_3"] == 2
    assert metrics["n_placed"] == 2
    assert metrics["n_no_zone"] == 2
    assert metrics["share_outside_z06"] == 0.25
    assert metrics["share_outside_z06_upper"] == 0.75
    assert metrics["n_not_z06_mention_caucel"] == 1


def test_saved_result_matches_a_fresh_count():
    source = ROOT / c.SOURCE
    saved = ROOT / "results" / "commute.json"
    if not source.is_file() or not saved.is_file():
        pytest.skip("the survey file or the saved result is not in this checkout")
    payload = c.evaluate(ROOT)
    stored = json.loads(saved.read_text(encoding="utf-8"))
    assert payload["n"] == stored["n"]
    assert payload["metrics"] == stored["metrics"]
    assert payload["demo"] is False
