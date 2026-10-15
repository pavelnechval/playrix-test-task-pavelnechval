"""Blind comparison of the two image routes (Gemini: final/, ChatGPT: gpt/final/) for every variant of a plan.

    python -I pipeline/compare_routes.py sets/<slug>/plan.json [--seed 7]

For each variant with both routes finished, it lays both into the set template (set_window.py) and gives them
blind codes (for example A1 and A2) in a random order. It writes to <plan folder>/compare/:
- window_<code>.jpg, the two set windows;
- cards_<variant>.png, the two card rows one above the other;
- compare.md, what to judge plus the measured set check per code;
- blind_key.json, which route each code is. Open it only after judging.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from PIL import Image  # noqa: E402

import colour_check  # noqa: E402
import set_window  # noqa: E402
from cardgen import SHORT, WINDOW_PAIRS  # noqa: E402
from sheets import build_sheet  # noqa: E402

ROUTES = {"gemini": "final", "chatgpt": "gpt/final"}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--gpt-dir", default="gpt", help="the ChatGPT route folder, e.g. gpt_v7")
    args = parser.parse_args(argv)
    ROUTES["chatgpt"] = f"{args.gpt_dir}/final"
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    folder = args.plan.parent
    out = folder / "compare"
    out.mkdir(exist_ok=True)
    # Every set gets its own order: the same seed for every set put ChatGPT first in all four final sets (W021),
    # so position and preference could not be told apart in that round.
    rng = random.Random(f"{args.seed}:{plan['set']}" if args.seed is not None else None)
    key, lines = {}, [f"# {plan['set']}: Gemini vs ChatGPT, blind", "",
                      "For each variant, two versions of the same plan (same card text and references) carry codes 1 and 2 "
                      "in a random order. Judge the window as a set (one world, mood, palette, build-up) and the cards "
                      "against the real ones. Then open blind_key.json.", "",
                      "| Code | Backdrops measured (cards 1-5 / 6-10) | Families | Lead colour cards (planned family) | Same-colour neighbours |",
                      "|---|---|---|---|---|"]
    for variant in plan["variants"]:
        vid = variant["id"]
        ready = all((folder / d / f"{c['id']}.png").exists() for d in ROUTES.values() for c in variant["cards"])
        if not ready:
            lines.append(f"| {vid}: not both routes finished | | | | |")
            continue
        routes = list(ROUTES)
        rng.shuffle(routes)
        rows = []
        for n, route in enumerate(routes, 1):
            code = f"{vid}{n}"
            key[code] = route
            final_dir = ROUTES[route]
            window = set_window.build(args.plan, vid, final_dir, None)
            shutil.copyfile(window.with_name(f"window_{vid}_preview.jpg"), out / f"window_{code}.jpg")
            paths = [folder / final_dir / f"{c['id']}.png" for c in variant["cards"]]
            fams = [colour_check.backdrop_family(Image.open(p)) for p in paths]
            lead = variant.get("lead_color", "")
            same = sum(fams[a] == fams[b] for a, b in WINDOW_PAIRS)
            lines.append(f"| {code} | {' '.join(SHORT[f] for f in fams[:5])} / {' '.join(SHORT[f] for f in fams[5:])} | "
                         f"{len(set(fams))} | {fams.count(lead)} ({lead}) | {same}/13 |")
            rows.append((code, [(f"{c['id']} {c['name']}", p) for c, p in zip(variant["cards"], paths)]))
        build_sheet(rows, out / f"cards_{vid}.png", 200, f"{plan['set']}: variant {vid}, two versions (blind codes)")
    (out / "blind_key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    (out / "compare.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"-> {out} (key in blind_key.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
