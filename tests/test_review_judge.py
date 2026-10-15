"""cardgen.review and judge: how a judge answer becomes a verdict (regression for W025: no verdict is never a pass)."""

import json

import pytest

import cardgen
import costs
import gemini_image
from support import OBJECT_BOX, TEXT_USAGE, card_png, make_plan, qa_answer

CARD = make_plan(("A",))["variants"][0]["cards"][0]  # A01: category 1, purple backdrop
SCENE = make_plan(("A",))["variants"][0]["cards"][7]  # A08: category 4, no pixel colour check
PURPLE = card_png("purple")


@pytest.mark.parametrize("passed", [True, False])
def test_review_honours_boolean_pass(fake_gemini, prompts, refs, passed):
    template, qa_template = prompts
    fake_gemini.texts.append(qa_answer(passed, fix="" if passed else "make the handle thicker"))
    verdict = cardgen.review(CARD, PURPLE, "image/png", template, qa_template, refs)
    assert verdict["pass"] is passed
    assert "qa_error" not in verdict
    assert verdict["fix"] == ("" if passed else "make the handle thicker")
    assert verdict["usage"] == TEXT_USAGE
    assert verdict["est_cost_usd"] == costs.text_cost(TEXT_USAGE)
    assert verdict["elapsed_s"] == 0.1
    call = fake_gemini.calls_of("text")[0]
    assert call[1] == cardgen.QA_MODEL
    kinds = [p["type"] for p in call[2]]
    assert kinds == ["text", "image", "image", "image"]  # the prompt, the candidate, two references of its category
    prompt = fake_gemini.text_of(call)
    assert CARD["name"] in prompt and CARD["subject"] in prompt and CARD["background"] in prompt


def test_review_reads_the_json_object_inside_prose(fake_gemini, prompts, refs):
    template, qa_template = prompts
    fake_gemini.texts.append('Here is my review:\n```json\n{"pass": false, "fix": "make it rounder"}\n```\nDone.')
    verdict = cardgen.review(CARD, PURPLE, "image/png", template, qa_template, refs)
    assert verdict["pass"] is False
    assert verdict["fix"] == "make it rounder"


@pytest.mark.parametrize("answer, unparseable", [
    ("Looks fine to me, the lantern is lovely.", True),
    ("", True),
    ("[1, 2, 3]", True),
    ('{"pass": "yes", "fix": ""}', False),
    ('{"pass": 1}', False),
    ('{"checks": {}, "fix": ""}', False),
    ('{"pass": null}', False),
])
def test_review_without_a_verdict_gives_pass_none(fake_gemini, prompts, refs, answer, unparseable):
    """W025: an unreadable answer or one without a true/false `pass` used to count as a pass."""
    template, qa_template = prompts
    fake_gemini.texts.append(answer)
    verdict = cardgen.review(CARD, PURPLE, "image/png", template, qa_template, refs)
    assert verdict["pass"] is None
    assert "no true/false verdict" in verdict["qa_error"]  # the generic reason replaces "unparseable QA answer"
    assert ("raw" in verdict) is unparseable  # the unreadable answer itself is kept for the log
    assert cardgen.qa_pass(verdict) is None
    assert cardgen.attempt_status({"qa_pass": cardgen.qa_pass(verdict)}) == "unchecked"


def test_review_keeps_the_raw_answer_when_unparseable(fake_gemini, prompts, refs):
    template, qa_template = prompts
    fake_gemini.texts.append("x" * 3000)
    verdict = cardgen.review(CARD, PURPLE, "image/png", template, qa_template, refs)
    assert verdict["raw"] == "x" * 2000


def test_judge_asks_once_more_then_leaves_the_card_unchecked(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.extend(["no json here", "still no json"])
    verdict = cardgen.judge(CARD, PURPLE, "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is None
    assert len(fake_gemini.calls_of("text")) == 2
    assert verdict["checks"]["bg_colour"]["pass"] is True  # the pixel check still ran, but it cannot turn None into a pass
    rows = [json.loads(line) for line in (tmp_path / "costs.jsonl").read_text().splitlines()]
    assert [r["kind"] for r in rows] == ["qa", "qa"]
    assert all(r["card"] == "A01" for r in rows)


def test_judge_second_ask_can_recover(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.extend(["no json here", qa_answer(True)])
    verdict = cardgen.judge(CARD, PURPLE, "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is True
    assert len(fake_gemini.calls_of("text")) == 2


def test_judge_does_not_ask_again_after_a_clear_verdict(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.append(qa_answer(False, fix="bigger"))
    verdict = cardgen.judge(CARD, PURPLE, "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is False
    assert len(fake_gemini.calls_of("text")) == 1


def test_judge_api_error_is_unchecked_not_retried(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.append(gemini_image.GeminiError("HTTP 503 for POST interactions: overloaded", 503))
    verdict = cardgen.judge(CARD, PURPLE, "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is None
    assert "503" in verdict["qa_error"]
    assert len(fake_gemini.calls_of("text")) == 1
    assert not cardgen.STOP.is_set()
    assert not (tmp_path / "costs.jsonl").exists()  # a failed call costs nothing and is not logged


def test_judge_billing_error_sets_stop(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.append(gemini_image.BillingError(gemini_image.BILLING_HELP, 402))
    verdict = cardgen.judge(CARD, PURPLE, "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is None
    assert cardgen.STOP.is_set()
    assert len(fake_gemini.calls_of("text")) == 1


def test_judge_pixel_colour_check_overrules_the_judge(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.append(qa_answer(True))
    verdict = cardgen.judge(CARD, card_png("teal"), "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is False
    assert verdict["checks"]["bg_colour"]["pass"] is False
    assert verdict["checks"]["bg_colour"]["level"] == "fail"
    assert verdict["fix"].startswith("Make the background purple: ")
    assert cardgen.qa_pass(verdict) is False


def test_judge_keeps_the_judge_fix_after_the_colour_fix(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.append(qa_answer(False, fix="thicker handle"))
    verdict = cardgen.judge(CARD, card_png("red"), "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is False
    assert verdict["fix"].startswith("Make the background purple")
    assert verdict["fix"].endswith("thicker handle")


def test_judge_neighbour_colour_is_a_warning_not_a_fail(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.append(qa_answer(True))
    verdict = cardgen.judge(CARD, card_png("pink"), "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is True
    assert verdict["checks"]["bg_colour"] == {**verdict["checks"]["bg_colour"], "pass": True, "level": "warn"}


def test_judge_skips_the_colour_check_for_category_4(fake_gemini, prompts, refs, tmp_path):
    template, qa_template = prompts
    fake_gemini.texts.append(qa_answer(True))
    verdict = cardgen.judge(SCENE, card_png("teal"), "image/png", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is True
    assert "bg_colour" not in verdict["checks"]


def test_judge_accepts_jpeg_candidates(fake_gemini, prompts, refs, tmp_path):
    from support import make_card, png_bytes
    template, qa_template = prompts
    fake_gemini.texts.append(qa_answer(True))
    jpeg = png_bytes(make_card("purple"), "JPEG")
    verdict = cardgen.judge(CARD, jpeg, "image/jpeg", tmp_path, template, qa_template, refs)
    assert verdict["pass"] is True
    assert fake_gemini.calls_of("text")[0][2][1]["mime_type"] == "image/jpeg"


@pytest.mark.parametrize("verdict, expected", [
    ({"pass": True}, True), ({"pass": False}, False), ({"pass": None}, None), ({}, None), ({"pass": 1}, True),
])
def test_qa_pass_mapping(verdict, expected):
    assert cardgen.qa_pass(verdict) is expected


@pytest.mark.parametrize("attempt, use_qa, expected", [
    ({"qa_pass": True}, True, "passed"),
    ({"qa_pass": False}, True, "accepted_with_issues"),
    ({"qa_pass": None}, True, "unchecked"),
    ({}, True, "unchecked"),
    ({"qa_pass": False}, False, "unchecked"),
    ({"qa_pass": True}, False, "passed"),
])
def test_attempt_status_mapping(attempt, use_qa, expected):
    assert cardgen.attempt_status(attempt, use_qa) == expected


def test_record_verdict_writes_the_file_and_the_attempt_fields(tmp_path):
    verdict = json.loads(qa_answer(False, fix="smaller", failing=("framing", "detail")))
    verdict["checks"]["bg_colour"] = {"pass": True, "level": "ok"}
    verdict["est_cost_usd"] = 0.004
    attempt = {"try": 1, "file": "try1.png"}
    cardgen.record_verdict(attempt, verdict, tmp_path / "try1")
    assert json.loads((tmp_path / "try1.qa.json").read_text(encoding="utf-8")) == verdict
    assert attempt == {"try": 1, "file": "try1.png", "qa_pass": False, "qa_cost": 0.004, "failed": ["framing", "detail"],
                       "fix": "smaller", "checks_passed": 6}


def test_passed_checks_ignores_non_dict_entries():
    assert cardgen.passed_checks({"checks": {"a": {"pass": True}, "b": {"pass": False}, "c": "yes", "d": {"pass": True}}}) == 2
    assert cardgen.passed_checks({}) == 0


def test_object_box_constant_matches_the_synthetic_card():
    assert OBJECT_BOX == [300, 300, 700, 700]
