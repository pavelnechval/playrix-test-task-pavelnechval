"""rating_report: the statistics helpers and the two regexes that read the external model's table."""

import pytest

import rating_report


def test_ranks_with_ties():
    assert rating_report.ranks([10, 20, 20, 30]) == [1.0, 2.5, 2.5, 4.0]
    assert rating_report.ranks([3, 1, 2]) == [3.0, 1.0, 2.0]
    assert rating_report.ranks([5, 5, 5]) == [2.0, 2.0, 2.0]
    assert rating_report.ranks([]) == []


def test_kappa():
    assert rating_report.kappa([True, True, False, False], [True, True, False, False]) == 1.0
    assert rating_report.kappa([True, True, False, False], [False, False, True, True]) == -1.0
    assert rating_report.kappa([True, True, True, True], [True, True, True, True]) == 1.0  # no chance disagreement
    assert rating_report.kappa([True, False, True, False], [True, False, False, True]) == pytest.approx(0.0)


def test_pct():
    assert rating_report.pct(3, 4) == "3/4 (75%)"
    assert rating_report.pct(0, 0) == "-"


@pytest.mark.parametrize("line, match", [
    ("| LC-A01 | 4 | no | fine, warm |", ("LC-A01", "4", "no", "fine, warm")),
    ("|PP-C10|2|YES|too busy|", ("PP-C10", "2", "YES", "too busy")),
    ("| LC-A01 | 4 | maybe | x |", None),
    ("| A01 | 4 | no | x |", None),  # no set prefix
    ("| LC-A01 | 44 | no | x |", None),  # one digit only
])
def test_row_regex(line, match):
    m = rating_report.ROW.match(line)
    assert (m.groups() if m else None) == match


@pytest.mark.parametrize("line, pick", [
    ("**Love in the City - Variant B:** the warmest set", ("Love in the City", "B")),
    ("**Once Upon a Garden — Variant A** reads best", ("Once Upon a Garden", "A")),
    ("**The Lost Island – Variant C:**", ("The Lost Island", "C")),
    ("Love in the City - Variant B", None),  # not bold
])
def test_pick_regex(line, pick):
    m = rating_report.PICK.search(line)
    assert ((m[1].strip(), m[2]) if m else None) == pick


def test_read_external(tmp_path):
    path = tmp_path / "external.md"
    path.write_text("# Ratings\n| code | score | notice | commentary |\n|---|---|---|---|\n"
                    "| LC-A01 | 4 | no | fine |\n| LC-A02 | 2 | Yes | the mug is odd |\n\n"
                    "**Love in the City - Variant B:** best overall\n", encoding="utf-8")
    scores, picks = rating_report.read_external(path)
    assert scores == {"LC-A01": {"score": 4, "notice": "no", "comment": "fine"},
                      "LC-A02": {"score": 2, "notice": "yes", "comment": "the mug is odd"}}
    assert picks == {"Love in the City": "B"}


def test_table_shape():
    assert rating_report.table(["a", "b"], [[1, 2]]) == ["| a | b |", "|---|---|", "| 1 | 2 |", ""]
