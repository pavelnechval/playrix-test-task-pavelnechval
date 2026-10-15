"""Regenerate a list of cards with the producer's notes, then build a before/after sheet for re-rating.

    python -I pipeline/redo.py sets/ratings/redo_round1.json

The JSON holds {"title", "cards": [{"code", "plan", "card", "fix", "reason"}, ...]}, with plan paths relative to
the project root. For each card, the current final image is kept as <spec folder>/<spec name>/before/<code>.png
(only the first time, so a re-run still compares with the original), then cardgen's regen makes a new one.
The note goes into every attempt, and a QA reviewer's fix is added to it, never swapped in.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import cardgen  # noqa: E402
from sheets import build_sheet  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    spec_path = Path(argv[0])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = spec_path.parent / spec_path.stem
    (out / "before").mkdir(parents=True, exist_ok=True)
    for job in spec["cards"]:
        plan = ROOT / job["plan"]
        before = out / "before" / f"{job['code']}.png"
        if not before.exists():
            shutil.copyfile(plan.parent / "final" / f"{job['card']}.png", before)
        print(f"--- {job['code']}: {job['reason']}", flush=True)
        try:
            cardgen.regen(plan, job["card"], job["fix"], True)
        except Exception as err:  # one card's failure must not stop the rest
            print(f"{job['code']}: regen crashed ({err!r}); the previous image is still the final", flush=True)
    rows = [("before", [(j["code"], out / "before" / f"{j['code']}.png") for j in spec["cards"]]),
            ("after", [(j["code"], (ROOT / j["plan"]).parent / "final" / f"{j['card']}.png") for j in spec["cards"]])]
    build_sheet(rows, out / "before_after.png", 260, spec.get("title", "Before and after"))
    print(f"Before/after sheet: {out / 'before_after.png'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
