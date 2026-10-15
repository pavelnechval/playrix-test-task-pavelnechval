"""Pixel check of a card's background colour family against the plan's bg_color (no model involved).

    python -I pipeline/colour_check.py sets/<slug>/plan.json    # audit every finished card of a set

cardgen.py runs the same check after the vision QA. It measures the outer ring of the card (for category 3,
the wall: the top band and the upper side strips) and names each saturated pixel's colour family.
- fail: the main family is neither the planned one nor its neighbour on the colour wheel, or 30%+ is teal;
- warn: the main family is the planned one's neighbour (orange for yellow, pink for purple);
- category 4 is skipped: its backdrop is a scene, not one colour.
On the 84 Cinema cards of categories 1-3 it failed exactly the two cards whose background ignored the plan
(PP-A08 teal instead of orange, LI-A04 red instead of green), both rated 3 or lower by Pavel (W016).
"""

from __future__ import annotations

import colorsys
import json
import sys
from pathlib import Path

from PIL import Image

RING = ["red", "orange", "yellow", "green", "teal", "blue", "purple", "pink"]
HUE_LIMITS = [(12, "red"), (40, "orange"), (68, "yellow"), (160, "green"), (195, "teal"), (255, "blue"),
              (290, "purple"), (345, "pink"), (360, "red")]
TEAL_LIMIT = 0.3


def _family(r: int, g: int, b: int) -> str:
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if s < 0.25 or v < 0.30:
        return "grey/dark"
    name = next(n for limit, n in HUE_LIMITS if h * 360 < limit)
    return "pink" if name == "red" and s < 0.55 else name  # pastel and salmon pinks share red's hue


def measure(image: Image.Image, category: int) -> dict[str, float]:
    """Share of each colour family in the background area, largest first."""
    img = image.convert("RGB").resize((240, 268))
    w, h = img.size
    px = img.load()
    edge = round(w * 0.06)
    counts: dict[str, int] = {}
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if category == 3:  # the wall: floors are often wood, so only the top band and upper side strips
                keep = y < h * 0.10 or (y < h * 0.5 and (x < edge or x >= w - edge))
            else:
                keep = x < edge or x >= w - edge or y < edge or y >= h - edge
            if keep:
                name = _family(*px[x, y])
                counts[name] = counts.get(name, 0) + 1
    total = sum(counts.values())
    return {k: round(v / total, 2) for k, v in sorted(counts.items(), key=lambda kv: -kv[1])}


def backdrop_family(image: Image.Image) -> str:
    """Main colour family of the backdrop (wall, sky or plain background) in any category: top band and upper sides."""
    return next((name for name in measure(image, 3) if name != "grey/dark"), "grey/dark")


def _near(a: str, b: str) -> bool:
    if a not in RING or b not in RING:
        return False
    d = abs(RING.index(a) - RING.index(b))
    return min(d, len(RING) - d) <= 1


def check(image: Image.Image, card: dict) -> dict | None:
    """None for category 4, otherwise a QA-style check: {"pass", "level", "why", "measured"}."""
    if card["category"] == 4:
        return None
    shares = measure(image, card["category"])
    top, planned = next(iter(shares)), card["bg_color"]
    measured = f"{top} ({shares[top]:.0%} of the background)"
    if shares.get("teal", 0) >= TEAL_LIMIT or (top != planned and not _near(top, planned)):
        return {"pass": False, "level": "fail", "measured": shares,
                "why": f"background is {measured}; the plan asks for {planned}"}
    level = "ok" if top == planned else "warn"
    return {"pass": True, "level": level, "measured": shares,
            "why": f"background is {measured}; planned {planned}"}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    plan_path = Path(argv[0])
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    counts = {"ok": 0, "warn": 0, "fail": 0}
    for variant in plan["variants"]:
        for card in variant["cards"]:
            final = plan_path.parent / "final" / f"{card['id']}.png"
            result = check(Image.open(final), card) if final.exists() else None
            if result:
                counts[result["level"]] += 1
                if result["level"] != "ok":
                    print(f"{result['level'].upper():4} {card['id']} {card['name']}: {result['why']}")
    print(f"{plan['set']}: {counts}")
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
