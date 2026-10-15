"""Build a rating pack for finished sets: thumbnails + manifest (for the Excel rating workbook)
and one labelled sheet per set for an external model (real reference cards on top, variants below).

    python -I pipeline/review_pack.py OUT_DIR sets/<slug>/plan.json [sets/<slug2>/plan.json ...]

Card codes get a set prefix (for example LC-A01), so ratings from several sets can be merged.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from PIL import Image  # noqa: E402

from sheets import build_sheet, to_card  # noqa: E402

REFS_FILE = HERE / "refs_production.json"
CARDS_DIR = HERE.parent / "references" / "miro_v1" / "cards"
THUMB_H = 223  # px; 200 x 223 keeps the card aspect (430:480)
EXTERNAL_REFS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R10", "R11"]  # 10 real cards, all 4 categories


def prefix(set_name: str) -> str:
    words = [w for w in set_name.replace("-", " ").split() if w[0].isalpha() and w.lower() not in ("in", "the", "a", "upon")]
    return "".join(w[0].upper() for w in words[:2])


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    out = Path(argv[0])
    (out / "thumbs").mkdir(parents=True, exist_ok=True)
    (out / "external").mkdir(parents=True, exist_ok=True)
    refs = json.loads(REFS_FILE.read_text(encoding="utf-8"))["refs"]
    ref_rows, manifest = [], {"cards": [], "references": []}
    for ref in refs:
        thumb = out / "thumbs" / f"ref_{ref['id']}.jpg"
        to_card(Image.open(CARDS_DIR / f"{ref['cell']}.png").convert("RGB"), THUMB_H).save(thumb, quality=92)
        manifest["references"].append({**ref, "thumb": str(thumb.resolve())})
    ref_items = [(f"real {r['id']}", CARDS_DIR / f"{r['cell']}.png") for r in refs if r["id"] in EXTERNAL_REFS]
    request_lists = []
    for plan_path in map(Path, argv[1:]):
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        code_prefix = prefix(plan["set"])
        rows, listing = [("Real game cards", ref_items)], []
        for variant in plan["variants"]:
            items = []
            for card in variant["cards"]:
                final = plan_path.parent / "final" / f"{card['id']}.png"
                code = f"{code_prefix}-{card['id']}"
                thumb = out / "thumbs" / f"{code}.jpg"
                Image.open(final).convert("RGB").resize((200, THUMB_H), Image.LANCZOS).save(thumb, quality=92)
                manifest["cards"].append({
                    "code": code, "set": plan["set"], "variant": variant["id"], "concept": variant.get("concept", ""),
                    "card": card["id"], "name": card["name"], "category": card["category"],
                    "thumb": str(thumb.resolve()), "final": str(final.resolve()),
                })
                items.append((code, final))
                listing.append(f"- {code}: {card['name']} (category {card['category']})")
            rows.append((f"Variant {variant['id']}", items))
        slug = plan_path.parent.name
        build_sheet(rows, out / "external" / f"{code_prefix}_{slug}.png", 170, f"{plan['set']} ({plan['genre']}): real cards on top, candidates below")
        request_lists.append((plan["set"], f"{code_prefix}_{slug}.png", listing))
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    lines = [
        "# Rating request for the external model (card sets)",
        "",
        "Attach the four images in this folder, then paste the text below the line. It is the same table format as the BENCH rating requests, so the scores stay comparable.",
        "",
        "---",
        "",
        "Each attached sheet shows one card set for a casual mobile game. The top row (\"real\") shows existing cards from the game. The rows below show three alternative 10-card sets of new card illustrations, labelled with codes, made to match that art style.",
        "",
        "For each code, give:",
        "1. Style match, from 1 (clearly a different style) to 5 (indistinguishable from the real cards' art style).",
        "2. \"Players would notice\": yes or no. Would a regular player notice a mismatch if this card sat next to the real cards at normal card size?",
        "3. One short sentence explaining the main reason.",
        "",
        "Judge rendering (shapes, shading, materials, highlights, outlines), colour (warmth, saturation, background contrast) and composition (camera angle, how large the object is in the frame, how simple the background is). Do not judge which object design is \"nicer\". Return a table with the columns: code | score | notice | commentary.",
        "",
        "After the table, for each set, name the variant you would ship and why, in one sentence.",
        "",
        "Card list:",
    ]
    for set_name, image, listing in request_lists:
        lines += ["", f"{set_name} (image {image}):", *listing]
    (out / "external" / "rating_request.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(manifest['cards'])} cards, {len(manifest['references'])} references -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
