"""Measure cards the way an art lead looks at them: object size and breathing room, composition category,
detail that disappears at card size, and highlight strength. Compares our cards with reference norms.

    python -I pipeline/card_metrics.py refs                                # all 160 reference cards -> analysis/
    python -I pipeline/card_metrics.py plan sets/<slug>/plan.json [--final-dir gpt/final] [--variants A,B]
    python -I pipeline/card_metrics.py report sets/<slug>/plan.json [--final-dir gpt/final] [--variants A,B]
    python -I pipeline/card_metrics.py fixes sets/<slug>/plan.json [--final-dir ...] [--out fixes.json]  # notes for flagged cards

A vision call (the QA model) returns the main object's box and the composition category, with the
categories as the brief defines them, plus 5 for character cards. Pixels give the rest, measured on the
430x480 card as players see it:
- height and width: the object's box as a share of the card;
- margin: the smallest gap between the box and an edge;
- detail lost: edge energy inside the box at card resolution, minus what survives a 66 px view;
- highlight: share of near-white, low-saturation pixels inside the box (specular shine).
Results are cached per image (by file size and modification time) in metrics.json next to the images' folder.
"""

from __future__ import annotations

import argparse
import colorsys
import concurrent.futures
import io
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from PIL import Image, ImageFilter  # noqa: E402

import costs  # noqa: E402
import gemini_image  # noqa: E402
from sheets import to_card  # noqa: E402

MODEL = "gemini-3.8-flash"
CARDS = ROOT / "references" / "miro_v1" / "cards"
REF_OUT = ROOT / "analysis" / "card_metrics_refs.json"
PROMPT = """This is a collectible-card illustration from a casual mobile game.
1. Find the main subject: the single object the card shows. For a scene card, take the main structure or vehicle, not the ground, sky or scenery; for a character card, take the character or characters. Give its bounding box as box_2d [ymin, xmin, ymax, xmax], normalised to 0-1000.
2. Classify the composition by the game's rules:
   1 = the object floats in the air, with no surface under it, on a single-colour, gradient or simple-pattern background;
   2 = the object stands on a plain, flat, single-colour surface in front of a simple background;
   3 = the object stands on a realistic surface (a wooden table, a floor, a podium) in front of a simple wall;
   4 = the object is set into a realistic surrounding environment (landscape, street, water) and stays central;
   5 = one or two characters (people or animals) acting out a little scene.
3. Say how much small detail on the subject would be lost when the card is shown about 66 pixels tall: low, medium or high.
Answer with JSON only: {"box_2d": [0, 0, 0, 0], "category": 1, "category_confidence": "high", "small_detail": "low", "why": "one short sentence"}"""


def flat(image: Image.Image):
    return image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()


def pixel_metrics(card: Image.Image, box: list[int]) -> dict:
    w, h = card.size
    y0, x0, y1, x1 = box
    bx = (max(0, round(x0 / 1000 * w)), max(0, round(y0 / 1000 * h)), min(w, round(x1 / 1000 * w)), min(h, round(y1 / 1000 * h)))
    if bx[2] - bx[0] < 4 or bx[3] - bx[1] < 4:
        return {}
    gray = card.convert("L")
    small = gray.resize((round(66 * w / h), 66), Image.LANCZOS).resize((w, h), Image.BILINEAR)
    edges_full = gray.filter(ImageFilter.FIND_EDGES).crop(bx)
    edges_small = small.filter(ImageFilter.FIND_EDGES).crop(bx)
    e_full = statistics.fmean(flat(edges_full))
    e_small = statistics.fmean(flat(edges_small))
    rgb = card.crop(bx).convert("RGB")
    shine = sat = 0
    pixels = list(flat(rgb))
    for r, g, b in pixels:
        _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        shine += v > 0.93 and s < 0.18
        sat += s
    return {"detail_lost": round(e_full - e_small, 2), "edge_full": round(e_full, 2),
            "highlight": round(shine / len(pixels), 4), "saturation": round(sat / len(pixels), 3)}


def measure(path: Path, log_dir: Path | None = None, name: str = "") -> dict:
    card = to_card(Image.open(path).convert("RGB"), 480)
    buffer = io.BytesIO()
    card.save(buffer, "PNG")
    result = gemini_image.generate_text(MODEL, [gemini_image.text_part(PROMPT), gemini_image.image_part(buffer.getvalue())])
    costs.log(log_dir, "vision", name, costs.text_cost(result["response"].get("usage", {})))
    raw = result["text"]
    answer = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    y0, x0, y1, x1 = [max(0, min(1000, int(v))) for v in answer["box_2d"]]
    row = {"category_seen": int(answer.get("category", 0)), "category_confidence": answer.get("category_confidence", ""),
           "small_detail": answer.get("small_detail", ""), "why": answer.get("why", ""), "box": [y0, x0, y1, x1],
           "height": round((y1 - y0) / 1000, 3), "width": round((x1 - x0) / 1000, 3),
           "margin": round(min(y0, x0, 1000 - y1, 1000 - x1) / 1000, 3),
           "margin_top": round(y0 / 1000, 3), "margin_bottom": round((1000 - y1) / 1000, 3)}
    row.update(pixel_metrics(card, [y0, x0, y1, x1]))
    return row


def measure_all(items: dict[str, Path], cache_path: Path, log_dir: Path | None = None) -> bool:
    """Measure the new or changed images; True if every one of them was measured."""
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    def key(p: Path) -> str:
        st = p.stat()
        return f"{st.st_size}:{int(st.st_mtime)}"
    todo = {name: p for name, p in items.items() if cache.get(name, {}).get("_key") != key(p)}
    done, failed, billing = 0, [], False
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(measure, p, log_dir, name): name for name, p in todo.items()}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            if future.cancelled():  # stopped after an empty-balance answer; counted below
                continue
            try:
                cache[name] = {**future.result(), "_key": key(todo[name])}
                done += 1
            except gemini_image.BillingError:
                billing = True
                failed.append(name)
                for other in futures:
                    other.cancel()
            except Exception as err:  # one bad answer must not stop the batch
                failed.append(name)
                print(f"{name}: failed ({str(err)[:120]})", flush=True)
    failed = sorted(set(failed) | {name for f, name in futures.items() if f.cancelled()})
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")
    # W023: count what was measured, not what was attempted; stale numbers must not pass as new ones
    print(f"{done} measured, {len(items) - len(todo)} unchanged, {len(failed)} not measured -> {cache_path}")
    if failed:
        print(f"not measured: {', '.join(failed)}; the report would show their old numbers, so run the same "
              "command again before reporting")
    if billing:
        print(gemini_image.BILLING_HELP)
    return not failed


def plan_items(plan_path: Path, final_dir: str, variants: str | None) -> tuple[dict, dict[str, Path], Path]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    wanted = set(variants.split(",")) if variants else None
    cards = {c["id"]: c for v in plan["variants"] if not wanted or v["id"] in wanted for c in v["cards"]}
    folder = plan_path.parent / final_dir
    items = {cid: folder / f"{cid}.png" for cid in cards if (folder / f"{cid}.png").exists()}
    return cards, items, folder.parent / f"metrics_{folder.name}.json"  # one cache per image folder


METRICS = ("extent", "margin", "margin_top", "detail_lost", "highlight")


def value(row: dict, metric: str) -> float | None:
    if metric == "extent":  # the object's largest dimension, so tall and wide shapes compare fairly
        return max(row["height"], row["width"])
    return row.get(metric)


def norms(refs: dict) -> dict[int, dict]:
    """Per category (1-4, as the vision call sees the reference cards): quartiles of each metric."""
    out = {}
    for cat in (1, 2, 3, 4):
        rows = [r for r in refs.values() if r.get("category_seen") == cat]
        if len(rows) < 4:
            continue
        out[cat] = {"n": len(rows)}
        for m in METRICS:
            values = sorted(v for r in rows if (v := value(r, m)) is not None)
            q = statistics.quantiles(values, n=4)
            out[cat][m] = {"q1": round(q[0], 3), "median": round(q[1], 3), "q3": round(q[2], 3)}
    return out


def card_flags(row: dict, planned_category: int, ref: dict) -> list[str]:
    """Flags against the reference middle half of the card's category, widened by a quarter of its range."""
    flags = []
    if row["category_seen"] != planned_category:
        flags.append(f"reads as C{row['category_seen']} ({row['category_confidence']})")
    checks = (("extent", "small", "too big"), ("margin", "tight margins", ""), ("margin_top", "little room above", "much room above"),
              ("detail_lost", "", "fine detail lost"))
    for m, low, high in checks:
        if m not in ref or value(row, m) is None:
            continue
        q1, q3 = ref[m]["q1"], ref[m]["q3"]
        pad = (q3 - q1) * 0.25
        v = value(row, m)
        if low and v < q1 - pad:
            flags.append(low)
        elif high and v > q3 + pad:
            flags.append(high)
    return flags


def report(plan_path: Path, final_dir: str, variants: str | None) -> str:
    refs = json.loads(REF_OUT.read_text(encoding="utf-8"))
    n = norms(refs)
    cards, items, cache_path = plan_items(plan_path, final_dir, variants)
    ours = json.loads(cache_path.read_text(encoding="utf-8"))
    lines = [f"# Card metrics: {plan_path.parent.name} ({final_dir})", "",
             "Reference norms by category, as the vision call classifies the 160 reference cards: median (middle half). "
             "Extent = the object's largest dimension as a share of the card.", "",
             "| Category | Cards | Extent | Smallest margin | Room above | Detail lost at 66 px | Highlight share |",
             "|---|---|---|---|---|---|---|"]
    for cat, v in n.items():
        f = lambda m: f"{v[m]['median']:.2f} ({v[m]['q1']:.2f}-{v[m]['q3']:.2f})"
        lines.append(f"| C{cat} | {v['n']} | {f('extent')} | {f('margin')} | {f('margin_top')} | {f('detail_lost')} | {f('highlight')} |")
    lines += ["", "Our cards. A flag means the value is outside the reference middle half by more than a quarter of that range, "
              "or the vision call reads a different category than the plan. Highlight is shown for information only: white "
              "objects count as shine.", "",
              "| Card | Name | Planned C | Seen C | Extent | Margin | Room above | Detail lost | Highlight | Flags |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    flagged, extents = 0, []
    for cid, card in cards.items():
        r = ours.get(cid)
        if not r:
            continue
        flags = card_flags(r, card["category"], n.get(card["category"], {}))
        flagged += bool(flags)
        extents.append(value(r, "extent"))
        lines.append(f"| {cid} | {card['name']} | C{card['category']} | C{r['category_seen']} | {value(r, 'extent'):.2f} | "
                     f"{r['margin']:.2f} | {r['margin_top']:.2f} | {r.get('detail_lost', 0):.1f} | {r.get('highlight', 0):.3f} | "
                     f"{', '.join(flags) or '-'} |")
    if len(extents) >= 4:
        q = statistics.quantiles(extents, n=4)
        lines += ["", f"Extent across these cards: median {q[1]:.2f}, middle half {q[0]:.2f}-{q[2]:.2f} (a narrower spread = more even sizes)."]
    lines += ["", f"{flagged} of {len(items)} cards flagged."]
    text = "\n".join(lines) + "\n"
    cache_path.with_suffix(".md").write_text(text, encoding="utf-8")
    return text


FRAMING_FLAGS = {"too big", "small", "tight margins", "little room above", "much room above"}
CATEGORY_FIX = {1: "make it float in the air with no surface under it, on a simple single-colour background",
                2: "stand it on a plain, flat, single-colour surface in front of a simple background",
                3: "stand it on a clearly realistic surface (a polished wooden tabletop or a glossy floor) in front of a plain wall",
                4: "set it into its realistic surrounding environment, still central"}


def make_fixes(plan_path: Path, final_dir: str, variants: str | None) -> dict[str, str]:
    """One correction note per flagged card, with measured numbers and the reference target."""
    n = norms(json.loads(REF_OUT.read_text(encoding="utf-8")))
    cards, items, cache_path = plan_items(plan_path, final_dir, variants)
    ours = json.loads(cache_path.read_text(encoding="utf-8"))
    log_path = (plan_path.parent / final_dir).parent / "reframe_log.json"
    framed = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else {}
    fixes = {}
    for cid, card in cards.items():
        r = ours.get(cid)
        if not r:
            continue
        ref = n.get(card["category"], {})
        notes = []
        for flag in card_flags(r, card["category"], ref):
            if cid in framed and flag in FRAMING_FLAGS:  # W023: reframe.py sets size and room; a redraw can't change them
                continue
            if flag.startswith("reads as"):
                notes.append(f"It reads as a different card category; {CATEGORY_FIX[card['category']]}.")
            elif flag == "too big":
                notes.append(f"The object spans {value(r, 'extent'):.0%} of the card; make it smaller, about {ref['extent']['median']:.0%}, "
                             "with clear empty space on every side.")
            elif flag == "small":
                notes.append(f"The object spans only {value(r, 'extent'):.0%} of the card; make it bigger, about {ref['extent']['median']:.0%}, "
                             "while keeping clear space around it.")
            elif flag == "tight margins":
                notes.append(f"The object comes within {r['margin']:.0%} of an edge; keep at least 5% clear on every side, "
                             "inside the central 90% of the width.")
            elif flag == "little room above":
                notes.append(f"Only {r['margin_top']:.0%} of the height is clear above the object; leave about 14% clear above it.")
            elif flag == "much room above":
                notes.append(f"{r['margin_top']:.0%} of the height is empty above the object; move it up to the vertical middle, "
                             "with about 14% clear above it.")
            elif flag == "fine detail lost":
                notes.append("Simplify it: fewer, larger shapes, and none of the small details that can't be read at card size.")
        if notes:
            fixes[cid] = " ".join(notes)
    return fixes


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["refs", "plan", "report", "fixes"])
    parser.add_argument("--out", type=Path, help="fixes: where to write the JSON of correction notes")
    parser.add_argument("plan", nargs="?", type=Path)
    parser.add_argument("--final-dir", default="final")
    parser.add_argument("--variants")
    args = parser.parse_args(argv)
    if args.command == "refs":
        measure_all({p.stem: p for p in sorted(CARDS.glob("r*c*.png"))}, REF_OUT)
    elif args.command == "plan":
        _, items, cache_path = plan_items(args.plan, args.final_dir, args.variants)
        complete = measure_all(items, cache_path, args.plan.parent)
        if (args.plan.parent / "summary.json").exists():  # W030: keep summary.md's cost line current
            import cardgen
            cardgen.write_summary(json.loads(args.plan.read_text(encoding="utf-8")), args.plan.parent)
        if not complete:
            return 2
    elif args.command == "fixes":
        fixes = make_fixes(args.plan, args.final_dir, args.variants)
        out = args.out or (args.plan.parent / args.final_dir).parent / "fixes.json"
        out.write_text(json.dumps(fixes, indent=1), encoding="utf-8")
        print(f"{len(fixes)} correction note(s) -> {out}")
    else:
        print(report(args.plan, args.final_dir, args.variants))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
