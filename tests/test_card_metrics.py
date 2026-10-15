"""card_metrics: reference norms, flags, correction notes and the measuring batch."""

import json
import statistics

import pytest

import card_metrics
import gemini_image
from support import OBJECT_BOX, make_card, make_plan, write_plan


def ref_row(category, extent=0.85, margin=0.06, margin_top=0.14, detail_lost=9.0, highlight=0.02):
    return {"category_seen": category, "category_confidence": "high", "height": extent, "width": extent * 0.9,
            "margin": margin, "margin_top": margin_top, "detail_lost": detail_lost, "highlight": highlight}


def synthetic_refs():
    refs = {}
    for cat in (1, 2, 3, 4):
        for i, extent in enumerate((0.76, 0.80, 0.85, 0.90, 0.94)):
            refs[f"c{cat}_{i}"] = ref_row(cat, extent=extent, margin=0.04 + i * 0.01, margin_top=0.12 + i * 0.01, detail_lost=7 + i * 1.5)
    refs["gold"] = ref_row(5)  # character cards are not a norm
    refs["few"] = ref_row(1)
    return refs


def test_norms_quartiles_per_category():
    refs = synthetic_refs()
    norms = card_metrics.norms(refs)
    assert set(norms) == {1, 2, 3, 4}
    assert norms[2]["n"] == 5
    extents = [0.76, 0.80, 0.85, 0.90, 0.94]
    q = statistics.quantiles(extents, n=4)
    assert norms[2]["extent"] == {"q1": round(q[0], 3), "median": round(q[1], 3), "q3": round(q[2], 3)}
    assert norms[1]["n"] == 6  # the extra category 1 row counts; the category 5 row never does
    assert set(norms[3]) == {"n", *card_metrics.METRICS}


def test_norms_need_at_least_four_cards():
    refs = {f"r{i}": ref_row(1) for i in range(3)}
    refs.update({f"s{i}": ref_row(2) for i in range(4)})
    assert set(card_metrics.norms(refs)) == {2}


def test_value_extent_is_the_largest_dimension():
    assert card_metrics.value({"height": 0.5, "width": 0.8}, "extent") == 0.8
    assert card_metrics.value({"height": 0.9, "width": 0.3}, "extent") == 0.9
    assert card_metrics.value({"margin": 0.05}, "margin") == 0.05
    assert card_metrics.value({}, "margin") is None


REF = {"extent": {"q1": 0.76, "median": 0.85, "q3": 0.94}, "margin": {"q1": 0.04, "median": 0.06, "q3": 0.08},
       "margin_top": {"q1": 0.12, "median": 0.14, "q3": 0.16}, "detail_lost": {"q1": 7.0, "median": 9.6, "q3": 12.0}}


def row(**values):
    base = {"category_seen": 1, "category_confidence": "high", "height": 0.85, "width": 0.80, "margin": 0.06,
            "margin_top": 0.14, "detail_lost": 9.0, "highlight": 0.1}
    return {**base, **values}


@pytest.mark.parametrize("values, flags", [
    ({}, []),
    ({"height": 0.70, "width": 0.60}, ["small"]),  # below q1 - a quarter of the range (0.715)
    ({"height": 0.72, "width": 0.60}, []),  # inside the widened band
    ({"height": 0.99, "width": 0.60}, ["too big"]),  # above q3 + the pad (0.985)
    ({"margin": 0.02}, ["tight margins"]),
    ({"margin": 0.20}, []),  # a wide margin is never flagged
    ({"margin_top": 0.10}, ["little room above"]),
    ({"margin_top": 0.18}, ["much room above"]),
    ({"detail_lost": 14.0}, ["fine detail lost"]),
    ({"detail_lost": 2.0}, []),  # little detail lost is fine
    ({"category_seen": 2, "category_confidence": "medium"}, ["reads as C2 (medium)"]),
    ({"category_seen": 4, "height": 0.99, "margin": 0.0}, ["reads as C4 (high)", "too big", "tight margins"]),
])
def test_card_flags_thresholds(values, flags):
    assert card_metrics.card_flags(row(**values), 1, REF) == flags


def test_card_flags_skip_metrics_without_a_norm():
    assert card_metrics.card_flags(row(height=0.99), 1, {}) == []
    assert card_metrics.card_flags(row(height=0.99, margin=0.0), 1, {"margin": REF["margin"]}) == ["tight margins"]


def test_pixel_metrics_keys_and_tiny_box():
    card = make_card("purple", "yellow", size=(430, 480))
    metrics = card_metrics.pixel_metrics(card, OBJECT_BOX)
    assert set(metrics) == {"detail_lost", "edge_full", "highlight", "saturation"}
    assert metrics["highlight"] == 0 and 0 < metrics["saturation"] <= 1
    assert card_metrics.pixel_metrics(card, [500, 500, 502, 502]) == {}


def test_measure_parses_the_vision_answer(tmp_path, fake_gemini):
    path = tmp_path / "A01.png"
    make_card("purple").save(path)
    fake_gemini.texts.append('{"box_2d": [300, 300, 700, 1200], "category": 2, "category_confidence": "high", "small_detail": "low", "why": "test"}')
    row = card_metrics.measure(path, tmp_path, "A01")
    assert row["box"] == [300, 300, 700, 1000] and row["category_seen"] == 2 and row["small_detail"] == "low"
    assert row["height"] == 0.4 and row["width"] == 0.7 and row["margin"] == 0.0
    assert row["margin_top"] == 0.3 and row["margin_bottom"] == 0.3
    assert "detail_lost" in row
    rows = [json.loads(l) for l in (tmp_path / "costs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(r["kind"], r["card"]) for r in rows] == [("vision", "A01")]
    assert fake_gemini.calls_of("text")[0][1] == card_metrics.MODEL


@pytest.fixture
def items(tmp_path):
    path = tmp_path / "final" / "A01.png"
    path.parent.mkdir()
    make_card("purple").save(path)
    cache = tmp_path / "metrics_final.json"
    cache.write_text(json.dumps({"A01": {"_key": "stale", "height": 0.5, "width": 0.5}}), encoding="utf-8")
    return {"A01": path}, cache


def test_measure_all_with_a_failing_api_reports_zero_measured_and_keeps_the_cache(items, monkeypatch, capsys):
    paths, cache = items
    def fail(path, log_dir=None, name=""):
        raise gemini_image.GeminiError("HTTP 503", 503)
    monkeypatch.setattr(card_metrics, "measure", fail)
    assert card_metrics.measure_all(paths, cache, None) is False
    out = capsys.readouterr().out
    assert "A01: failed (HTTP 503)" in out
    assert "0 measured, 0 unchanged, 1 not measured" in out and "not measured: A01" in out
    assert json.loads(cache.read_text(encoding="utf-8")) == {"A01": {"_key": "stale", "height": 0.5, "width": 0.5}}


def test_measure_all_on_an_empty_balance_says_so(items, monkeypatch, capsys):
    paths, cache = items
    def fail(path, log_dir=None, name=""):
        raise gemini_image.BillingError(gemini_image.BILLING_HELP, 402)
    monkeypatch.setattr(card_metrics, "measure", fail)
    assert card_metrics.measure_all(paths, cache, None) is False
    assert gemini_image.BILLING_HELP in capsys.readouterr().out


def test_measure_all_skips_unchanged_images_and_updates_the_rest(items, monkeypatch, capsys):
    paths, cache = items
    st = paths["A01"].stat()
    cache.write_text(json.dumps({"A01": {"_key": f"{st.st_size}:{int(st.st_mtime)}", "height": 0.5}}), encoding="utf-8")
    monkeypatch.setattr(card_metrics, "measure", lambda path, log_dir=None, name="": pytest.fail("measure called"))
    assert card_metrics.measure_all(paths, cache, None) is True
    assert "0 measured, 1 unchanged, 0 not measured" in capsys.readouterr().out
    cache.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(card_metrics, "measure", lambda path, log_dir=None, name="": {"height": 0.8, "width": 0.7})
    assert card_metrics.measure_all(paths, cache, None) is True
    saved = json.loads(cache.read_text(encoding="utf-8"))
    assert saved["A01"]["height"] == 0.8 and saved["A01"]["_key"] == f"{st.st_size}:{int(st.st_mtime)}"
    assert "1 measured, 0 unchanged, 0 not measured" in capsys.readouterr().out


@pytest.fixture
def measured_set(tmp_path, monkeypatch):
    """A plan with measured cards: A01 too big and reading as C2, A02 flagged on framing only, A03 within the norms."""
    plan = make_plan(("A",))
    plan_path = write_plan(tmp_path / "sets" / "test-set", plan)
    final = plan_path.parent / "final"
    final.mkdir()
    for cid in ("A01", "A02", "A03"):
        make_card("purple").save(final / f"{cid}.png")
    ours = {"A01": row(category_seen=2, height=0.99, width=0.6, detail_lost=15.0),
            "A02": row(category_seen=2, margin=0.01, margin_top=0.09),  # planned category 2: no category flag
            "A03": row()}
    (plan_path.parent / "metrics_final.json").write_text(json.dumps(ours), encoding="utf-8")
    monkeypatch.setattr(card_metrics, "REF_OUT", tmp_path / "refs.json")
    card_metrics.REF_OUT.write_text(json.dumps(synthetic_refs()), encoding="utf-8")
    return plan_path


def test_make_fixes_writes_one_note_per_flagged_card(measured_set):
    fixes = card_metrics.make_fixes(measured_set, "final", None)
    assert set(fixes) == {"A01", "A02"}
    assert "It reads as a different card category; make it float in the air" in fixes["A01"]
    assert "The object spans 99% of the card; make it smaller, about 85%" in fixes["A01"]
    assert "Simplify it: fewer, larger shapes" in fixes["A01"]
    assert fixes["A02"].startswith("The object comes within 1% of an edge; keep at least 5% clear")
    assert "Only 9% of the height is clear above the object" in fixes["A02"]


def test_make_fixes_leaves_out_framing_flags_on_framed_cards(measured_set):
    (measured_set.parent / "reframe_log.json").write_text(json.dumps({"A01": {"zoom": 1}, "A02": {"zoom": 1}}), encoding="utf-8")
    fixes = card_metrics.make_fixes(measured_set, "final", None)
    assert set(fixes) == {"A01"}  # A02 had framing flags only: reframe.py sets size and room, a redraw can't
    assert "make it smaller" not in fixes["A01"]
    assert "reads as a different card category" in fixes["A01"] and "Simplify it" in fixes["A01"]


def test_report_lists_norms_flags_and_the_spread(measured_set):
    text = card_metrics.report(measured_set, "final", None)
    assert "| C1 | 6 |" in text and "| C4 | 5 |" in text
    assert "| A01 | Brass Lantern | C1 | C2 | 0.99 |" in text and "reads as C2 (high), too big, fine detail lost |" in text
    assert "| A03 | Paper Map | C1 | C1 | 0.85 |" in text and "| - |" in text
    assert "2 of 3 cards flagged." in text
    assert (measured_set.parent / "metrics_final.md").read_text(encoding="utf-8") == text


def test_fixes_command_writes_the_json(measured_set, capsys):
    assert card_metrics.main(["fixes", str(measured_set)]) == 0
    out = measured_set.parent / "fixes.json"
    assert set(json.loads(out.read_text(encoding="utf-8"))) == {"A01", "A02"}
    assert "2 correction note(s)" in capsys.readouterr().out


def test_plan_items_one_cache_per_folder(measured_set):
    cards, items, cache = card_metrics.plan_items(measured_set, "final", "A")
    assert set(items) == {"A01", "A02", "A03"} and len(cards) == 10
    assert cache == measured_set.parent / "metrics_final.json"
    assert card_metrics.plan_items(measured_set, "gpt_v7/final", None)[2] == measured_set.parent / "gpt_v7" / "metrics_final.json"
