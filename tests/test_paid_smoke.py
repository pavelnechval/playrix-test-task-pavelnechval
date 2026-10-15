"""The one paid test: one real card through generation, QA and framing (about $0.10).

Skipped unless RUN_PAID_TESTS=1 and a Gemini key are set:

    RUN_PAID_TESTS=1 python -m pytest -q tests/test_paid_smoke.py
"""

import json
import shutil

import pytest
from PIL import Image

import cardgen
import reframe

pytestmark = pytest.mark.paid


def test_one_card_generate_qa_reframe(tmp_path):
    folder = tmp_path / "sets" / "smoke-test"
    folder.mkdir(parents=True)
    plan_path = folder / "plan.json"
    shutil.copyfile(cardgen.ROOT / "sets" / "cosy-mystery" / "plan.json", plan_path)
    assert cardgen.main(["run", str(plan_path), "--cards", "A01", "--workers", "1", "--retries", "0"]) == 0
    final = folder / "final" / "A01.png"
    assert final.exists() and Image.open(final).size == (430, 480)
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    assert summary["cards"]["A01"]["status"] in ("passed", "accepted_with_issues", "unchecked")
    assert summary["images_generated"] == 1 and summary["qa_reviews"] == 1
    assert reframe.main([str(plan_path), "--route", "gemini", "--ids", "A01"]) == 0
    assert Image.open(final).size == (430, 480)
    log = json.loads((folder / "reframe_log.json").read_text(encoding="utf-8"))
    assert log["A01"]["fill"] in ("none", "stretch", "outpaint")
    kinds = {json.loads(line)["kind"] for line in (folder / "costs.jsonl").read_text(encoding="utf-8").splitlines()}
    assert {"generate", "qa", "vision"} <= kinds
    cost_line = next(l for l in (folder / "summary.md").read_text(encoding="utf-8").splitlines() if l.startswith("Estimated cost"))
    assert "$" in cost_line
