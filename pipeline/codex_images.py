"""ChatGPT route: generate a plan's cards with the image tool of Codex (ChatGPT plan, no API credits).

    python -I pipeline/codex_images.py prepare sets/<slug>/plan.json A [B ...]   # prompt files + Codex task only
    python -I pipeline/codex_images.py run sets/<slug>/plan.json A [B ...]       # prepare, run `codex exec`, collect
    python -I pipeline/codex_images.py collect sets/<slug>/plan.json A [B ...]   # crop raw outputs, sheets, set check
    (card ids such as A04 work in place of variant ids, for single cards)

Each card gets the same card text as the Gemini route (the TASK section of cardgen's prompt file), with
4 reference images: the 3 production references of its category and a sheet of all 12. Codex's image tool
(image_gen.imagegen) takes at most 5 paths and has returned portrait images (BENCH-03), so the text asks
for a square composition that survives the crop to the card shape.

Everything goes to sets/<slug>/gpt/: prompts/, raw/ (as generated), final/ (430x480), sheets/, codex_log_<ids>.md.
First test (W018, LC-B04): Codex accepted all 4 references and returned a square 1254x1254 image in about 30 s.
One attempt per card, plus one retry on a tool error. This route has no automatic QA loop; the pixel
colour check and the set check run on the results.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from PIL import Image  # noqa: E402

import cardgen  # noqa: E402
import colour_check  # noqa: E402
from sheets import build_sheet, extend_to_card, to_card  # noqa: E402

REF_SHEET = ROOT / "references" / "production_refs_sheet.png"
GPT_INTRO = ("You will create one illustration for a collectible card in a casual mobile game. The attached reference "
             "images are existing cards from this game: images 1-3 are cards in the same composition category as the "
             "new card, and image 4 is a sheet of 12 cards (one row per category: 1 floating object, 2 plain surface, "
             "3 realistic surface, 4 environment). Use them only to learn the art style; never copy their objects.")
SQUARE = ("Composition for the card format: make the image square (1:1). If it has to be taller than wide, keep the "
          "whole object and its margins inside the central square area, because the card is cropped to a near-square shape.")


def ref_sheet() -> Path:
    if not REF_SHEET.exists():
        refs = cardgen.Refs().refs
        rows = [(f"category {k}", [(f"{r['id']} {r['name']}", cardgen.CARDS_DIR / f"{r['cell']}.png")
                                   for r in refs if r["category"] == k]) for k in (1, 2, 3, 4)]
        build_sheet(rows, REF_SHEET, 300, "Reference cards from the game, one row per composition category")
    return REF_SHEET


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def run_tag(ids: list[str]) -> str:
    """Short name for one run's task, log and output files."""
    return ''.join(ids) if len(ids) <= 3 else f"{len(ids)}cards_{ids[0]}"


def cards_of(plan: dict, ids: list[str]) -> list[dict]:
    """Cards of the given variants (A, B ...) or single cards (A04 ...)."""
    return [c for v in plan["variants"] for c in v["cards"] if v["id"] in ids or c["id"] in ids]


def prepare(plan_path: Path, variant_ids: list[str], route_dir: str = "gpt", fixes: dict | None = None) -> Path:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    gpt = plan_path.parent / route_dir
    for sub in ("prompts", "raw", "final"):
        (gpt / sub).mkdir(parents=True, exist_ok=True)
    template, refs, sheet = cardgen.load_sections(cardgen.PROMPT_FILE), cardgen.Refs(), ref_sheet()
    cards = cards_of(plan, variant_ids)
    for card in cards:
        note = (fixes or {}).get(card["id"], "")
        task = template["TASK"].format(
            name=card["name"], subject=card["subject"], unique_detail=card["unique_detail"],
            main_colors=card["main_colors"], background=card["background"],
            context_cue=card.get("context_cue") or "none", category=card["category"],
            category_rules=template[f"CATEGORY_{card['category']}"],
            fix=f"- Art direction for this card: {note}" if note else "").rstrip()
        paths = [cardgen.CARDS_DIR / f"{r['cell']}.png" for r in refs.of_category(card["category"])] + [sheet]
        lines = [f"# {card['id']} {card['name']} (prompt file {cardgen.PROMPT_FILE.name}, ChatGPT route)", "",
                 "Reference images, attach in this order:", *[f"{i}. {rel(p)}" for i, p in enumerate(paths, 1)], "",
                 "Prompt:", GPT_INTRO, "", task, "", SQUARE]
        (gpt / "prompts" / f"{card['id']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    listing = "\n".join(f"- {c['id']}: {rel(gpt / 'prompts' / (c['id'] + '.md'))} -> {rel(gpt / 'raw' / (c['id'] + '.png'))}"
                        for c in cards)
    task_text = f"""You are generating card illustrations with your built-in image generation tool. Work only inside {rel(gpt)}/. Do not edit, move or delete any other file, and do not change the prompt files.

For each card below, in this order:
1. Read the prompt file. Use the text after the line "Prompt:" exactly as written, with no additions or rewording.
2. Call the image tool once with that prompt and with the reference image paths listed in the file, in that order (4 paths). If the tool lets you choose a size or aspect ratio, choose square (1:1).
3. Copy the generated image, unchanged, to the raw path given below. Never crop, resize, retouch or edit an image.
4. Make one attempt per card. Do not regenerate because of how an image looks. If the tool returns an error, retry once and record it.

Cards (prompt file -> output path):
{listing}

When all cards are done, write {rel(gpt / ('codex_log_' + run_tag(variant_ids) + '.md'))} with one entry per card: card id, image tool name, model name or version if the tool reports it (otherwise "not exposed"), output size in pixels, the original generated file path, retries and errors, start and end time. Do not include any credentials or tokens.
"""
    task_path = gpt / f"codex_task_{run_tag(variant_ids)}.md"
    task_path.write_text(task_text, encoding="utf-8")
    print(f"{len(cards)} prompt(s) and {rel(task_path)} written")
    return task_path


def collect(plan_path: Path, variant_ids: list[str], route_dir: str = "gpt", fit: str = "extend") -> None:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    gpt = plan_path.parent / route_dir
    shape = extend_to_card if fit == "extend" else to_card  # W019: extend keeps ChatGPT's side margins
    lines = [f"# {plan['set']}: ChatGPT route results ({route_dir}/)", "",
             "| card | name | raw size | background check |", "|---|---|---|---|"]
    for card in cards_of(plan, [v["id"] for v in plan["variants"]]):  # the summary always covers every card present
        raw = gpt / "raw" / f"{card['id']}.png"
        if not raw.exists():
            continue
        image = Image.open(raw).convert("RGB")
        final = shape(image, 480)
        if card in cards_of(plan, variant_ids) or not (gpt / "final" / f"{card['id']}.png").exists():
            final.save(gpt / "final" / f"{card['id']}.png")
        check = colour_check.check(final, card)
        lines.append(f"| {card['id']} | {card['name']} | {image.width}x{image.height} | "
                     f"{check['level'] + ': ' + check['why'] if check else 'category 4, not checked'} |")
    (gpt / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    touched = {v["id"] for v in plan["variants"] for c in v["cards"] if v["id"] in variant_ids or c["id"] in variant_ids}
    for variant in plan["variants"]:
        if variant["id"] not in touched:
            continue
        items = [(f"{c['id']} {c['name']} C{c['category']} {'*' * c.get('stars', 0)}".rstrip(), gpt / "final" / f"{c['id']}.png")
                 for c in variant["cards"] if (gpt / "final" / f"{c['id']}.png").exists()]
        if items:
            build_sheet([(f"{variant['id']} 1-5", items[:5]), (f"{variant['id']} 6-10", items[5:])],
                        gpt / "sheets" / f"variant_{variant['id']}.png", 240,
                        f"{plan['set']}: variant {variant['id']} (ChatGPT route), {variant.get('concept', '')}")
    print("\n".join(lines))
    print(cardgen.setcheck(plan_path, f"{route_dir}/final"))


def run(plan_path: Path, variant_ids: list[str], route_dir: str = "gpt", fixes: dict | None = None) -> None:
    task_path = prepare(plan_path, variant_ids, route_dir, fixes)
    gpt = plan_path.parent / route_dir
    cmd = ["codex", "exec", "--skip-git-repo-check", "-C", str(ROOT), "-s", "workspace-write",
           "-o", str(gpt / f"codex_last_message_{run_tag(variant_ids)}.md"), "-"]
    print("Running:", " ".join(cmd[:-1]), "< task", flush=True)
    result = subprocess.run(cmd, input=task_path.read_text(encoding="utf-8"), text=True, encoding="utf-8",
                            capture_output=True, timeout=3600)
    (gpt / f"codex_output_{run_tag(variant_ids)}.txt").write_text(result.stdout[-20000:] + "\n--- stderr ---\n" + result.stderr[-20000:],
                                                                  encoding="utf-8")
    print(f"codex exit code {result.returncode}", flush=True)
    collect(plan_path, variant_ids, route_dir)


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(errors="replace")  # never crash on a non-ASCII character in a cp1251 console
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["prepare", "run", "collect"])
    parser.add_argument("plan", type=Path)
    parser.add_argument("ids", nargs="+", help="variant ids (A) or card ids (A04)")
    parser.add_argument("--route-dir", default="gpt", help="output folder next to the plan, e.g. gpt_v7 to keep earlier runs")
    parser.add_argument("--fixes", type=Path, help="JSON {card id: correction note}, e.g. from card_metrics.py fixes")
    parser.add_argument("--fit", choices=["extend", "crop"], default="extend",
                        help="square to card shape: extend the background above and below (default) or cut the sides")
    args = parser.parse_args(argv)
    fixes = json.loads(args.fixes.read_text(encoding="utf-8")) if args.fixes else None
    if args.command == "prepare":
        prepare(args.plan, args.ids, args.route_dir, fixes)
    elif args.command == "run":
        run(args.plan, args.ids, args.route_dir, fixes)
    else:
        collect(args.plan, args.ids, args.route_dir, args.fit)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
