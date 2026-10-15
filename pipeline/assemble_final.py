"""Assemble a set's deliverable: one image per card from the chosen source folder, plus its set window.

    python -I pipeline/assemble_final.py sets/<slug>/plan.json B --from gpt_v7/final [--override B03=gpt_v7_clean/final ...]

Copies each card of the variant into <set>/final_set/<id>.png and records where each one came from in
final_set/sources.json, with the route, folder and the pick that decided it. Then lays the variant into its
set template (set_window.py) from final_set/. final_set/ is what goes into the brief's "final sets" templates.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import set_window  # noqa: E402


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path)
    parser.add_argument("variant")
    parser.add_argument("--from", dest="source", required=True, help="default folder of finished cards, relative to the plan")
    parser.add_argument("--override", nargs="*", default=[], help="card=folder pairs for single cards")
    parser.add_argument("--note", default="", help="why these sources (for sources.json)")
    args = parser.parse_args(argv)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    folder = args.plan.parent
    variant = next(v for v in plan["variants"] if v["id"] == args.variant)
    overrides = dict(item.split("=", 1) for item in args.override)
    out = folder / "final_set"
    out.mkdir(exist_ok=True)
    sources = {"set": plan["set"], "variant": args.variant, "note": args.note, "cards": {}}
    for card in variant["cards"]:
        src_dir = overrides.get(card["id"], args.source)
        src = folder / src_dir / f"{card['id']}.png"
        shutil.copyfile(src, out / f"{card['id']}.png")
        sources["cards"][card["id"]] = {"name": card["name"], "stars": card.get("stars"), "from": src_dir}
    (out / "sources.json").write_text(json.dumps(sources, indent=1), encoding="utf-8")
    window = set_window.build(args.plan, args.variant, "final_set", None)
    print(f"{len(variant['cards'])} cards -> {out}; window {window}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
