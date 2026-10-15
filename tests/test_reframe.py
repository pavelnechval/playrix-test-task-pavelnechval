"""reframe.py: the card window geometry, background stretching, the seam check and the command run offline."""

import hashlib
import json
import random

import pytest
from PIL import Image

import cardgen
import gemini_image
import reframe
from sheets import CARD_ASPECT, to_card
from support import OBJECT_BOX, card_png, make_card, make_plan, png_bytes, write_plan

SIZE = (1024, 1024)
W, H = SIZE


def box_px(box, size=SIZE):
    y0, x0, y1, x1 = box
    w, h = size
    return x0 / 1000 * w, y0 / 1000 * h, x1 / 1000 * w, y1 / 1000 * h


def extent_of(box, win, size=SIZE):
    bx0, by0, bx1, by1 = box_px(box, size)
    left, top, cw, ch = win
    return max((bx1 - bx0) / cw, (by1 - by0) / ch)


def room_above(box, win, size=SIZE):
    _, by0, _, _ = box_px(box, size)
    return (by0 - win[1]) / win[3]


FITTING_BOXES = [  # boxes whose window stays inside a square picture: the geometry is unconstrained by the edges
    OBJECT_BOX, [350, 200, 650, 800], [200, 350, 800, 650], [250, 250, 600, 600], [400, 400, 650, 650], [250, 200, 650, 800],
]


@pytest.mark.parametrize("category", [1, 2, 3, 4])
@pytest.mark.parametrize("box", FITTING_BOXES)
def test_window_aspect_is_the_card_aspect(box, category):
    left, top, cw, ch = reframe.window(SIZE, box, category, False)
    assert cw / ch == pytest.approx(CARD_ASPECT, abs=1e-9)
    assert cw / ch == pytest.approx(430 / 480, abs=1e-9)


@pytest.mark.parametrize("category, target", sorted(reframe.TARGET.items()))
def test_square_object_lands_at_the_target_extent(category, target):
    win = reframe.window(SIZE, OBJECT_BOX, category, False)
    assert reframe.overrun(SIZE, win) == [0, 0, 0, 0]
    assert extent_of(OBJECT_BOX, win) == pytest.approx(target, abs=1e-6)


@pytest.mark.parametrize("category", [1, 2, 3, 4])
@pytest.mark.parametrize("box", FITTING_BOXES)
def test_margins_and_room_above_follow_the_reference_norms(box, category):
    win = reframe.window(SIZE, box, category, False)
    assert reframe.overrun(SIZE, win) == [0, 0, 0, 0]
    bx0, by0, bx1, by1 = box_px(box)
    left, top, cw, ch = win
    assert (bx0 - left) / cw >= reframe.MARGIN - 1e-9
    assert (left + cw - bx1) / cw >= reframe.MARGIN - 1e-9
    assert (top + ch - by1) / ch >= reframe.MARGIN - 1e-9
    assert reframe.ROOM_ABOVE - 1e-9 <= room_above(box, win) <= reframe.ROOM_ABOVE_MAX + 1e-9
    assert extent_of(box, win) <= reframe.TARGET[category] + 1e-9
    assert extent_of(box, win) >= 1 - reframe.ROOM_ABOVE - reframe.MARGIN - 1e-9  # a tall object fills what the room above allows


def test_wide_object_is_centred_horizontally():
    box = [400, 100, 600, 900]
    left, top, cw, ch = reframe.window(SIZE, box, 1, False)
    bx0, by0, bx1, by1 = box_px(box)
    assert left + cw / 2 == pytest.approx((bx0 + bx1) / 2, abs=1e-6)


LOW_WIDE = [850, 100, 950, 900]  # a flat object drawn low: the window must run past the bottom of the picture


@pytest.mark.parametrize("category, share", [(1, reframe.MAX_PAD_BELOW), (2, reframe.MAX_PAD_BELOW), (3, reframe.MAX_PAD_BELOW),
                                             (4, reframe.MAX_PAD)])
def test_window_may_run_past_the_bottom_by_25_percent_on_plain_backdrops_and_12_on_scenes(category, share):
    pads = reframe.overrun(SIZE, reframe.window(SIZE, LOW_WIDE, category, False))
    assert pads[3] == round(share * H)
    assert pads[0] <= round(reframe.MAX_PAD * W) and pads[2] <= round(reframe.MAX_PAD * W) and pads[1] <= round(reframe.MAX_PAD * H)


def test_stretching_keeps_12_percent_everywhere_and_none_on_a_touched_side():
    pads = reframe.overrun(SIZE, reframe.window(SIZE, LOW_WIDE, 1, True))
    assert pads[3] == round(reframe.MAX_PAD * H)
    touching = [850, 100, 995, 900]  # within TOUCH of the bottom edge
    pads = reframe.overrun(SIZE, reframe.window(SIZE, touching, 1, True))
    assert pads[3] == 0
    assert reframe.overrun(SIZE, reframe.window(SIZE, touching, 1, False))[3] == round(reframe.MAX_PAD_BELOW * H)


def test_overrun_is_never_negative_and_the_window_never_leaves_the_padded_picture():
    rng = random.Random(7)
    for _ in range(300):
        y0, x0 = rng.randint(0, 900), rng.randint(0, 900)
        box = [y0, x0, rng.randint(y0 + 20, 1000), rng.randint(x0 + 20, 1000)]
        category = rng.choice([1, 2, 3, 4])
        stretch = rng.choice([True, False])
        size = rng.choice([SIZE, (1024, 768), (768, 1024)])
        win = reframe.window(size, box, category, stretch)
        pads = reframe.overrun(size, win)
        assert all(isinstance(p, int) and p >= 0 for p in pads), (box, category, stretch, pads)
        w, h = size
        below = reframe.MAX_PAD_BELOW if category in (1, 2, 3) and not stretch else reframe.MAX_PAD
        assert pads[0] <= round(reframe.MAX_PAD * w) + 1 and pads[2] <= round(reframe.MAX_PAD * w) + 1
        assert pads[1] <= round(reframe.MAX_PAD * h) + 1 and pads[3] <= round(below * h) + 1
        assert win[2] > 0 and win[3] > 0


def test_overrun_values():
    assert reframe.overrun((100, 100), (-5.4, 0, 80, 120.4)) == [5, 0, 0, 20]
    assert reframe.overrun((100, 100), (10, 10, 50, 50)) == [0, 0, 0, 0]


# ---------------------------------------------------------------- stretching, seam check

def test_stretch_pad_sizes_and_content():
    image = make_card("purple", "yellow", size=(100, 80))
    out = reframe.stretch_pad(image, 5, 7, 11, 13)
    assert out.size == (116, 100)
    assert out.getpixel((5 + 50, 7 + 40)) == image.getpixel((50, 40))  # the picture sits at (left, top)
    assert reframe.stretch_pad(image, 0, 0, 0, 0).size == image.size
    solid = Image.new("RGB", (60, 40), (40, 90, 200))
    padded = reframe.stretch_pad(solid, 30, 20, 30, 20)
    assert padded.size == (120, 80)
    assert padded.getcolors() == [(120 * 80, (40, 90, 200))]  # a plain backdrop stretches to the same colour


def test_ring_diff_of_a_picture_with_itself_is_zero():
    image = make_card("blue", "orange")
    assert reframe.ring_diff(image, image) == 0.0
    assert reframe.ring_diff(image, image.copy()) == 0.0


def shifted(image, dx, dy):
    out = Image.new("RGB", image.size, image.getpixel((0, 0)))
    out.paste(image, (dx, dy))
    return out


def textured_card():
    """Something like a card: a gradient backdrop with rings and an object, so a shift changes the ring."""
    image = make_card("purple", "yellow", size=(1024, 1024))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    for r in range(80, 720, 60):
        draw.ellipse((512 - r, 512 - r, 512 + r, 512 + r), outline=(190, 120, 240), width=8)
    for y in range(0, 1024, 32):
        draw.line((0, y, 1024, y), fill=(120, 40, 200), width=3)
    return image


REAL_CARDS = sorted((reframe.HERE.parent / "sets").glob("*/final/*.png"))


@pytest.mark.skipif(not REAL_CARDS, reason="no finished card in sets/ to measure")
@pytest.mark.xfail(reason="On a real card a copy shifted by 4 px scores about 2 (SEAM_MAX is 5.0; W022 saw 4.0 before colour "
                          "matching), so a 4 px misalignment passes the seam check today. Pavel to decide whether it should be rejected.",
                   strict=False)
def test_seam_check_rejects_a_4px_shift(record_property):
    image = Image.open(REAL_CARDS[0]).convert("RGB")
    score = reframe.ring_diff(image, shifted(image, 4, 4))
    record_property("ring_diff_4px", round(score, 2))
    record_property("card", REAL_CARDS[0].as_posix())
    assert score > reframe.SEAM_MAX, f"a 4 px shift of {REAL_CARDS[0].name} scores {score:.2f} against SEAM_MAX {reframe.SEAM_MAX}"


def test_seam_check_rejects_a_large_shift():
    image = textured_card()
    small, large = reframe.ring_diff(image, shifted(image, 4, 4)), reframe.ring_diff(image, shifted(image, 48, 48))
    assert 0 < small < large
    assert large > reframe.SEAM_MAX


def test_compose_matches_colours_and_blends_the_original_back():
    image = make_card("purple", "yellow", size=(400, 400))
    S = round(400 * (1 + 2 * reframe.MAX_PAD))
    ml = (S - 400) // 2
    model = reframe.stretch_pad(image, ml, ml, S - 400 - ml, S - 400 - ml)  # the perfect outpaint: the same picture
    darker = Image.eval(model, lambda v: max(0, v - 20))  # the model shifted the palette, as in W022
    out, info = reframe.compose(image, darker)
    assert out.size == (S, S)
    assert info["offset"] == [ml, ml] and info["margin"] == reframe.MAX_PAD
    assert info["colour_shift"] == [20, 20, 20]
    assert info["ok"] is True and info["seam"] < 1
    assert out.getpixel((ml + 200, ml + 200)) == image.getpixel((200, 200))  # the original pixels are kept


# ---------------------------------------------------------------- the command, offline

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Folder:
    """A one-variant set with A01 generated and chosen, as cardgen leaves it."""

    def __init__(self, tmp_path, box=OBJECT_BOX, backdrop="purple"):
        self.plan = make_plan(("A",))
        self.plan_path = write_plan(tmp_path / "sets" / "test-set", self.plan)
        self.folder = self.plan_path.parent
        card_dir = self.folder / "cards" / "A01"
        card_dir.mkdir(parents=True)
        self.image = make_card(backdrop, "yellow", box)
        self.src = card_dir / "try1.png"
        self.src.write_bytes(png_bytes(self.image))
        (card_dir / "try1.request.json").write_text(json.dumps({"card": {"id": "A01"}, "sent_at": "2026-10-15T00:00:00+00:00"}), encoding="utf-8")
        (card_dir / "try1.response.json").write_text(json.dumps({"est_cost_usd": 0.05, "elapsed_s": 9}), encoding="utf-8")
        (card_dir / "chosen.json").write_text(json.dumps({"file": "try1.png", "status": "passed"}), encoding="utf-8")
        self.final = self.folder / "final" / "A01.png"
        self.final.parent.mkdir()
        to_card(self.image, 480).save(self.final)
        self.before = sha(self.final)

    def cache_box(self, box):
        stamp = {"file": str(self.src), "mtime": int(self.src.stat().st_mtime), "box": list(box)}
        (self.folder / "boxes_raw.json").write_text(json.dumps({"A01": stamp}), encoding="utf-8")

    def log(self):
        return json.loads((self.folder / "reframe_log.json").read_text(encoding="utf-8"))

    def main(self, *args):
        return reframe.main([str(self.plan_path), "--route", "gemini", *args])


@pytest.fixture
def no_vision(monkeypatch):
    """raw_box must not be called: it is a paid vision call."""
    def refuse(path, log_dir=None, card=""):
        raise AssertionError("raw_box was called")
    monkeypatch.setattr(reframe, "raw_box", refuse)


def test_fill_stretch_makes_no_api_call(tmp_path, fake_gemini, monkeypatch, capsys):
    f = Folder(tmp_path, box=LOW_WIDE)
    calls = []
    monkeypatch.setattr(reframe, "raw_box", lambda path, log_dir=None, card="": calls.append(str(path)) or list(LOW_WIDE))
    assert f.main("--fill", "stretch") == 0
    assert calls == [str(f.src)]
    assert fake_gemini.calls == []  # no outpainting: the stretched edge fills the window
    entry = f.log()["A01"]
    assert entry["fill"] == "stretch" and entry["pad"][3] == round(reframe.MAX_PAD * H) and entry["pad"][:3] == [0, 0, 0]
    assert sha(f.final) != f.before
    assert Image.open(f.final).size == (430, 480)
    assert (f.folder / "final_prev" / "A01.png").exists() and sha(f.folder / "final_prev" / "A01.png") == f.before
    cache = json.loads((f.folder / "boxes_raw.json").read_text(encoding="utf-8"))
    assert cache["A01"]["box"] == LOW_WIDE and cache["A01"]["file"] == str(f.src)
    assert "A01 Brass Lantern: zoom" in capsys.readouterr().out
    assert (f.folder / "sheets" / "variant_A.png").exists() and (f.folder / "summary.md").exists()


def test_a_fresh_box_cache_means_no_vision_call(tmp_path, fake_gemini, no_vision):
    f = Folder(tmp_path)
    f.cache_box(OBJECT_BOX)
    assert f.main() == 0
    assert fake_gemini.calls == []
    assert f.log()["A01"]["fill"] == "none" and f.log()["A01"]["extent"] == pytest.approx(0.82, abs=0.001)
    assert f.log()["A01"]["room_above"] == pytest.approx(0.14, abs=0.001)


def test_override_box_needs_no_api_call(tmp_path, fake_gemini, no_vision, capsys):
    f = Folder(tmp_path)
    assert f.main("--override", "A01", "--box", "300,300,700,700", "--why", "the subject is the whole lantern") == 0
    assert fake_gemini.calls == []
    framing = json.loads((f.folder / "framing.json").read_text(encoding="utf-8"))
    assert framing["gemini/A01"] == {"mtime": int(f.src.stat().st_mtime), "image": "try1.png",
                                     "why": "the subject is the whole lantern", "box": [300, 300, 700, 700]}
    assert not (f.folder / "boxes_raw.json").exists()  # the vision cache keeps vision boxes only
    assert f.log()["A01"]["override"] == "the subject is the whole lantern"
    assert f.log()["A01"]["fill"] == "none"
    assert "override for gemini/A01 written" in capsys.readouterr().out
    assert sha(f.final) != f.before


def test_override_needs_a_reason_and_a_box_or_fill(tmp_path, fake_gemini, no_vision):
    f = Folder(tmp_path)
    with pytest.raises(SystemExit, match="needs --why"):
        f.main("--override", "A01", "--box", "300,300,700,700")
    with pytest.raises(SystemExit, match="needs --box and/or --fill"):
        f.main("--override", "A01", "--why", "x")
    with pytest.raises(SystemExit, match="y0,x0,y1,x1"):
        f.main("--override", "A01", "--box", "1,2,3", "--why", "x")
    with pytest.raises(SystemExit, match="No generated images found"):
        f.main("--override", "A02", "--box", "300,300,700,700", "--why", "x")
    assert not (f.folder / "framing.json").exists()


def test_stale_override_is_ignored(tmp_path, fake_gemini, monkeypatch, capsys):
    f = Folder(tmp_path)
    (f.folder / "framing.json").write_text(json.dumps({"gemini/A01": {"mtime": 1, "image": "try0.png", "why": "old",
                                                                        "box": [0, 0, 1000, 1000]}}), encoding="utf-8")
    monkeypatch.setattr(reframe, "raw_box", lambda path, log_dir=None, card="": list(OBJECT_BOX))
    assert f.main() == 0
    assert "A01: the framing override is for an earlier image; ignored" in capsys.readouterr().out
    assert "override" not in f.log()["A01"] and f.log()["A01"]["extent"] == pytest.approx(0.82, abs=0.001)


def test_clear_override(tmp_path, fake_gemini, no_vision, capsys):
    f = Folder(tmp_path)
    f.cache_box(OBJECT_BOX)
    path = f.folder / "framing.json"
    path.write_text(json.dumps({"gemini/A01": {"mtime": int(f.src.stat().st_mtime), "image": "try1.png", "why": "x",
                                               "fill": "stretch"}, "gemini/A02": {"why": "keep"}}), encoding="utf-8")
    assert f.main("--clear-override", "A01") == 0
    assert json.loads(path.read_text(encoding="utf-8")) == {"gemini/A02": {"why": "keep"}}
    assert "override for gemini/A01 removed" in capsys.readouterr().out
    assert "override" not in f.log()["A01"]


def test_failed_box_call_leaves_the_final_unchanged(tmp_path, fake_gemini, monkeypatch, capsys):
    f = Folder(tmp_path)
    def fail(path, log_dir=None, card=""):
        raise gemini_image.GeminiError("HTTP 503 for POST interactions: overloaded", 503)
    monkeypatch.setattr(reframe, "raw_box", fail)
    assert f.main() == 0
    out = capsys.readouterr().out
    assert "A01: box failed (HTTP 503" in out and "no box for A01: left as they were" in out
    assert sha(f.final) == f.before
    assert f.log() == {}
    assert not (f.folder / "final_prev").exists()
    assert json.loads((f.folder / "boxes_raw.json").read_text(encoding="utf-8")) == {}


def test_empty_balance_during_the_box_call_exits_2(tmp_path, fake_gemini, monkeypatch, capsys):
    f = Folder(tmp_path)
    def fail(path, log_dir=None, card=""):
        raise gemini_image.BillingError(gemini_image.BILLING_HELP, 402)
    monkeypatch.setattr(reframe, "raw_box", fail)
    assert f.main() == 2
    assert gemini_image.BILLING_HELP in capsys.readouterr().out
    assert sha(f.final) == f.before and f.log() == {}


def test_empty_balance_during_outpainting_leaves_the_card_as_it_was(tmp_path, fake_gemini, monkeypatch, capsys):
    f = Folder(tmp_path, box=LOW_WIDE)
    f.cache_box(LOW_WIDE)
    fake_gemini.images.append(gemini_image.BillingError(gemini_image.BILLING_HELP, 402))
    assert f.main() == 2
    out = capsys.readouterr().out
    assert "no background extension for A01: left as they were" in out
    assert sha(f.final) == f.before and "A01" not in f.log()


def test_outpaint_failure_falls_back_to_stretching(tmp_path, fake_gemini, monkeypatch, capsys):
    f = Folder(tmp_path, box=LOW_WIDE)
    f.cache_box(LOW_WIDE)
    fake_gemini.images.append(gemini_image.GeminiError("HTTP 500", 500))
    assert f.main() == 0
    assert "A01: outpaint failed (HTTP 500); stretching instead" in capsys.readouterr().out
    assert f.log()["A01"]["fill"] == "stretch" and sha(f.final) != f.before


def test_outpainting_uses_the_model_image_when_the_seam_is_clean(tmp_path, fake_gemini, monkeypatch):
    f = Folder(tmp_path, box=LOW_WIDE)
    f.cache_box(LOW_WIDE)
    S = round(W * (1 + 2 * reframe.MAX_PAD_BELOW))
    ml, mt = (S - W) // 2, (S - H) // 2
    fake_gemini.images.append(png_bytes(reframe.stretch_pad(f.image, ml, mt, S - W - ml, S - H - mt)))  # a faithful extension
    assert f.main() == 0
    call = fake_gemini.calls_of("image")[0]
    assert call[1] == cardgen.GEN_MODEL and [p["type"] for p in call[2]] == ["image", "text"]
    assert reframe.OUTPAINT_PROMPT in fake_gemini.text_of(call)
    entry = f.log()["A01"]
    assert entry["fill"] == "outpaint" and entry["seam"] < reframe.SEAM_MAX
    op = json.loads((f.folder / "outpaint.json").read_text(encoding="utf-8"))["A01"]
    assert op["ok"] is True and op["tries"] == 1 and op["margin"] == reframe.MAX_PAD_BELOW and op["cost"] > 0
    assert (f.folder / "outpaint" / "A01.try1.model.png").exists() and (f.folder / "outpaint" / "A01.png").exists()
    rows = [json.loads(l) for l in (f.folder / "costs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["kind"] for r in rows] == ["outpaint"]
    fake_gemini.calls.clear()
    assert f.main() == 0  # a re-run reuses the saved extension: no call
    assert fake_gemini.calls == []


def test_a_moved_outpaint_is_retried_once_then_stretched(tmp_path, fake_gemini, capsys):
    f = Folder(tmp_path, box=LOW_WIDE)
    f.cache_box(LOW_WIDE)
    moved = Image.new("RGB", (1024, 1024), (10, 10, 10))  # nothing like the picture
    fake_gemini.images.extend([png_bytes(moved), png_bytes(moved)])
    assert f.main() == 0
    assert len(fake_gemini.calls_of("image")) == 2
    assert f.log()["A01"]["fill"] == "stretch"
    op = json.loads((f.folder / "outpaint.json").read_text(encoding="utf-8"))["A01"]
    assert op["ok"] is False and op["tries"] == 2 and op["models"] == ["A01.try1.model.png", "A01.try2.model.png"]


def test_mistyped_route_and_missing_images(tmp_path, fake_gemini, no_vision):
    f = Folder(tmp_path)
    with pytest.raises(SystemExit, match="No route folder"):
        f.main("--route", "gpt_v9")
    with pytest.raises(SystemExit, match="--fill is outpaint or stretch"):
        f.main("--fill", "A01.try2.model.png")
    (f.folder / "cards" / "A01" / "chosen.json").unlink()
    (f.folder / "cards" / "A01" / "try1.response.json").unlink()
    f.final.unlink()
    with pytest.raises(SystemExit, match="No generated images found"):
        f.main()


def test_raw_box_parses_and_clamps_the_answer(tmp_path, fake_gemini):
    path = tmp_path / "card.png"
    path.write_bytes(card_png("purple"))
    fake_gemini.texts.append('The box: {"box_2d": [-20, 300, 1200, 700], "category": 1}')
    assert reframe.raw_box(path, tmp_path, "A01") == [0, 300, 1000, 700]
    rows = [json.loads(l) for l in (tmp_path / "costs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(r["kind"], r["card"]) for r in rows] == [("vision", "A01")]
    call = fake_gemini.calls_of("text")[0]
    assert [p["type"] for p in call[2]] == ["text", "image"]
