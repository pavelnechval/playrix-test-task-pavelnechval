"""BENCH-03: prompt v3, Nano Banana 2.1 vs GPT Image 2.5, two samples per hidden target, blind sheets.

    python -I experiments/BENCH-03/bench.py prepare        # copy refs, write expanded prompts (no API calls)
    python -I experiments/BENCH-03/bench.py run [ARM ...]  # paid API calls; arms: nb21, gpt25s, gpt2
    python -I experiments/BENCH-03/bench.py sheets         # blind sheets + score template

Same hidden targets, subject text and 12-card reference pack as BENCH-02. Gemini
gets the prompt with each reference labelled in place. The OpenAI Images API
takes one prompt plus an image list, so its prompt carries the same labels as a
numbered list ("Image 1: ..."). The content is otherwise identical.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import gemini_image  # noqa: E402
import openai_image  # noqa: E402
from sheets import build_sheet  # noqa: E402

PROMPT_FILE = HERE / "prompt_v3.md"
BENCH01 = ROOT / "experiments" / "BENCH-01"
BENCH02 = ROOT / "experiments" / "BENCH-02"
SAMPLES = ("a", "b")
ARMS = {
    "nb21": {"provider": "gemini", "model": "gemini-nano-banana-2.1", "aspect_ratio": "1:1", "image_size": "1K"},
    "gpt25s": {"provider": "openai", "model": "gpt-image-2.5-sunburst", "size": "1024x1136", "quality": "high"},
    "gpt2": {"provider": "openai", "model": "gpt-image-2", "size": "1024x1024", "quality": "high"},  # fallback
}
# USD per 1M tokens, as read on 2026-10-13. Gemini: official pricing page. OpenAI: gpt-image-2 rates
# from third-party listings (2.5 reportedly the same); verify on OpenAI's pricing page.
PRICES = {
    "gemini-nano-banana-2.1": {"input": 1.50, "image_out_1k": 0.0336},
    "openai": {"text_in": 5.0, "image_in": 8.0, "image_out": 30.0},
}

TARGETS = [  # identical to BENCH-01/02; never sent to a model
    {"id": "T1", "name": "Bottle", "category": 1, "cell": "r05c07", "subject": "a sports water bottle"},
    {"id": "T2", "name": "Tea Cup", "category": 2, "cell": "r07c06", "subject": "a tea cup"},
    {"id": "T3", "name": "Bumpers", "category": 3, "cell": "r06c02", "subject": "a bumper car (a fairground dodgem)"},
    {"id": "T4", "name": "Lighthouse", "category": 4, "cell": "r14c08", "subject": "a lighthouse"},
]
STYLE_PACK = [  # same 12 Miro originals as BENCH-02
    {"id": "R1", "category": 1, "cell": "r02c07"}, {"id": "R2", "category": 1, "cell": "r02c09"},
    {"id": "R3", "category": 1, "cell": "r05c01"}, {"id": "R4", "category": 2, "cell": "r02c04"},
    {"id": "R5", "category": 2, "cell": "r03c07"}, {"id": "R6", "category": 2, "cell": "r05c04"},
    {"id": "R7", "category": 3, "cell": "r01c06"}, {"id": "R8", "category": 3, "cell": "r05c10"},
    {"id": "R9", "category": 3, "cell": "r02c02"}, {"id": "R10", "category": 4, "cell": "r05c03"},
    {"id": "R11", "category": 4, "cell": "r06c09"}, {"id": "R12", "category": 4, "cell": "r06c01"},
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


def task_text(target: dict, template: dict[str, str]) -> str:
    rules = template[f"CATEGORY_{target['category']}"]
    return template["TASK"].format(subject=target["subject"], category=target["category"], category_rules=rules)


def label(ref: dict, template: dict[str, str]) -> str:
    return template["REFERENCE_LABEL"].format(ref_id=ref["id"], category_short=CATEGORY_SHORT[ref["category"]])


def gemini_request(target: dict, template: dict[str, str]) -> list[tuple[str, str]]:
    content = [("text", template["INTRO"].format(n_refs=len(STYLE_PACK)))]
    for ref in STYLE_PACK:
        content += [("text", label(ref, template)), ("image", ref_path(ref).relative_to(ROOT).as_posix())]
    return content + [("text", task_text(target, template))]


def openai_prompt(target: dict, template: dict[str, str]) -> str:
    intro = template["INTRO"].format(n_refs=len(STYLE_PACK)).replace("The next", "The attached")
    listing = "\n".join(f"Image {i}: {label(ref, template)[:-1]}." for i, ref in enumerate(STYLE_PACK, 1))
    return f"{intro}\n\n{listing}\n\n{task_text(target, template)}"


def prepare() -> None:
    (HERE / "refs").mkdir(exist_ok=True)
    for ref in STYLE_PACK:
        shutil.copyfile(BENCH02 / "refs" / ref_path(ref).name, ref_path(ref))
    template = load_template()
    for provider in ("gemini", "openai"):
        (HERE / "prompts" / provider).mkdir(parents=True, exist_ok=True)
    for target in TARGETS:
        lines = [f"# Gemini request {target['id']}: {target['name']}, category {target['category']}", ""]
        for kind, value in gemini_request(target, template):
            lines += [f"[image: {value}]" if kind == "image" else value, ""]
        (HERE / "prompts" / "gemini" / f"{target['id']}.md").write_text("\n".join(lines), encoding="utf-8")
        images = "\n".join(f"- {ref_path(r).relative_to(ROOT).as_posix()}" for r in STYLE_PACK)
        text = f"# OpenAI request {target['id']}\n\nImages, in order:\n{images}\n\nPrompt:\n\n{openai_prompt(target, template)}\n"
        (HERE / "prompts" / "openai" / f"{target['id']}.md").write_text(text, encoding="utf-8")
    print("Prepared refs/ and prompts/gemini, prompts/openai")


def estimate_cost(arm: dict, usage: dict) -> float | None:
    if arm["provider"] == "gemini":
        price = PRICES[arm["model"]]
        return usage.get("total_input_tokens", 0) * price["input"] / 1e6 + price["image_out_1k"]
    details = usage.get("input_tokens_details") or {}
    if not usage:
        return None
    price = PRICES["openai"]
    return (details.get("text_tokens", 0) * price["text_in"] + details.get("image_tokens", 0) * price["image_in"]
            + usage.get("output_tokens", 0) * price["image_out"]) / 1e6


def run(arm_names: list[str]) -> None:
    unknown = [a for a in arm_names if a not in ARMS]
    if unknown or not arm_names:
        raise SystemExit(f"Choose arms from {list(ARMS)}")
    template = load_template()
    for folder in ("runs", "outputs"):
        (HERE / folder).mkdir(exist_ok=True)
    for arm_name in arm_names:
        arm = ARMS[arm_name]
        for target in TARGETS:
            for sample in SAMPLES:
                stem = f"{arm_name}_{target['id']}{sample}"
                if list((HERE / "outputs").glob(stem + ".*")):
                    print(f"skip {stem}: output exists")
                    continue
                record = {"run": stem, "experiment": "BENCH-03", "prompt_file": PROMPT_FILE.name, "target": target,
                          "sample": sample, **arm, "sent_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
                try:
                    if arm["provider"] == "gemini":
                        content = gemini_request(target, template)
                        record["content"] = [{"text": v} if k == "text" else
                                             {"image": v, "sha256": hashlib.sha256((ROOT / v).read_bytes()).hexdigest()}
                                             for k, v in content]
                        (HERE / "runs" / f"{stem}.request.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
                        parts = [gemini_image.text_part(v) if k == "text" else gemini_image.image_part((ROOT / v).read_bytes())
                                 for k, v in content]
                        result = gemini_image.generate_image(arm["model"], parts, aspect_ratio=arm["aspect_ratio"],
                                                             image_size=arm["image_size"])
                        usage = result["response"].get("usage", {})
                    else:
                        prompt = openai_prompt(target, template)
                        record["prompt"] = prompt
                        record["images"] = [ref_path(r).relative_to(ROOT).as_posix() for r in STYLE_PACK]
                        (HERE / "runs" / f"{stem}.request.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
                        result = openai_image.edit_image(arm["model"], prompt, [ref_path(r) for r in STYLE_PACK],
                                                         size=arm["size"], quality=arm["quality"])
                        usage = result["response"].get("usage", {})
                except (gemini_image.GeminiError, openai_image.OpenAIError) as err:
                    (HERE / "runs" / f"{stem}.error.txt").write_text(str(err), encoding="utf-8")
                    print(f"FAILED {stem}: {str(err)[:400]}")
                    continue
                extension = ".jpg" if "jpeg" in result["mime_type"] else ".png"
                (HERE / "outputs" / f"{stem}{extension}").write_bytes(result.pop("image_bytes"))
                result["est_cost_usd"] = estimate_cost(arm, usage)
                result["received_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                (HERE / "runs" / f"{stem}.response.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
                cost = f"${result['est_cost_usd']:.3f}" if result["est_cost_usd"] is not None else "cost n/a"
                print(f"ok {stem}: {result['elapsed_s']} s, {cost}")


def sheets() -> None:
    outputs = sorted(p.name for p in (HERE / "outputs").glob("*_T*.*"))
    if not outputs:
        raise SystemExit("No outputs yet; run first.")
    key_file = HERE / "blind_key.json"
    key = json.loads(key_file.read_text(encoding="utf-8")) if key_file.exists() else {}
    if sorted(key.values()) != outputs:
        pool = [f"{letter}{digit}" for letter in "ABCDEFGHJKLMNPQRSTUVWXYZ" for digit in range(2, 10)]
        key = dict(zip(random.SystemRandom().sample(pool, len(outputs)), outputs))
        key_file.write_text(json.dumps(key, indent=2), encoding="utf-8")
        print("New blind key written (blind_key.json): do not open it before scoring.")
    rows = []
    for target in TARGETS:
        items = [("real", truth_path(target))]
        items += sorted((code, HERE / "outputs" / name) for code, name in key.items() if f"_{target['id']}" in name)
        rows.append((f"{target['id']} {target['name']} (C{target['category']})", items))
    (HERE / "sheets").mkdir(exist_ok=True)
    build_sheet(rows, HERE / "sheets" / "compare_card_size.png", 66, "BENCH-03 at real card size (66 px tall), blind")
    build_sheet(rows, HERE / "sheets" / "compare_large.png", 300, "BENCH-03 enlarged, blind")
    scores = HERE / "scores_pavel.csv"
    if not scores.exists():
        with scores.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["code", "target", "style_1to5", "players_would_notice_yes_no", "notes"])
            for code, name in sorted(key.items(), key=lambda item: (item[1].split("_")[1][:2], item[0])):
                writer.writerow([code, name.split("_")[1][:2], "", "", ""])
    print("Sheets written to sheets/; blind score template: scores_pavel.csv")


def main(argv: list[str]) -> int:
    command = argv[0] if argv else ""
    if command == "prepare":
        prepare()
    elif command == "run":
        run(argv[1:])
    elif command == "sheets":
        sheets()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
