"""BENCH-02: prompt v2 and reference pack v2 on Nano Banana 2.1, two samples per hidden target.

    python -I experiments/BENCH-02/bench.py prepare   # build refs + expanded prompts (no API calls)
    python -I experiments/BENCH-02/bench.py run       # 4 targets x 2 samples (paid API calls)
    python -I experiments/BENCH-02/bench.py sheets    # real | BENCH-01 v1 | v2 sample a | v2 sample b

Same hidden targets, subject text, model and settings as BENCH-01, so the only
changes are the prompt (prompt_v2.md) and the reference pack (12 Miro originals,
3 per category, chosen to show the rules BENCH-01 feedback asked for). Both
change at once, so the result measures their combined effect.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

from PIL import Image  # noqa: E402

import gemini_image  # noqa: E402
from sheets import build_sheet  # noqa: E402

CARDS = ROOT / "references" / "miro_v1" / "cards"
PROMPT_FILE = HERE / "prompt_v2.md"
BENCH01 = ROOT / "experiments" / "BENCH-01"
MODEL = {"model": "gemini-nano-banana-2.1", "aspect_ratio": "1:1", "image_size": "1K"}
SAMPLES = ("a", "b")
PRICE_PER_IMAGE_USD = 0.0336  # 1K output; Gemini API pricing page as read on 2026-10-13

TARGETS = [  # identical to BENCH-01; never sent to the model
    {"id": "T1", "name": "Bottle", "category": 1, "cell": "r05c07", "subject": "a sports water bottle"},
    {"id": "T2", "name": "Tea Cup", "category": 2, "cell": "r07c06", "subject": "a tea cup"},
    {"id": "T3", "name": "Bumpers", "category": 3, "cell": "r06c02", "subject": "a bumper car (a fairground dodgem)"},
    {"id": "T4", "name": "Lighthouse", "category": 4, "cell": "r14c08", "subject": "a lighthouse"},
]
STYLE_PACK = [  # what each card demonstrates; "brief" = category example on pp. 3-4
    {"id": "R1", "name": "Fan Fold", "category": 1, "cell": "r02c07", "shows": "pattern bg, complementary colour (brief)"},
    {"id": "R2", "name": "Popsicle", "category": 1, "cell": "r02c09", "shows": "rays centred behind, complementary colour"},
    {"id": "R3", "name": "Glove", "category": 1, "cell": "r05c01", "shows": "rays centred behind, brown on blue"},
    {"id": "R4", "name": "Mojito", "category": 2, "cell": "r02c04", "shows": "plain surface + wall, one colour family (brief)"},
    {"id": "R5", "name": "Beach Bag", "category": 2, "cell": "r03c07", "shows": "plain surface, striped wall (brief)"},
    {"id": "R6", "name": "Sneakers", "category": 2, "cell": "r05c04", "shows": "plain surface, warm gradient"},
    {"id": "R7", "name": "Computer", "category": 3, "cell": "r01c06", "shows": "realistic desk, plain gradient wall"},
    {"id": "R8", "name": "Boxing Gloves", "category": 3, "cell": "r05c10", "shows": "wooden floor, simple striped wall"},
    {"id": "R9", "name": "Ice Tray", "category": 3, "cell": "r02c02", "shows": "wooden table, rays behind"},
    {"id": "R10", "name": "Field Ball", "category": 4, "cell": "r05c03", "shows": "close, low angle on grass (brief)"},
    {"id": "R11", "name": "Coaster", "category": 4, "cell": "r06c09", "shows": "low angle, cropped, clean sky (brief)"},
    {"id": "R12", "name": "Ferris Wheel", "category": 4, "cell": "r06c01", "shows": "low angle, large, cropped against sky"},
]
CATEGORY_SHORT = {
    1: "category 1: floating object, simple background",
    2: "category 2: object on a plain surface, simple background",
    3: "category 3: object on a realistic surface, simple back wall",
    4: "category 4: object inside a realistic environment, low angle",
}


def load_template() -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    name = None
    for line in PROMPT_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            name = line[3:].strip()
            sections[name] = []
        elif name:
            sections[name].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def ref_path(ref: dict) -> Path:
    return HERE / "refs" / f"{ref['id']}_{ref['cell']}.png"


def truth_path(target: dict) -> Path:
    return BENCH01 / "ground_truth" / "miro_v1" / f"{target['id']}_{target['cell']}.png"


def request_for(target: dict, template: dict[str, str]) -> list[tuple[str, str]]:
    content = [("text", template["INTRO"].format(n_refs=len(STYLE_PACK)))]
    for ref in STYLE_PACK:
        label = template["REFERENCE_LABEL"].format(ref_id=ref["id"], category_short=CATEGORY_SHORT[ref["category"]])
        content += [("text", label), ("image", ref_path(ref).relative_to(ROOT).as_posix())]
    rules = template[f"CATEGORY_{target['category']}"]
    content.append(("text", template["TASK"].format(subject=target["subject"], category=target["category"], category_rules=rules)))
    return content


def prepare() -> None:
    leaked = {t["cell"] for t in TARGETS} & {r["cell"] for r in STYLE_PACK}
    if leaked:
        raise SystemExit(f"Hidden target(s) in the style pack: {sorted(leaked)}")
    for folder in ("refs", "prompts", "sheets"):
        (HERE / folder).mkdir(exist_ok=True)
    for ref in STYLE_PACK:
        Image.open(CARDS / f"{ref['cell']}.png").convert("RGB").save(ref_path(ref))
    template = load_template()
    for target in TARGETS:
        lines = [f"# Expanded request {target['id']}: {target['name']}, category {target['category']}", ""]
        for kind, value in request_for(target, template):
            lines += [f"[image: {value}]" if kind == "image" else value, ""]
        (HERE / "prompts" / f"{target['id']}.md").write_text("\n".join(lines), encoding="utf-8")
    build_sheet([("Style pack v2", [(r["id"], ref_path(r)) for r in STYLE_PACK])],
                HERE / "sheets" / "refs_overview.png", 150, "BENCH-02 reference pack (12 Miro originals)")
    print("Prepared refs/, prompts/ and sheets/refs_overview.png")


def run() -> None:
    template = load_template()
    print(f"Up to {len(TARGETS) * len(SAMPLES)} images; estimated output cost ${PRICE_PER_IMAGE_USD * len(TARGETS) * len(SAMPLES):.2f} plus input tokens")
    for folder in ("runs", "outputs"):
        (HERE / folder).mkdir(exist_ok=True)
    for target in TARGETS:
        content = request_for(target, template)
        parts = [gemini_image.text_part(v) if k == "text" else gemini_image.image_part((ROOT / v).read_bytes()) for k, v in content]
        for sample in SAMPLES:
            stem = f"v2_nb21_{target['id']}{sample}"
            if list((HERE / "outputs").glob(stem + ".*")):
                print(f"skip {stem}: output exists")
                continue
            record = {
                "run": stem, "experiment": "BENCH-02", "reference_set": "miro_v1", "prompt_file": PROMPT_FILE.name,
                "target": target, "sample": sample, **MODEL, "thinking_level": "model default",
                "content": [{"text": v} if k == "text" else {"image": v, "sha256": hashlib.sha256((ROOT / v).read_bytes()).hexdigest()}
                            for k, v in content],
                "sent_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            (HERE / "runs" / f"{stem}.request.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
            try:
                result = gemini_image.generate_image(MODEL["model"], parts, aspect_ratio=MODEL["aspect_ratio"], image_size=MODEL["image_size"])
            except gemini_image.GeminiError as err:
                (HERE / "runs" / f"{stem}.error.txt").write_text(str(err), encoding="utf-8")
                print(f"FAILED {stem}: {str(err)[:400]}")
                continue
            extension = ".jpg" if "jpeg" in result["mime_type"] else ".png"
            (HERE / "outputs" / f"{stem}{extension}").write_bytes(result.pop("image_bytes"))
            result["est_output_cost_usd"] = PRICE_PER_IMAGE_USD
            result["received_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            (HERE / "runs" / f"{stem}.response.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"ok {stem}: {result['elapsed_s']} s")


def sheets() -> None:
    rows = []
    for target in TARGETS:
        items = [("real", truth_path(target))]
        items += [("v1", p) for p in sorted((BENCH01 / "outputs").glob(f"miro_v1_nb21_{target['id']}.*"))]
        items += [(f"v2-{s}", p) for s in SAMPLES for p in sorted((HERE / "outputs").glob(f"v2_nb21_{target['id']}{s}.*"))]
        rows.append((f"{target['id']} {target['name']} (C{target['category']})", items))
    build_sheet(rows, HERE / "sheets" / "compare_card_size.png", 66, "BENCH-02 at real card size (66 px tall)")
    build_sheet(rows, HERE / "sheets" / "compare_large.png", 300, "BENCH-02: real | v1 (BENCH-01) | v2 samples a, b")
    print("Sheets written to sheets/")


def main(argv: list[str]) -> int:
    command = argv[0] if argv else ""
    if command == "prepare":
        prepare()
    elif command == "run":
        run()
    elif command == "sheets":
        sheets()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
