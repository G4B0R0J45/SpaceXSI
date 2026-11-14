from pathlib import Path

from epistemics.studies.crux_mapper import build_map, load_people, render_html

ROOT = Path(__file__).resolve().parents[1]


def test_crux_classification():
    person_a, person_b = load_people(ROOT)
    mapped = build_map(person_a, person_b)
    assert [row["claim"] for row in mapped["shared"]] == ["The offer includes four office days"]
    assert [row["claim"] for row in mapped["cruxes"]] == ["The team is growing"]
    assert mapped["cruxes"][0]["gap"] == 0.4
    assert mapped["inconsistencies"]["person_a"][0]["probabilities"] == [0.8, 0.4]
    assert mapped["inconsistencies"]["person_b"] == []
    assert mapped["only_b"][0]["claim"] == "Remote work stays available"


def test_html_embeds_the_map():
    person_a, person_b = load_people(ROOT)
    page = render_html(build_map(person_a, person_b))
    assert "The team is growing" in page
    assert 'id="disagreement-map"' in page
    assert "Template example" in page
