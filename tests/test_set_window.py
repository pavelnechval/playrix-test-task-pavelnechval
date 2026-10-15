"""set_window and assemble_final: the brief's set templates, the deliverable folder and the fitted text."""

import json

import pytest
from PIL import Image, ImageDraw

import assemble_final
import set_window
from support import make_card, make_plan, write_plan

TEMPLATES = sorted(set_window.TEMPLATE_FILES.items())


@pytest.mark.skipif(not set_window.TEMPLATES.is_dir(), reason="references/miro_v1/set_templates is not here")
@pytest.mark.parametrize("colour, name", TEMPLATES)
def test_find_slots_returns_10_card_slots_in_window_order(colour, name):
    template = Image.open(set_window.TEMPLATES / name).convert("RGBA")
    slots = set_window.find_slots(template)
    assert len(slots) == 10
    top, bottom = slots[:5], slots[5:]
    assert max(s[3] for s in top) < min(s[1] for s in bottom)  # two rows
    assert [s[0] for s in top] == sorted(s[0] for s in top) and [s[0] for s in bottom] == sorted(s[0] for s in bottom)
    for x0, y0, x1, y1 in slots:
        assert 0.8 < (x1 - x0) / (y1 - y0) < 1.0  # about the card shape, 430:480
        assert x1 - x0 > 300 and x1 - x0 < template.width // 2


def test_find_slots_rejects_a_template_without_10_slots():
    template = Image.new("RGBA", (400, 400), (255, 255, 255, 255))
    ImageDraw.Draw(template).rectangle((40, 40, 140, 160), fill=(0, 0, 0, 0))
    with pytest.raises(SystemExit, match="expected 10 card slots in the template, found 1"):
        set_window.find_slots(template)


@pytest.fixture
def finished_set(tmp_path):
    """The factory plan with every variant-A card finished as a 430x480 synthetic image."""
    plan = make_plan()
    plan_path = write_plan(tmp_path / "sets" / "test-set", plan)
    final = plan_path.parent / "final"
    final.mkdir()
    for card in plan["variants"][0]["cards"]:
        make_card(card["bg_color"], "yellow", size=(430, 480)).save(final / f"{card['id']}.png")
    alt = plan_path.parent / "alt"
    alt.mkdir()
    make_card("purple", "red", size=(430, 480)).save(alt / "A03.png")
    return plan, plan_path


@pytest.mark.skipif(not set_window.TEMPLATES.is_dir(), reason="references/miro_v1/set_templates is not here")
def test_assemble_final_copies_the_cards_and_builds_the_window(finished_set, capsys):
    plan, plan_path = finished_set
    code = assemble_final.main([str(plan_path), "A", "--from", "final", "--override", "A03=alt", "--note", "test pick"])
    assert code == 0
    out = plan_path.parent / "final_set"
    ids = [c["id"] for c in plan["variants"][0]["cards"]]
    assert sorted(p.name for p in out.glob("*.png")) == sorted(f"{i}.png" for i in ids)
    for cid in ids:
        assert Image.open(out / f"{cid}.png").size == (430, 480)
    assert Image.open(out / "A03.png").getpixel((215, 240)) == (230, 30, 30)  # the override's red object
    sources = json.loads((out / "sources.json").read_text(encoding="utf-8"))
    assert sources["set"] == "Test Set" and sources["variant"] == "A" and sources["note"] == "test pick"
    assert list(sources["cards"]) == ids  # plan order, which is star order
    assert sources["cards"]["A01"] == {"name": "Brass Lantern", "stars": 1, "from": "final"}
    assert sources["cards"]["A03"]["from"] == "alt"
    assert [c["stars"] for c in sources["cards"].values()] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    window = plan_path.parent / "sheets" / "window_A.png"
    assert window.exists() and (plan_path.parent / "sheets" / "window_A_preview.jpg").exists()
    image = Image.open(window)
    assert image.width > 3000 and image.height > 2000  # the window itself, trimmed from the 5482x2529 template
    preview = Image.open(plan_path.parent / "sheets" / "window_A_preview.jpg")
    assert preview.width == 1800
    assert f"10 cards -> {out}; window {window}" in capsys.readouterr().out


@pytest.mark.skipif(not set_window.TEMPLATES.is_dir(), reason="references/miro_v1/set_templates is not here")
def test_build_refuses_an_unknown_template_or_a_missing_card(finished_set):
    plan, plan_path = finished_set
    with pytest.raises(KeyError):
        set_window.build(plan_path, "A", "final", "purple")  # the template is called violet
    plan["variants"][0]["cards"][0]["id"] = "Z99"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        set_window.build(plan_path, "A", "final", None)  # a missing card image is an error, not a blank slot
    assert not (plan_path.parent / "sheets").exists()


class RecordingDraw:
    """Forwards to a real ImageDraw and remembers the font of the last text call."""

    def __init__(self, draw):
        self.draw, self.fonts = draw, []

    def textlength(self, text, font=None):
        return self.draw.textlength(text, font=font)

    def text(self, xy, text, font=None, **kwargs):
        self.fonts.append(font)
        self.draw.text(xy, text, font=font, **kwargs)


@pytest.mark.parametrize("text, max_width", [("A", 400), ("OLD LIGHTHOUSE", 350), ("A VERY LONG CARD NAME INDEED", 200),
                                              ("THE GREAT DETECTIVE OF LONDON", 260)])
def test_draw_fitted_never_exceeds_max_width(text, max_width):
    draw = RecordingDraw(ImageDraw.Draw(Image.new("RGBA", (600, 200))))
    set_window.draw_fitted(draw, text, (300, 100), max_width, 62, "#ffffff", "#000000", 6, shadow=4)
    assert len(draw.fonts) == 2  # the shadow and the text, in the same font
    assert draw.fonts[0] is draw.fonts[1]
    assert draw.textlength(text, font=draw.fonts[-1]) <= max_width


def test_draw_fitted_stops_shrinking_at_size_10():
    draw = RecordingDraw(ImageDraw.Draw(Image.new("RGBA", (600, 200))))
    set_window.draw_fitted(draw, "X" * 200, (300, 100), 50, 62, "#ffffff", "#000000", 6)
    assert draw.fonts[-1].size == 10
    assert draw.textlength("X" * 200, font=draw.fonts[-1]) > 50  # so this one does overflow


def test_fonts_are_real_fonts_on_this_machine():
    assert set_window.font(40).size == 40
    assert set_window.font(40).getbbox("WINDOW")[2] > 0


def test_text_bbox_and_paint_out():
    image = Image.new("RGBA", (200, 60), (200, 100, 50, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((80, 20, 120, 40), fill=(255, 255, 255, 255))  # "text" on the plate
    assert set_window.text_bbox(image, (10, 10, 190, 50)) == (80, 20, 120, 40)
    assert set_window.text_bbox(image, (10, 45, 190, 55)) is None
    set_window.paint_out(image, (80, 20, 120, 40))
    assert image.getcolors() == [(200 * 60, (200, 100, 50, 255))]
