"""colour_check (pixel colour families), costs (the spend log) and sheets (card shaping and contact sheets)."""

import json

import pytest
from PIL import Image

import colour_check
import costs
import sheets
from support import FAMILY_RGB, make_card, make_plan

CARDS = {c["id"]: c for c in make_plan(("A",))["variants"][0]["cards"]}


# ---------------------------------------------------------------- colour_check

@pytest.mark.parametrize("family", sorted(FAMILY_RGB))
def test_family_of_each_synthetic_backdrop(family):
    image = make_card(family, "yellow" if family != "yellow" else "blue")
    shares = colour_check.measure(image, 1)
    assert next(iter(shares)) == family and shares[family] == 1.0
    assert colour_check.backdrop_family(image) == family


def test_grey_dark_and_pastel_pink():
    assert colour_check._family(120, 120, 120) == "grey/dark"
    assert colour_check._family(40, 10, 10) == "grey/dark"
    assert colour_check._family(255, 200, 200) == "grey/dark"  # too pale to be a colour family at all
    assert colour_check._family(255, 160, 170) == "pink"  # a salmon pink: red's hue with low saturation
    assert colour_check._family(230, 30, 30) == "red"


def test_measure_category_3_looks_at_the_wall_not_the_floor():
    image = make_card("blue", "yellow")
    w, h = image.size
    image.paste(FAMILY_RGB["orange"], (0, h // 2, w, h))  # an orange floor over the lower half
    assert colour_check.backdrop_family(image) == "blue"
    assert next(iter(colour_check.measure(image, 3))) == "blue"
    shares = colour_check.measure(image, 1)  # the plain ring includes the floor
    assert set(shares) == {"blue", "orange"}


def test_check_exact_neighbour_and_far_families():
    assert colour_check.check(make_card("purple"), CARDS["A01"])["level"] == "ok"
    warn = colour_check.check(make_card("pink"), CARDS["A01"])  # pink is purple's neighbour on the wheel
    assert warn["pass"] is True and warn["level"] == "warn" and "planned purple" in warn["why"]
    fail = colour_check.check(make_card("green"), CARDS["A01"])
    assert fail["pass"] is False and fail["level"] == "fail"
    assert fail["why"] == "background is green (100% of the background); the plan asks for purple"
    assert fail["measured"] == {"green": 1.0}


def test_teal_fails_even_next_to_its_neighbours():
    blue = {**CARDS["A01"], "bg_color": "blue"}
    assert colour_check.check(make_card("teal"), blue)["pass"] is False  # blue's neighbour, but teal is banned
    image = make_card("blue")
    w, h = image.size
    image.paste(FAMILY_RGB["teal"], (0, 0, w, round(h * 0.35)))  # a third of the ring is teal
    result = colour_check.check(image, blue)
    assert result["pass"] is False and result["measured"]["teal"] >= colour_check.TEAL_LIMIT


def test_check_returns_none_for_category_4():
    assert colour_check.check(make_card("teal"), CARDS["A08"]) is None


def test_near_on_the_wheel():
    assert colour_check._near("red", "pink") and colour_check._near("pink", "red")  # the wheel wraps
    assert colour_check._near("purple", "pink") and not colour_check._near("purple", "yellow")
    assert not colour_check._near("grey/dark", "red")


def test_colour_check_command(tmp_path, capsys):
    plan = make_plan(("A", "B", "C"))
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    final = tmp_path / "final"
    final.mkdir()
    make_card("purple").save(final / "A01.png")  # planned purple: ok
    make_card("green").save(final / "A02.png")  # planned green: ok
    make_card("red").save(final / "A03.png")  # planned blue: fail
    make_card("pink").save(final / "A04.png")  # planned purple: warn
    assert colour_check.main([str(plan_path)]) == 1
    out = capsys.readouterr().out
    assert "FAIL A03 Paper Map: background is red" in out and "WARN A04 Oak Chest" in out
    assert "Test Set: {'ok': 2, 'warn': 1, 'fail': 1}" in out
    assert colour_check.main([]) == 2


# ---------------------------------------------------------------- costs

def test_image_and_text_cost():
    assert costs.image_cost({}) == costs.GEN_IMAGE_1K
    assert costs.image_cost({"total_input_tokens": 1_000_000}) == pytest.approx(costs.GEN_INPUT_PER_M + costs.GEN_IMAGE_1K)
    assert costs.text_cost({}) == 0
    usage = {"total_input_tokens": 1_000_000, "total_output_tokens": 500_000, "total_thought_tokens": 500_000}
    assert costs.text_cost(usage) == pytest.approx(costs.TEXT_INPUT_PER_M + costs.TEXT_OUTPUT_PER_M)
    assert costs.text_cost({"total_input_tokens": 4058, "total_output_tokens": 276, "total_thought_tokens": 456}) == pytest.approx(0.004225)


def test_log_and_totals(tmp_path):
    assert costs.totals(tmp_path) == {}
    costs.log(None, "generate", "A01", 0.05)  # no folder: nothing is written anywhere
    costs.log(tmp_path, "generate", "A01", 0.0554321)
    costs.log(tmp_path, "qa", "A01", 0.004)
    costs.log(tmp_path, "generate", "A02", 0.0554321)
    costs.log(tmp_path, "outpaint", "A02", 0.0354)
    rows = [json.loads(line) for line in (tmp_path / "costs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["kind"] for r in rows] == ["generate", "qa", "generate", "outpaint"]
    assert rows[0] == {**rows[0], "card": "A01", "usd": 0.05543}
    assert rows[0]["at"].endswith("+00:00")
    assert costs.totals(tmp_path) == {"generate": 0.111, "qa": 0.004, "outpaint": 0.035, "total": 0.15}


def test_totals_skips_blank_lines(tmp_path):
    (tmp_path / "costs.jsonl").write_text('{"kind": "vision", "card": "A01", "usd": 0.001}\n\n   \n', encoding="utf-8")
    assert costs.totals(tmp_path) == {"vision": 0.001, "total": 0.001}


# ---------------------------------------------------------------- sheets

def banded(width, height):
    """Red left third, green middle third, blue right third."""
    image = Image.new("RGB", (width, height), (0, 255, 0))
    image.paste((255, 0, 0), (0, 0, width // 3, height))
    image.paste((0, 0, 255), (width - width // 3, 0, width, height))
    return image


def test_to_card_size_and_centre_crop():
    for size in ((1024, 1024), (1000, 500), (500, 1000), (430, 480)):
        card = sheets.to_card(Image.new("RGB", size), 480)
        assert card.size == (430, 480)
    assert sheets.to_card(Image.new("RGB", (1024, 1024)), 240).size == (215, 240)
    wide = sheets.to_card(banded(3000, 500), 480)  # trims the sides: only the middle band survives
    assert wide.getpixel((5, 240)) == (0, 255, 0) and wide.getpixel((424, 240)) == (0, 255, 0)
    tall = sheets.to_card(banded(430, 2000), 480)  # trims top and bottom: all three bands survive
    assert tall.getpixel((5, 240)) == (255, 0, 0) and tall.getpixel((424, 240)) == (0, 0, 255)


def test_extend_to_card_keeps_the_sides_and_stretches_the_background():
    card = sheets.extend_to_card(banded(900, 900), 480)
    assert card.size == (430, 480)
    assert card.getpixel((2, 240)) == (255, 0, 0) and card.getpixel((427, 240)) == (0, 0, 255)  # full width kept
    assert card.getpixel((215, 2)) == (0, 255, 0) and card.getpixel((215, 477)) == (0, 255, 0)  # the rows stretch outward
    solid = sheets.extend_to_card(Image.new("RGB", (800, 800), (40, 90, 200)), 480)
    assert solid.getcolors() == [(430 * 480, (40, 90, 200))]
    assert sheets.extend_to_card(Image.new("RGB", (430, 480)), 480).size == (430, 480)  # nothing to extend


def test_build_sheet_layout_and_captions(tmp_path):
    a, b = tmp_path / "a.png", tmp_path / "b.png"
    make_card("purple").save(a)
    make_card("green").save(b)
    out = tmp_path / "sheets" / "s.png"
    sheets.build_sheet([("row 1", [("A01 Brass Lantern C1 *", a), ("A02 Tin Kettle C2 *", b)]), ("row 2", [("x", a)])],
                       out, 150, "A title that is far too long for such a small sheet, " * 3)
    sheet = Image.open(out)
    cell_w = round(150 * sheets.CARD_ASPECT)
    assert sheet.size == (16 * 2 + 170 + 2 * (cell_w + 12), 16 * 2 + (22 + 20) + 2 * (150 + 22 + 10 + 12))
    assert sheet.getpixel((16 + 170 + 3, 16 + 42 + 3)) == FAMILY_RGB["purple"]  # the first card's backdrop
    assert sheet.getpixel((16 + 170 + cell_w // 2, 16 + 42 + 75)) == FAMILY_RGB["yellow"]  # its object, centred
    assert sheet.getpixel((16 + 170 + cell_w + 12 + 3, 16 + 42 + 3)) == FAMILY_RGB["green"]
    assert sheet.getpixel((sheet.width - 5, sheet.height - 5)) == (255, 255, 255)


def test_caption_font_is_a_real_font():
    font = sheets.caption_font(14)
    assert font.getbbox("Fête")[2] > 0
