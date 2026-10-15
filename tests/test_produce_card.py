"""cardgen.produce_card and the commands around it, run in a temporary set folder with a fake Gemini.

Covers the happy path, retries with the producer's note, the pixel colour check, both empty-balance paths (W023,
W025), regen with framing, choose, and the summary's single cost line.
"""

import hashlib
import io
import json

import pytest
from PIL import Image, ImageChops

import cardgen
import costs
import gemini_image
import reframe
from sheets import to_card
from support import IMAGE_USAGE, OBJECT_BOX, TEXT_USAGE, card_png, make_card, qa_answer

GEN_COST = costs.image_cost(IMAGE_USAGE)
QA_COST = costs.text_cost(TEXT_USAGE)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same_pixels(a: Image.Image, b: Image.Image) -> bool:
    return a.size == b.size and ImageChops.difference(a.convert("RGB"), b.convert("RGB")).getbbox() is None


def cost_rows(out):
    path = out / "costs.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


class Run:
    """One card of the factory plan in a temporary set folder."""

    def __init__(self, plan_path, plan, prompts, refs, card_id="A01"):
        self.plan_path, self.plan, self.out = plan_path, plan, plan_path.parent
        self.template, self.qa_template = prompts
        self.refs = refs
        self.card = next(c for v in plan["variants"] for c in v["cards"] if c["id"] == card_id)
        self.card_dir = self.out / "cards" / card_id
        self.final = self.out / "final" / f"{card_id}.png"

    def produce(self, retries=2, use_qa=True, first_fix=""):
        return cardgen.produce_card(self.card, self.out, self.template, self.qa_template, self.refs, retries, use_qa, first_fix)

    def request(self, n):
        return json.loads((self.card_dir / f"try{n}.request.json").read_text(encoding="utf-8"))

    def qa(self, n):
        return json.loads((self.card_dir / f"try{n}.qa.json").read_text(encoding="utf-8"))

    def chosen(self):
        return json.loads((self.card_dir / "chosen.json").read_text(encoding="utf-8"))


@pytest.fixture
def run(plan_path, plan, prompts, refs):
    return Run(plan_path, plan, prompts, refs)


@pytest.fixture
def passed_card(run, fake_gemini):
    """A01 finished on its first attempt: final/A01.png, chosen.json try1 passed."""
    fake_gemini.images.append(card_png("purple", "yellow"))
    fake_gemini.texts.append(qa_answer(True))
    result = run.produce()
    assert result["status"] == "passed"
    fake_gemini.calls.clear()
    return run


# ---------------------------------------------------------------- happy path and retries

def test_happy_path_writes_final_logs_and_costs(run, fake_gemini):
    fake_gemini.images.append(card_png("purple", "yellow"))
    fake_gemini.texts.append(qa_answer(True))
    result = run.produce()
    assert result["status"] == "passed" and result["chosen"] == "try1.png"
    assert [a["try"] for a in result["attempts"]] == [1]
    assert result["attempts"][0]["qa_pass"] is True and result["attempts"][0]["checks_passed"] == 8  # 7 judge checks + the pixel check
    final = Image.open(run.final)
    assert final.size == (430, 480)
    assert same_pixels(final, to_card(make_card("purple", "yellow"), 480))
    assert run.chosen() == {"file": "try1.png", "status": "passed"}
    request = run.request(1)
    assert request["model"] == cardgen.GEN_MODEL and request["prompt_file"] == "card_v7.md" and request["fix"] == ""
    assert request["card"] == run.card and len(request["refs"]) == 12 and all("sha256" in r for r in request["refs"])
    assert request["text_parts"][-1].startswith("Task:") and run.card["subject"] in request["text_parts"][-1]
    response = json.loads((run.card_dir / "try1.response.json").read_text(encoding="utf-8"))
    assert "image_bytes" not in response and response["est_cost_usd"] == GEN_COST
    qa = run.qa(1)
    assert qa["pass"] is True and qa["checks"]["bg_colour"]["pass"] is True
    rows = cost_rows(run.out)
    assert [(r["kind"], r["card"]) for r in rows] == [("generate", "A01"), ("qa", "A01")]
    assert rows[0]["usd"] == round(GEN_COST, 5) and rows[1]["usd"] == round(QA_COST, 5)
    sent = [c for c in fake_gemini.calls_of("image")]
    assert len(sent) == 1 and sent[0][1] == cardgen.GEN_MODEL and sent[0][3] == {"aspect_ratio": "1:1", "image_size": "1K"}
    assert sum(p["type"] == "image" for p in sent[0][2]) == 12  # the 12 production references go with every request


def test_jpeg_answers_are_kept_as_jpg(run, fake_gemini):
    jpeg = io.BytesIO()
    make_card("purple").save(jpeg, "JPEG")
    fake_gemini.images.append((jpeg.getvalue(), "image/jpeg"))
    fake_gemini.texts.append(qa_answer(True))
    result = run.produce()
    assert result["chosen"] == "try1.jpg" and (run.card_dir / "try1.jpg").exists()
    assert Image.open(run.final).size == (430, 480)


def test_retry_keeps_the_producer_note_and_adds_the_reviewer_fix(run, fake_gemini):
    fake_gemini.images.extend([card_png("purple", "yellow"), card_png("purple", "red"), card_png("purple", "blue")])
    fake_gemini.texts.extend([qa_answer(False, "make the handle bigger", failing=("subject", "framing", "detail")),
                              qa_answer(False, "add the spout", failing=("subject",)),
                              qa_answer(False, "add the lid", failing=("subject", "style"))])
    result = run.produce(retries=2, first_fix="keep the lid blue")
    assert len(fake_gemini.calls_of("image")) == 3  # at most retries + 1 images
    assert len(fake_gemini.calls_of("text")) == 3
    assert run.request(1)["fix"] == "keep the lid blue"
    assert run.request(2)["fix"] == "keep the lid blue make the handle bigger"
    assert run.request(3)["fix"] == "keep the lid blue add the spout"  # the newest reviewer fix, the producer's note kept
    assert "- Correction from the art review of the previous attempt: keep the lid blue add the spout" in run.request(3)["text_parts"][-1]
    assert run.request(1)["text_parts"][-1].endswith("- Correction from the art review of the previous attempt: keep the lid blue")
    assert result["status"] == "accepted_with_issues"
    assert result["chosen"] == "try2.png"  # the attempt with most checks passed (7 of 8) is kept
    assert run.chosen() == {"file": "try2.png", "status": "accepted_with_issues"}
    assert same_pixels(Image.open(run.final), to_card(make_card("purple", "red"), 480))
    assert [a["failed"] for a in result["attempts"]] == [["subject", "framing", "detail"], ["subject"], ["subject", "style"]]


def test_retries_zero_means_one_attempt(run, fake_gemini):
    fake_gemini.images.append(card_png("purple"))
    fake_gemini.texts.append(qa_answer(False, "bigger"))
    result = run.produce(retries=0)
    assert result["status"] == "accepted_with_issues" and len(result["attempts"]) == 1
    assert len(fake_gemini.calls_of("image")) == 1


def test_no_qa_makes_one_image_and_marks_it_unchecked(run, fake_gemini):
    fake_gemini.images.append(card_png("purple"))
    result = run.produce(use_qa=False)
    assert result["status"] == "unchecked" and result["attempts"][0]["qa_pass"] is None
    assert fake_gemini.calls_of("text") == []
    assert run.chosen() == {"file": "try1.png", "status": "unchecked"}
    assert not (run.card_dir / "try1.qa.json").exists()
    assert [r["kind"] for r in cost_rows(run.out)] == ["generate"]


def test_pixel_colour_check_overrules_the_judge(run, fake_gemini):
    fake_gemini.images.extend([card_png("teal"), card_png("purple")])
    fake_gemini.texts.extend([qa_answer(True), qa_answer(True)])
    result = run.produce(retries=1)
    assert result["status"] == "passed" and result["chosen"] == "try2.png"
    first = run.qa(1)
    assert first["pass"] is False and first["checks"]["bg_colour"]["pass"] is False
    assert run.request(2)["fix"].startswith("Make the background purple: ")
    assert result["attempts"][0]["failed"] == ["bg_colour"]


def test_generation_error_is_recorded_and_retried(run, fake_gemini):
    fake_gemini.images.extend([gemini_image.GeminiError("HTTP 500 for POST interactions: boom", 500), card_png("purple")])
    fake_gemini.texts.append(qa_answer(True))
    result = run.produce(retries=1)
    assert result["status"] == "passed" and result["chosen"] == "try2.png"
    assert (run.card_dir / "try1.error.txt").read_text(encoding="utf-8").startswith("HTTP 500")
    assert result["attempts"][0] == {"try": 1, "error": "HTTP 500 for POST interactions: boom"}
    assert not (run.card_dir / "try1.response.json").exists()


def test_all_calls_failing_gives_status_failed(run, fake_gemini):
    fake_gemini.images.extend([gemini_image.GeminiError("HTTP 500", 500)] * 3)
    result = run.produce(retries=2)
    assert result["status"] == "failed" and not run.final.exists()
    assert len(fake_gemini.calls_of("image")) == 3


# ---------------------------------------------------------------- the empty balance (W023, W025)

def test_billing_error_during_generation_keeps_the_final_and_stops(passed_card, fake_gemini):
    run = passed_card
    before, chosen_before = sha(run.final), run.chosen()
    fake_gemini.images.append(gemini_image.BillingError(gemini_image.BILLING_HELP, 402))
    result = run.produce(retries=2, first_fix="redo it")
    assert result["status"] == "interrupted"
    assert cardgen.STOP.is_set()
    assert len(fake_gemini.calls_of("image")) == 1  # no retry after a billing answer
    assert sha(run.final) == before and run.chosen() == chosen_before
    assert (run.card_dir / "try2.error.txt").exists() and not (run.card_dir / "try2.png").exists()
    cardgen.write_summary(run.plan, run.out)
    summary = json.loads((run.out / "summary.json").read_text(encoding="utf-8"))
    assert summary["cards"]["A01"]["status"] == "passed" and summary["cards"]["A01"]["chosen"] == "try1.png"


def test_billing_error_during_qa_keeps_the_final_then_a_rerun_reviews_the_waiting_attempt(passed_card, fake_gemini):
    run = passed_card
    before, chosen_before = sha(run.final), run.chosen()
    fake_gemini.images.append(card_png("purple", "red"))
    fake_gemini.texts.append(gemini_image.BillingError(gemini_image.BILLING_HELP, 402))
    result = run.produce(retries=1, first_fix="redo it")
    assert result["status"] == "interrupted" and cardgen.STOP.is_set()
    assert sha(run.final) == before and run.chosen() == chosen_before
    assert (run.card_dir / "try2.png").exists()
    waiting = run.qa(2)
    assert waiting["pass"] is None and "balance is empty" in waiting["qa_error"]
    assert result["attempts"][-1]["qa_pass"] is None

    cardgen.STOP.clear()  # the balance was topped up; the same command runs again
    fake_gemini.calls.clear()
    fake_gemini.texts.append(qa_answer(True))
    result = run.produce(retries=1, first_fix="redo it")
    assert fake_gemini.calls_of("image") == []  # the waiting image is reviewed, not drawn again
    assert len(fake_gemini.calls_of("text")) == 1
    assert result["status"] == "passed" and result["chosen"] == "try2.png"
    assert run.chosen() == {"file": "try2.png", "status": "passed"}
    assert sha(run.final) != before
    assert same_pixels(Image.open(run.final), to_card(make_card("purple", "red"), 480))
    assert not (run.card_dir / "try3.request.json").exists()


def test_regen_on_an_empty_balance_exits_with_the_message(passed_card, fake_gemini):
    run = passed_card
    before = sha(run.final)
    fake_gemini.images.append(card_png("purple", "red"))
    fake_gemini.texts.append(gemini_image.BillingError(gemini_image.BILLING_HELP, 402))
    with pytest.raises(SystemExit) as stop:
        cardgen.regen(run.plan_path, "A01", "redo it", True)
    assert str(stop.value) == gemini_image.BILLING_HELP
    assert sha(run.final) == before and run.chosen() == {"file": "try1.png", "status": "passed"}
    assert (run.out / "summary.md").exists()


def test_qa_outage_leaves_the_new_image_unchecked(passed_card, fake_gemini):
    """A QA call that fails for any reason but billing: the regen's new image stands, honestly marked unchecked
    (choose try1 brings the earlier one back); only the empty balance keeps the earlier final (W025)."""
    run = passed_card
    fake_gemini.images.append(card_png("purple", "red"))
    fake_gemini.texts.append(gemini_image.GeminiError("HTTP 503", 503))
    result = run.produce(retries=1)
    assert result["status"] == "unchecked" and result["chosen"] == "try2.png"
    assert len(fake_gemini.calls_of("image")) == 1  # no verdict to retry against: nothing new is drawn
    assert run.qa(2)["pass"] is None
    assert run.chosen() == {"file": "try2.png", "status": "unchecked"}


def test_a_waiting_attempt_that_fails_review_counts_as_an_attempt(run, fake_gemini):
    fake_gemini.images.append(card_png("purple", "red"))
    fake_gemini.texts.append(gemini_image.GeminiError("HTTP 503", 503))
    assert run.produce(retries=1)["status"] == "unchecked"  # try1 waits without a verdict
    fake_gemini.calls.clear()
    fake_gemini.texts.extend([qa_answer(False, "bigger"), qa_answer(True)])
    fake_gemini.images.append(card_png("purple", "blue"))
    result = run.produce(retries=1)
    assert [a["try"] for a in result["attempts"]] == [1, 2]  # the reviewed attempt plus one new one, not two
    assert len(fake_gemini.calls_of("image")) == 1
    assert result["status"] == "passed" and result["chosen"] == "try2.png"
    assert run.request(2)["fix"] == "bigger"
    assert run.chosen() == {"file": "try2.png", "status": "passed"}


def test_run_reviews_a_card_left_unchecked(run, fake_gemini, plan_path):
    fake_gemini.images.append(card_png("purple"))
    assert run.produce(use_qa=False)["status"] == "unchecked"
    fake_gemini.calls.clear()
    fake_gemini.texts.append(qa_answer(True))
    assert cardgen.main(["run", str(plan_path), "--cards", "A01", "--workers", "1"]) == 0
    assert fake_gemini.calls_of("image") == [] and len(fake_gemini.calls_of("text")) == 1
    assert run.chosen() == {"file": "try1.png", "status": "passed"}


def test_run_skips_finished_cards_and_builds_sheets(run, fake_gemini, plan_path, capsys):
    fake_gemini.images.append(card_png("purple"))
    fake_gemini.texts.append(qa_answer(True))
    assert cardgen.main(["run", str(plan_path), "--cards", "A01", "--workers", "1", "--retries", "0"]) == 0
    out = capsys.readouterr().out
    assert "1 card(s) to make" in out and "A01 Brass Lantern: passed after 1 attempt(s)" in out
    assert (run.out / "sheets" / "variant_A.png").exists() and (run.out / "sheets" / "overview.png").exists()
    assert (run.out / "summary.md").exists()
    fake_gemini.calls.clear()
    assert cardgen.main(["run", str(plan_path), "--cards", "A01", "--workers", "1"]) == 0  # nothing queued: no call is made
    assert fake_gemini.calls == []
    assert "0 card(s) to make" in capsys.readouterr().out


def test_run_rejects_an_invalid_plan_before_any_call(run, fake_gemini, plan_path, plan):
    plan["variants"][0]["cards"][0]["category"] = 5
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(SystemExit, match="Plan invalid"):
        cardgen.main(["run", str(plan_path)])
    assert fake_gemini.calls == []


# ---------------------------------------------------------------- regen, choose

def test_regen_replaces_the_final_and_frames_it(passed_card, fake_gemini, monkeypatch):
    run = passed_card
    (run.out / "reframe_log.json").write_text("{}", encoding="utf-8")  # the set has been framed before
    monkeypatch.setattr(reframe, "raw_box", lambda path, log_dir=None, card="": list(OBJECT_BOX))
    fake_gemini.images.append(card_png("purple", "red"))
    fake_gemini.texts.append(qa_answer(True))
    cardgen.regen(run.plan_path, "A01", "make it rounder", True)
    assert run.request(2)["fix"] == "make it rounder"
    assert run.chosen() == {"file": "try2.png", "status": "passed"}
    assert fake_gemini.calls_of("image") == [] or len(fake_gemini.calls_of("image")) == 1  # no outpainting: the window fits
    log = json.loads((run.out / "reframe_log.json").read_text(encoding="utf-8"))
    assert log["A01"]["fill"] == "none" and log["A01"]["extent"] == pytest.approx(0.82, abs=0.01)
    assert (run.out / "final_prev" / "A01.png").exists()
    final = Image.open(run.final)
    assert final.size == (430, 480)
    assert not same_pixels(final, to_card(make_card("purple", "red"), 480))  # framed, not just centre-cropped
    assert final.getpixel((215, 240)) == (230, 30, 30)  # the red object is still in the middle
    assert (run.out / "sheets" / "variant_A.png").exists()


def test_regen_without_an_earlier_framing_only_rebuilds_sheets(passed_card, fake_gemini):
    run = passed_card
    fake_gemini.images.append(card_png("purple", "red"))
    fake_gemini.texts.append(qa_answer(True))
    cardgen.regen(run.plan_path, "A01", "", True)
    assert not (run.out / "reframe_log.json").exists()
    assert same_pixels(Image.open(run.final), to_card(make_card("purple", "red"), 480))


def test_choose_restores_an_earlier_attempt_byte_for_byte(run, fake_gemini, tmp_path):
    fake_gemini.images.extend([card_png("purple", "yellow"), card_png("purple", "red")])
    fake_gemini.texts.extend([qa_answer(False, "bigger"), qa_answer(True)])
    assert run.produce(retries=1)["chosen"] == "try2.png"
    expected = tmp_path / "expected.png"
    to_card(Image.open(run.card_dir / "try1.png").convert("RGB"), 480).save(expected)
    cardgen.choose(run.plan_path, "A01", "try1", frame=False)
    assert run.final.read_bytes() == expected.read_bytes()
    assert run.chosen() == {"file": "try1.png", "status": "accepted_with_issues", "by": "choose"}
    summary = json.loads((run.out / "summary.json").read_text(encoding="utf-8"))
    assert summary["cards"]["A01"]["chosen"] == "try1.png" and summary["cards"]["A01"]["status"] == "accepted_with_issues"
    cardgen.choose(run.plan_path, "A01", "TRY2", frame=False)
    assert run.chosen()["file"] == "try2.png" and run.chosen()["status"] == "passed"


def test_choose_refuses_an_attempt_without_an_image(passed_card):
    with pytest.raises(SystemExit, match="try7 has no image"):
        cardgen.choose(passed_card.plan_path, "A01", "try7", frame=False)


# ---------------------------------------------------------------- summary and the cost line

def test_summary_counts_one_total_without_double_counting(run, fake_gemini, plan):
    fake_gemini.images.append(card_png("purple"))
    fake_gemini.texts.append(qa_answer(True))
    run.produce()
    second = Run(run.plan_path, plan, (run.template, run.qa_template), run.refs, "A02")
    fake_gemini.images.append(card_png("green"))
    second.produce(use_qa=False)
    cardgen.write_summary(plan, run.out)
    summary = json.loads((run.out / "summary.json").read_text(encoding="utf-8"))
    gen_qa = round(2 * GEN_COST + QA_COST, 2)
    assert summary["est_cost_usd"] == gen_qa
    assert summary["images_generated"] == 2 and summary["qa_reviews"] == 1 and summary["first_try_pass"] == 1
    assert summary["status_counts"] == {"passed": 1, "accepted_with_issues": 0, "unchecked": 1, "failed": 0, "not_started": 28}
    line = cardgen.cost_line(run.out, summary["est_cost_usd"])
    assert line.startswith(f"Estimated cost: ${gen_qa:.2f} for generation and QA (from the attempt files)")
    assert "+" not in line and "costs.jsonl" not in line  # generate and qa rows are never added a second time
    assert "began before costs.jsonl" not in line
    costs.log(run.out, "outpaint", "A01", 0.0354)
    costs.log(run.out, "vision", "A01", 0.0014)
    line = cardgen.cost_line(run.out, summary["est_cost_usd"])
    # the other kinds are added once, from costs.jsonl, each rounded to a tenth of a cent before the sum
    assert f"+ $0.036 for outpaint $0.035, vision $0.001 (costs.jsonl) = ${gen_qa + 0.036:.2f}" in line
    assert line.endswith("Text-model rates unverified.")
    text = (run.out / "summary.md").read_text(encoding="utf-8")
    assert "| A02 | Tin Kettle | unchecked | 1 | - |  |" in text
    assert "| A01 | Brass Lantern | passed | 1 | - |  |" in text


def test_summary_open_fix_shows_only_for_unresolved_cards(run, fake_gemini, plan):
    fake_gemini.images.append(card_png("purple"))
    fake_gemini.texts.append(qa_answer(False, "make the handle bigger", failing=("framing",)))
    run.produce(retries=0)
    cardgen.write_summary(plan, run.out)
    text = (run.out / "summary.md").read_text(encoding="utf-8")
    assert "| A01 | Brass Lantern | accepted_with_issues | 1 | framing | make the handle bigger |" in text


def test_older_than_log_only_for_sets_begun_before_the_log(run, fake_gemini):
    assert cardgen.older_than_log(run.out) is False  # nothing generated yet
    fake_gemini.images.append(card_png("purple"))
    fake_gemini.texts.append(qa_answer(True))
    run.produce()
    assert cardgen.older_than_log(run.out) is False
    (run.out / "costs.jsonl").unlink()
    assert cardgen.older_than_log(run.out) is True
    assert "began before costs.jsonl existed" in cardgen.cost_line(run.out, 0.05)
