"""BENCH-01: leave-one-out style benchmark (see plan.md).

    python -I experiments/BENCH-01/bench.py prepare [--refs SET]        # build refs + prompts (no API calls)
    python -I experiments/BENCH-01/bench.py run [--refs SET] [ARM ...]  # generate images (paid API calls)
    python -I experiments/BENCH-01/bench.py sheets [--refs SET]         # blind comparison sheets + score template

SET is the reference source: miro_v1 (default; 430x480 originals from the Miro
board) or pdf_v0 (~60x66 px crops from the PDF). Before each call, the exact
request (prompt text and reference files) is written to runs/. After it come
the redacted response, timing and output image. Existing outputs are skipped,
so an interrupted run can simply be restarted.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

from PIL import Image  # noqa: E402

import gemini_image  # noqa: E402
import refs_from_sheet  # noqa: E402
from sheets import build_sheet  # noqa: E402

REF_SETS = {
    "miro_v1": {"upscale": 1},  # originals downloaded from the Miro board
    "pdf_v0": {"upscale": 4},  # thumbnails cropped from the PDF, sent enlarged 4x (LANCZOS)
}
PROMPT_FILE = HERE / "prompt_v1.md"

TARGETS = [  # hidden: never sent to a model
    {"id": "T1", "name": "Bottle", "category": 1, "cell": "r05c07", "subject": "a sports water bottle"},
    {"id": "T2", "name": "Tea Cup", "category": 2, "cell": "r07c06", "subject": "a tea cup"},
    {"id": "T3", "name": "Bumpers", "category": 3, "cell": "r06c02", "subject": "a bumper car (a fairground dodgem)"},
    {"id": "T4", "name": "Lighthouse", "category": 4, "cell": "r14c08", "subject": "a lighthouse"},
]
STYLE_PACK = [  # basis "brief": category example on pp. 3-4; "rules": our reading of the category rules
    {"id": "R1", "name": "Fan Fold", "category": 1, "cell": "r02c07", "basis": "brief"},
    {"id": "R2", "name": "Popsicle", "category": 1, "cell": "r02c09", "basis": "rules"},
    {"id": "R3", "name": "Mojito", "category": 2, "cell": "r02c04", "basis": "brief"},
    {"id": "R4", "name": "Beach Bag", "category": 2, "cell": "r03c07", "basis": "brief"},
    {"id": "R5", "name": "Fruit Plate", "category": 3, "cell": "r02c06", "basis": "rules"},
    {"id": "R6", "name": "Computer", "category": 3, "cell": "r01c06", "basis": "rules"},
    {"id": "R7", "name": "Field Ball", "category": 4, "cell": "r05c03", "basis": "brief"},
    {"id": "R8", "name": "Coaster", "category": 4, "cell": "r06c09", "basis": "brief"},
]
ARMS = {
    "nb21": {"model": "gemini-nano-banana-2.1", "aspect_ratio": "1:1", "image_size": "1K"},
    "nbpro": {"model": "gemini-3-pro-image", "aspect_ratio": "1:1", "image_size": "1K"},
}
PRICE_PER_IMAGE_USD = {  # output only; Gemini API pricing page as read on 2026-10-13
    ("gemini-nano-banana-2.1", "1K"): 0.0336,
    ("gemini-3-pro-image", "1K"): 0.134,
}
CATEGORY_SHORT = {
    1: "category 1: floating object, simple background",
    2: "category 2: object on a surface, simple background",
    3: "category 3: object on a realistic surface, simple back wall",
    4: "category 4: object inside a realistic environment",
}


def cards_dir(ref_set: str) -> Path:
    return ROOT / "references" / ref_set / "cards"


def ref_path(ref_set: str, ref: dict) -> Path:
    return HERE / "refs" / ref_set / f"{ref['id']}_{ref['cell']}.png"


def truth_path(ref_set: str, target: dict) -> Path:
    return HERE / "ground_truth" / ref_set / f"{target['id']}_{target['cell']}.png"


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request_for(ref_set: str, target: dict, template: dict[str, str]) -> list[tuple[str, str]]:
    """Ordered request content: ("text", text) or ("image", path relative to the project root)."""
    content = [("text", template["INTRO"].format(n_refs=len(STYLE_PACK)))]
    for ref in STYLE_PACK:
        label = template["REFERENCE_LABEL"].format(ref_id=ref["id"], category_short=CATEGORY_SHORT[ref["category"]])
        content += [("text", label), ("image", ref_path(ref_set, ref).relative_to(ROOT).as_posix())]
    rules = template[f"CATEGORY_{target['category']}"]
    task = template["TASK"].format(subject=target["subject"], category=target["category"], category_rules=rules)
    content.append(("text", task))
    return content


def prepare(ref_set: str) -> None:
    leaked = {t["cell"] for t in TARGETS} & {r["cell"] for r in STYLE_PACK}
    if leaked:
        raise SystemExit(f"Hidden target(s) in the style pack: {sorted(leaked)}")
    cards = cards_dir(ref_set)
    if ref_set == "pdf_v0" and not (cards / "index.json").exists():
        refs_from_sheet.main([str(cards.parent / "source_sheet_p6.png"), str(cards)])
    missing = [c for c in [r["cell"] for r in STYLE_PACK] + [t["cell"] for t in TARGETS] if not (cards / f"{c}.png").exists()]
    if missing:
        raise SystemExit(f"Missing {ref_set} cards: {missing}")
    upscale = REF_SETS[ref_set]["upscale"]
    for folder in ("refs", "ground_truth", "prompts", "sheets"):
        (HERE / folder / ref_set).mkdir(parents=True, exist_ok=True)
    for ref in STYLE_PACK:
        card = Image.open(cards / f"{ref['cell']}.png").convert("RGB")
        card.resize((card.width * upscale, card.height * upscale), Image.LANCZOS).save(ref_path(ref_set, ref))
    for target in TARGETS:
        Image.open(cards / f"{target['cell']}.png").convert("RGB").save(truth_path(ref_set, target))
    template = load_template()
    for target in TARGETS:
        lines = [f"# Expanded request {target['id']}: {target['name']}, category {target['category']} ({ref_set})", ""]
        for kind, value in request_for(ref_set, target, template):
            lines += [f"[image: {value}]" if kind == "image" else value, ""]
        (HERE / "prompts" / ref_set / f"{target['id']}.md").write_text("\n".join(lines), encoding="utf-8")
    overview = [
        ("Style pack (sent)", [(f"{r['id']} {r['name']}", ref_path(ref_set, r)) for r in STYLE_PACK]),
        ("Hidden targets", [(f"{t['id']} {t['name']}", truth_path(ref_set, t)) for t in TARGETS]),
    ]
    build_sheet(overview, HERE / "sheets" / ref_set / "refs_overview.png", 200, f"BENCH-01 references ({ref_set})")
    print(f"Prepared {ref_set}: refs/, ground_truth/, prompts/ and sheets/{ref_set}/refs_overview.png")


def run(ref_set: str, arm_names: list[str]) -> None:
    unknown = [a for a in arm_names if a not in ARMS]
    if unknown:
        raise SystemExit(f"Unknown arm(s) {unknown}; choose from {list(ARMS)}")
    arm_names = arm_names or list(ARMS)
    estimate = sum(PRICE_PER_IMAGE_USD.get((ARMS[a]["model"], ARMS[a]["image_size"]), 0) for a in arm_names) * len(TARGETS)
    print(f"Up to {len(arm_names) * len(TARGETS)} images; estimated output cost ${estimate:.2f} plus input tokens")
    template = load_template()
    for folder in ("runs", "outputs"):
        (HERE / folder).mkdir(exist_ok=True)
    for arm_name in arm_names:
        arm = ARMS[arm_name]
        for target in TARGETS:
            stem = f"{ref_set}_{arm_name}_{target['id']}"
            if list((HERE / "outputs").glob(stem + ".*")):
                print(f"skip {stem}: output exists")
                continue
            content = request_for(ref_set, target, template)
            record = {
                "run": stem,
                "experiment": "BENCH-01",
                "reference_set": ref_set,
                "prompt_file": PROMPT_FILE.name,
                "target": target,
                **arm,
                "thinking_level": "model default",
                "content": [
                    {"text": value} if kind == "text" else {"image": value, "sha256": sha256(ROOT / value)}
                    for kind, value in content
                ],
                "sent_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            (HERE / "runs" / f"{stem}.request.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
            parts = [
                gemini_image.text_part(value) if kind == "text" else gemini_image.image_part((ROOT / value).read_bytes())
                for kind, value in content
            ]
            try:
                result = gemini_image.generate_image(
                    arm["model"], parts, aspect_ratio=arm["aspect_ratio"], image_size=arm["image_size"]
                )
            except gemini_image.GeminiError as err:
                (HERE / "runs" / f"{stem}.error.txt").write_text(str(err), encoding="utf-8")
                print(f"FAILED {stem}: {str(err)[:400]}")
                continue
            extension = ".jpg" if "jpeg" in result["mime_type"] else ".png"
            (HERE / "outputs" / f"{stem}{extension}").write_bytes(result.pop("image_bytes"))
            result["est_output_cost_usd"] = PRICE_PER_IMAGE_USD.get((arm["model"], arm["image_size"]))
            result["received_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            (HERE / "runs" / f"{stem}.response.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"ok {stem}: {result['elapsed_s']} s, {result['images_in_response']} image(s) via {result['image_source']}")


def sheets(ref_set: str) -> None:
    outputs = sorted(p.name for p in (HERE / "outputs").glob(f"{ref_set}_*_T*.*"))
    if not outputs:
        raise SystemExit(f"No {ref_set} outputs yet; run first.")
    key_file = HERE / f"blind_key_{ref_set}.json"
    key = json.loads(key_file.read_text(encoding="utf-8")) if key_file.exists() else {}
    if sorted(key.values()) != outputs:
        pool = [f"{letter}{digit}" for letter in "ABCDEFGHJKLMNPQRSTUVWXYZ" for digit in range(2, 10)]
        key = dict(zip(random.SystemRandom().sample(pool, len(outputs)), outputs))
        key_file.write_text(json.dumps(key, indent=2), encoding="utf-8")
        print(f"New blind key written ({key_file.name}): do not open it before scoring.")
    rows = []
    for target in TARGETS:
        items = [("real", truth_path(ref_set, target))]
        items += sorted((code, HERE / "outputs" / name) for code, name in key.items() if f"_{target['id']}." in name)
        rows.append((f"{target['id']} {target['name']} (C{target['category']})", items))
    build_sheet(rows, HERE / "sheets" / ref_set / "compare_card_size.png", 66, f"BENCH-01 {ref_set} at real card size (66 px tall)")
    build_sheet(rows, HERE / "sheets" / ref_set / "compare_large.png", 360, f"BENCH-01 {ref_set} enlarged")
    scores = HERE / f"scores_pavel_{ref_set}.csv"
    if not scores.exists():
        with scores.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["code", "target", "style_1to5", "category_1to5", "readability_1to5",
                             "clean_1to5", "scale_1to5", "players_would_notice_yes_no", "notes"])
            for code, name in sorted(key.items(), key=lambda item: (item[1].rsplit("_", 1)[1], item[0])):
                writer.writerow([code, name.rsplit("_", 1)[1].split(".")[0], "", "", "", "", "", "", ""])
    print(f"Sheets written to sheets/{ref_set}/; blind score template: {scores.name}")


def main(argv: list[str]) -> int:
    args = list(argv)
    ref_set = "miro_v1"
    if "--refs" in args:
        i = args.index("--refs")
        ref_set = args[i + 1] if i + 1 < len(args) else ""
        del args[i:i + 2]
    if ref_set not in REF_SETS:
        raise SystemExit(f"Unknown reference set {ref_set!r}; choose from {list(REF_SETS)}")
    command = args[0] if args else ""
    if command == "prepare":
        prepare(ref_set)
    elif command == "run":
        run(ref_set, args[1:])
    elif command == "sheets":
        sheets(ref_set)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
