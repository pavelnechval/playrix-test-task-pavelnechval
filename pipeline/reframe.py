"""Auto-framing: give every card the reference cards' object size and breathing room, whatever the model drew.

    python -I pipeline/reframe.py sets/<slug>/plan.json --route gpt_v7 [--ids A,B or A01,A02]   # ChatGPT route
    python -I pipeline/reframe.py sets/<slug>/plan.json --route gemini [--ids B]                 # Gemini route
    ... --fill stretch      # no image-model calls
    ... --recompose         # rebuild the outpainted canvases from the saved model images (no calls)
    ... --override A06 --box 120,80,900,920 --why "the subject includes the trees"   # see "Review overrides"
    ... --override A06 --fill stretch --why "..."  |  --clear-override A06

For each card, a vision call finds the main object's box on the full generated image (cached in
<route folder>/boxes_raw.json). The script then picks the card-shaped window (9:10) that puts the object at
the reference median size for its category (largest dimension: C1 0.82, C2 0.85, C3 0.89, C4 0.85; medians
of the 160 reference cards, card_metrics.py), with at least 5% clear on the sides and about 14% clear above.
The window may run past the picture by up to 12% per side. There the background is extended:

- outpaint (default): the image model (nano banana) continues the picture outward in the same style. Its
  colours are matched to the original at the seam, and the original pixels are kept and blended in over a
  2% seam. A seam check rejects a result whose copy of the picture moved; after one retry the card falls
  back to stretching. Every attempt is kept in <route folder>/outpaint/ (about $0.035 per call).
- stretch: the outermost rows or columns are stretched and blurred, never on a side the object touches.
  This suits plain backdrops; on scenery and patterned backdrops it leaves streaks (W022).

Review overrides, written with --override into sets/<slug>/framing.json: a hand-set box (y0,x0,y1,x1 on a
0-1000 scale of the generated image) for a scene whose subject is more than the vision box, or the fill to use
where the seam check and the eye disagree (stretch, or a saved attempt such as A06.try2.model.png). Each one
records why. It applies to that exact image and is ignored once the card is regenerated.

The result replaces <route>/final/<id>.png; the image from before the first reframing is kept as
<route>/final_prev/<id>.png. The variant sheets are rebuilt at the end. A card whose box can't be measured is
left as it was. If the Gemini balance runs out (HTTP 402), the script frames what it can, says so and exits 2.

W019: the reframing standardises size and breathing room deterministically. Prompts alone did not: ChatGPT
ignored numeric framing, and our fixed crop had pushed wide objects into the edges.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import io
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat  # noqa: E402

import cardgen  # noqa: E402
import costs  # noqa: E402
import gemini_image  # noqa: E402
from card_metrics import MODEL, PROMPT  # noqa: E402
from sheets import CARD_ASPECT, build_sheet  # noqa: E402

TARGET = {1: 0.82, 2: 0.85, 3: 0.89, 4: 0.85}  # reference medians of the object's largest dimension
ROOM_ABOVE, ROOM_ABOVE_MAX, MARGIN, MAX_PAD = 0.14, 0.21, 0.05, 0.12  # room above: reference median and upper quartile
OUT_W, OUT_H = 430, 480
TOUCH = 10            # box units (of 1000): an object this close to an edge touches it
OUTPAINT_MIN = 0.01   # outpaint when the window runs past the picture by more than this share of its side
SEAM_MAX = 5.0        # mean difference (0-255) allowed at the seam. W022: aligned results 0.9-4.9 after colour
                      # matching; a copy 4 px off scored 4.0 and 12 px off 7.8 before colour matching
FEATHER = 0.02        # seam blend width, share of the picture's side
OUTPAINT_PROMPT = (
    "This illustration sits in the middle of a larger square canvas; the blurred, stretched border around it is only "
    "a colour placeholder. Repaint the border so that the illustration continues outward naturally, in exactly the "
    "same style, colours and lighting: the same sky, backdrop or light rays above and at the sides, the same ground "
    "or tabletop below. Keep the original illustration exactly as it is, at the same size and position. Do not add "
    "new objects, text or frames. Return the whole square image.")


def raw_box(path: Path, log_dir: Path | None = None, card: str = "") -> list[int]:
    buffer = io.BytesIO()
    Image.open(path).convert("RGB").save(buffer, "PNG")
    result = gemini_image.generate_text(MODEL, [gemini_image.text_part(PROMPT), gemini_image.image_part(buffer.getvalue())])
    costs.log(log_dir, "vision", card, costs.text_cost(result["response"].get("usage", {})))
    text = result["text"]
    answer = json.loads(text[text.index("{"): text.rindex("}") + 1])
    return [max(0, min(1000, int(v))) for v in answer["box_2d"]]


def stretch_pad(image: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
    """Extend the picture outward by stretching its outermost 6 px rows or columns, with a 12 px soft seam."""
    rows, seam = 6, 12

    def horizontal(img: Image.Image, l: int, r: int) -> Image.Image:
        if not l and not r:
            return img
        w, h = img.size
        out = Image.new("RGB", (w + l + r, h))
        out.paste(img, (l, 0))
        fade = Image.linear_gradient("L").rotate(90, expand=True).resize((seam, h))  # 0 at the left column, 255 at the right
        # wider bands get a softer blur, so stretched texture reads as a smooth surface, not streaks
        soft = lambda size: ImageFilter.GaussianBlur(max(2, size // 8))  # noqa: E731
        if l:
            band = img.crop((0, 0, rows, h)).resize((l + seam, h), Image.BICUBIC).filter(soft(l))
            out.paste(band.crop((0, 0, l, h)), (0, 0))
            # the seam starts as pure band at the boundary and fades into the picture (W022: the mask was inverted)
            out.paste(band.crop((l, 0, l + seam, h)), (l, 0), fade.transpose(Image.FLIP_LEFT_RIGHT))
        if r:
            band = img.crop((w - rows, 0, w, h)).resize((r + seam, h), Image.BICUBIC).filter(soft(r))
            out.paste(band.crop((seam, 0, r + seam, h)), (l + w, 0))
            out.paste(band.crop((0, 0, seam, h)), (l + w - seam, 0), fade)
        return out

    def vertical(img: Image.Image, t: int, b: int) -> Image.Image:
        if not t and not b:
            return img
        return horizontal(img.transpose(Image.ROTATE_90), t, b).transpose(Image.ROTATE_270)

    return vertical(horizontal(image.convert("RGB"), left, right), top, bottom)


def window(size: tuple[int, int], box: list[int], category: int, stretch: bool) -> tuple[float, float, float, float]:
    """The card window (left, top, width, height) in picture pixels; it may run past the picture."""
    W, H = size
    y0, x0, y1, x1 = box
    bx0, by0, bx1, by1 = x0 / 1000 * W, y0 / 1000 * H, x1 / 1000 * W, y1 / 1000 * H
    bw, bh = max(1.0, bx1 - bx0), max(1.0, by1 - by0)
    target = TARGET.get(category, 0.85)
    ch = max(bw / (CARD_ASPECT * target), bh / target)            # object at the target size
    ch = max(ch, bw / (CARD_ASPECT * (1 - 2 * MARGIN)))             # side margins
    ch = max(ch, bh / (1 - ROOM_ABOVE - MARGIN))                    # room above and a margin below
    cw = CARD_ASPECT * ch
    left = (bx0 + bx1) / 2 - cw / 2
    slack = ch - bh
    room = max(ROOM_ABOVE * ch, min(slack / 2, slack - MARGIN * ch))  # centred, but at least ROOM_ABOVE above ...
    room = min(room, ROOM_ABOVE_MAX * ch) if slack > ROOM_ABOVE_MAX * ch else room  # ... and at most the reference q3
    top = by0 - room
    # How far the window may run past the picture per side (left, top, right, bottom). Stretching a side the object
    # touches smears the object (W022, the beanstalk); the image model continues the object instead, so outpainting may.
    pad = [MAX_PAD * W, MAX_PAD * H, MAX_PAD * W, MAX_PAD * H]
    if stretch:
        touches = [x0 <= TOUCH, y0 <= TOUCH, x1 >= 1000 - TOUCH, y1 >= 1000 - TOUCH]
        pad = [0.0 if t else p for t, p in zip(touches, pad)]
    room_w, room_h = W + pad[0] + pad[2], H + pad[1] + pad[3]
    if cw > room_w or ch > room_h:  # zoom in until the window fits: the object ends up a little above the norm
        s = min(room_w / cw, room_h / ch)
        cw, ch = cw * s, ch * s
        left = (bx0 + bx1) / 2 - cw / 2
        top = (by0 + by1) / 2 - ch / 2
    left = min(max(left, -pad[0]), W + pad[2] - cw)
    top = min(max(top, -pad[1]), H + pad[3] - ch)
    return left, top, cw, ch


def overrun(size: tuple[int, int], win: tuple[float, float, float, float]) -> list[int]:
    """How far the window runs past the picture: left, top, right, bottom, in px."""
    W, H = size
    left, top, cw, ch = win
    return [max(0, round(-left)), max(0, round(-top)), max(0, round(left + cw - W)), max(0, round(top + ch - H))]


def ring_mask(size: tuple[int, int], ring: float = 0.08) -> Image.Image:
    """White in the picture's outer ring (where the seam goes), black inside."""
    w, h = size
    mask, r = Image.new("L", size, 255), round(ring * max(w, h))
    ImageDraw.Draw(mask).rectangle((r, r, w - 1 - r, h - 1 - r), fill=0)
    return mask


def ring_diff(a: Image.Image, b: Image.Image, size: int = 256) -> float:
    """Mean difference between two copies of a picture in its outer ring. A moved, rescaled or recoloured copy scores
    high."""
    a = a.convert("RGB").resize((size, size), Image.BILINEAR)
    b = b.convert("RGB").resize((size, size), Image.BILINEAR)
    return ImageStat.Stat(ImageChops.difference(a, b).convert("L"), ring_mask((size, size))).mean[0]


def compose(image: Image.Image, model: Image.Image) -> tuple[Image.Image, dict]:
    """Fit the model's extended square around the original picture: match its colours to the original at the seam
    (the model sometimes shifts the whole palette slightly: W022, the magic beans), check the alignment, blend the
    original back in over the seam."""
    W, H = image.size
    S = round(max(W, H) * (1 + 2 * MAX_PAD))
    ml, mt = (S - W) // 2, (S - H) // 2
    out = model.convert("RGB").resize((S, S), Image.LANCZOS)
    ring = ring_mask((W, H))
    have = ImageStat.Stat(out.crop((ml, mt, ml + W, mt + H)), ring).mean
    want = ImageStat.Stat(image, ring).mean
    shift = [round(w - h) for w, h in zip(want, have)]
    out = Image.merge("RGB", [band.point(lambda v, s=s: max(0, min(255, v + s))) for band, s in zip(out.split(), shift)])
    seam = ring_diff(out.crop((ml, mt, ml + W, mt + H)), image)
    feather = max(8, round(FEATHER * max(W, H)))
    mask = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(mask)
    for i in range(feather):  # the original fades in over the seam
        draw.rectangle((i, i, W - 1 - i, H - 1 - i), outline=round(255 * i / feather))
    out.paste(image, (ml, mt), mask)
    return out, {"offset": [ml, mt], "seam": round(seam, 2), "ok": seam <= SEAM_MAX, "colour_shift": shift}


def outpaint(image: Image.Image, stem: Path) -> tuple[Image.Image, dict]:
    """Extend the picture by MAX_PAD per side with the image model, keeping the picture itself pixel for pixel.
    Writes the model's image and response as <stem>.model.png and <stem>.response.json; returns the canvas and info."""
    image = image.convert("RGB")
    W, H = image.size
    S = round(max(W, H) * (1 + 2 * MAX_PAD))
    ml, mt = (S - W) // 2, (S - H) // 2
    hint = stretch_pad(image, ml, mt, S - W - ml, S - H - mt)  # a colour placeholder the model repaints
    buffer = io.BytesIO()
    hint.save(buffer, "PNG")
    result = gemini_image.generate_image(cardgen.GEN_MODEL, [gemini_image.image_part(buffer.getvalue()),
                                                             gemini_image.text_part(OUTPAINT_PROMPT)],
                                         aspect_ratio="1:1", image_size="1K")
    model = Image.open(io.BytesIO(result.pop("image_bytes"))).convert("RGB")
    out, info = compose(image, model)
    stem.parent.mkdir(exist_ok=True)
    model.save(f"{stem}.model.png")
    info["cost"] = round(costs.image_cost(result["response"].get("usage", {})), 4)
    Path(f"{stem}.response.json").write_text(json.dumps({**result, **info}, indent=1), encoding="utf-8")
    return out, info


def route_sheets(plan: dict, plan_path: Path, route: str, route_dir: Path) -> None:
    """Variant sheets of the framed cards, so the review looks at what the set window will show (W023)."""
    if route == "gemini":
        cardgen.write_summary(plan, plan_path.parent)  # its spend line now includes this run's calls
        cardgen.sheets(plan_path)
        return
    for variant in plan["variants"]:
        items = [(f"{c['id']} {c['name']} C{c['category']} {'*' * c.get('stars', 0)}".rstrip(), route_dir / "final" / f"{c['id']}.png")
                 for c in variant["cards"] if (route_dir / "final" / f"{c['id']}.png").exists()]
        if items:
            build_sheet([(f"{variant['id']} 1-5", items[:5]), (f"{variant['id']} 6-10", items[5:])],
                        route_dir / "sheets" / f"variant_{variant['id']}.png", 240,
                        f"{plan['set']}: variant {variant['id']} ({route}, framed)")


def set_override(folder: Path, key: str, src: Path, box: str | None, fill: str | None, why: str | None) -> None:
    """Write one review override into framing.json, tied to the exact image it was made for (its mtime)."""
    if not why:
        raise SystemExit("--override needs --why: the reason is part of the record")
    if not (box or fill):
        raise SystemExit("--override needs --box and/or --fill")
    path = folder / "framing.json"
    framing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    entry = {"mtime": int(src.stat().st_mtime), "image": src.name, "why": why}
    if box:
        values = [int(v) for v in box.split(",")]
        if len(values) != 4:
            raise SystemExit("--box takes y0,x0,y1,x1 on a 0-1000 scale of the generated image")
        entry["box"] = values
    if fill:
        entry["fill"] = fill
    framing[key] = entry
    path.write_text(json.dumps(framing, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"override for {key} written to {path}")


def sources(plan: dict, folder: Path, route: str, ids: set[str] | None) -> dict[str, tuple[dict, Path, Path]]:
    """card id -> (card, generated image, route folder); Gemini: the chosen attempt in cards/<id>/."""
    out = {}
    for v in plan["variants"]:
        for c in v["cards"]:
            if ids and v["id"] not in ids and c["id"] not in ids:
                continue
            if route == "gemini":
                chosen = cardgen.collect_card(c, folder)["chosen"]  # chosen.json, or the run's own rule for older cards
                if chosen:
                    out[c["id"]] = (c, folder / "cards" / c["id"] / chosen, folder)
            else:
                raw = folder / route / "raw" / f"{c['id']}.png"
                if raw.exists():
                    out[c["id"]] = (c, raw, folder / route)
    return out


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--route", default="gpt", help="gemini, or the ChatGPT route folder (gpt, gpt_v7 ...)")
    parser.add_argument("--ids", help="variant or card ids, comma-separated")
    parser.add_argument("--fill", default="outpaint",
                        help="outpaint or stretch: how to extend the background; with --override also a saved attempt file")
    parser.add_argument("--recompose", action="store_true",
                        help="rebuild the outpainted canvases from the saved model images (no new calls)")
    parser.add_argument("--override", metavar="ID", help="write a review override for this card (with --box/--fill and --why)")
    parser.add_argument("--box", help="--override: y0,x0,y1,x1 on a 0-1000 scale of the generated image")
    parser.add_argument("--why", help="--override: the reason, kept in framing.json")
    parser.add_argument("--clear-override", metavar="ID", help="remove a card's review override")
    args = parser.parse_args(argv)
    if args.fill not in ("outpaint", "stretch") and not args.override:
        raise SystemExit("--fill is outpaint or stretch (a saved attempt file only with --override)")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    folder = args.plan.parent
    if args.override or args.clear_override:  # these commands frame only the card they touch
        args.ids = args.override or args.clear_override
    items = sources(plan, folder, args.route, set(args.ids.split(",")) if args.ids else None)
    route_dir = folder if args.route == "gemini" else folder / args.route
    if args.override:
        if args.override not in items:
            raise SystemExit(f"{args.override}: no generated image found for route {args.route}")
        fill = args.fill if any(a == "--fill" or a.startswith("--fill=") for a in argv) else None
        set_override(folder, f"{args.route}/{args.override}", items[args.override][1], args.box, fill, args.why)
        if args.fill not in ("outpaint", "stretch"):  # an attempt file is an override, not a run mode
            args.fill = "outpaint"
    if args.clear_override:
        path = folder / "framing.json"
        framing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        if framing.pop(f"{args.route}/{args.clear_override}", None) is not None:
            path.write_text(json.dumps(framing, indent=1, ensure_ascii=False), encoding="utf-8")
            print(f"override for {args.route}/{args.clear_override} removed")
    # Review overrides, sets/<slug>/framing.json: {"<route>/<card id>": {"mtime": ..., "image": ..., "why": "...",
    # "box": [y0, x0, y1, x1] and/or "fill": "stretch" or a saved outpaint attempt such as "C05.try2.model.png"}}.
    # A box for a scene whose subject is more than the vision model found (W022: the hammock without its palm trees);
    # a fill where the seam check and the eye disagree. An override holds only for the image it was made for.
    framing_path = folder / "framing.json"
    framing = json.loads(framing_path.read_text(encoding="utf-8")) if framing_path.exists() else {}
    overrides = {}
    for cid, (_, src, _) in items.items():
        override = framing.get(f"{args.route}/{cid}")
        if override and override.get("mtime") == int(src.stat().st_mtime):
            overrides[cid] = override
        elif override:
            print(f"{cid}: the framing override is for an earlier image; ignored")
    forced = {cid: o["fill"] for cid, o in overrides.items() if "fill" in o}
    cache_path = route_dir / "boxes_raw.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    stamp = lambda src: {"file": str(src), "mtime": int(src.stat().st_mtime)}  # noqa: E731
    fresh = lambda cid, src: {k: cache.get(cid, {}).get(k) for k in ("file", "mtime")} == stamp(src)  # noqa: E731
    # a hand-set box needs no vision call, so it also works while the balance is empty (W023)
    todo = {cid: src for cid, (_, src, _) in items.items() if not fresh(cid, src) and "box" not in overrides.get(cid, {})}
    billing = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(raw_box, src, folder, cid): cid for cid, src in todo.items()}
        for future in concurrent.futures.as_completed(futures):
            cid = futures[future]
            if future.cancelled():  # stopped after an empty-balance answer
                continue
            try:
                cache[cid] = {**stamp(todo[cid]), "box": future.result()}
            except gemini_image.BillingError:
                billing = True
                for other in futures:
                    other.cancel()
            except Exception as err:
                print(f"{cid}: box failed ({str(err)[:100]})")
    if todo:
        cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")
    for cid, override in overrides.items():  # applied after saving: boxes_raw.json keeps the vision boxes only
        if "box" in override:
            cache[cid] = {**stamp(items[cid][1]), "box": override["box"]}
        if cid in cache:
            cache[cid]["override"] = override["why"]
    # W023: a card whose box couldn't be measured keeps its final image; the cached box belongs to an older image
    stale = sorted(cid for cid, (_, src, _) in items.items() if not fresh(cid, src))
    if stale:
        print(f"no box for {', '.join(stale)}: left as they were; run the same command again to frame them")
    items = {cid: item for cid, item in items.items() if cid not in stale}

    # outpaint the cards whose window runs past the picture; earlier results are reused while the image is unchanged
    op_path = route_dir / "outpaint.json"
    op_cache = json.loads(op_path.read_text(encoding="utf-8")) if op_path.exists() else {}
    need = {}
    for cid, (card, src, _) in (items.items() if not billing else []):
        if cid in cache and args.fill == "outpaint" and cid not in forced:
            size = Image.open(src).size
            if max(overrun(size, window(size, cache[cid]["box"], card["category"], False))) > OUTPAINT_MIN * max(size):
                entry = op_cache.get(cid, {})
                if {k: entry.get(k) for k in ("file", "mtime")} != stamp(src):  # a failed seam check is not retried
                    need[cid] = src                                                # on re-runs; delete the entry to retry

    def run_outpaint(cid: str, src: Path) -> dict:
        """Up to two model calls (one retry if the seam check fails); every attempt is kept as outpaint/<id>.try<n>.*"""
        done = len(list((route_dir / "outpaint").glob(f"{cid}.try*.model.png")))
        canvas, info, tries, cost = None, {}, 0, 0.0
        while tries < 2 and not info.get("ok"):
            tries += 1
            canvas, info = outpaint(Image.open(src).convert("RGB"), route_dir / "outpaint" / f"{cid}.try{done + tries}")
            costs.log(folder, "outpaint", cid, info["cost"])
            cost += info["cost"]
        canvas.save(route_dir / "outpaint" / f"{cid}.png")
        models = [f"{cid}.try{done + n}.model.png" for n in range(1, tries + 1)]
        spent = op_cache.get(cid, {}).get("spent", op_cache.get(cid, {}).get("cost", 0)) + cost  # every run, not just the last
        return {**stamp(src), **info, "cost": round(cost, 4), "spent": round(spent, 4), "tries": tries,
                "models": models, "model": models[-1]}

    cost, done, unpainted = 0.0, 0, set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(run_outpaint, cid, src): cid for cid, src in need.items()}
        for future in concurrent.futures.as_completed(futures):
            cid = futures[future]
            if future.cancelled():  # counted below
                continue
            try:
                op_cache[cid] = future.result()
                cost, done = cost + op_cache[cid]["cost"], done + 1
            except gemini_image.BillingError:  # W023: leave the card as it was rather than stretch it
                billing = True
                unpainted.add(cid)
                for other in futures:
                    other.cancel()
            except Exception as err:  # the earlier entry stays: it records what was spent (W023)
                print(f"{cid}: outpaint failed ({str(err)[:160]}); stretching instead")
    unpainted |= {cid for f, cid in futures.items() if f.cancelled()}
    if unpainted:
        print(f"no background extension for {', '.join(sorted(unpainted))}: left as they were")
        items = {cid: item for cid, item in items.items() if cid not in unpainted}
    if args.recompose:  # rebuild the canvases from the saved model images, keeping the attempt with the best seam
        for cid, (_, src, _) in items.items():
            entry = op_cache.get(cid)
            if cid in need or not entry or {k: entry.get(k) for k in ("file", "mtime")} != stamp(src):
                continue
            image, best = Image.open(src).convert("RGB"), None
            for name in entry.get("models") or sorted(p.name for p in (route_dir / "outpaint").glob(f"{cid}.try*.model.png")):
                canvas, info = compose(image, Image.open(route_dir / "outpaint" / name))
                if best is None or info["seam"] < best[1]["seam"]:
                    best = (canvas, info, name)
            best[0].save(route_dir / "outpaint" / f"{cid}.png")
            op_cache[cid] = {**entry, **best[1], "model": best[2]}
    if need or args.recompose:
        op_path.write_text(json.dumps(op_cache, indent=1, sort_keys=True), encoding="utf-8")

    log_path = route_dir / "reframe_log.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else {}
    for cid, (card, src, _) in items.items():
        if cid not in cache:
            continue
        final = route_dir / "final" / f"{cid}.png"
        prev = route_dir / "final_prev" / f"{cid}.png"
        if final.exists() and not prev.exists():
            prev.parent.mkdir(exist_ok=True)
            shutil.copyfile(final, prev)
        image = Image.open(src).convert("RGB")
        box, category = cache[cid]["box"], card["category"]
        entry = op_cache.get(cid, {})
        win = window(image.size, box, category, False)
        pads = overrun(image.size, win)
        painted = entry.get("ok") and {k: entry.get(k) for k in ("file", "mtime")} == stamp(src)
        if billing and args.fill == "outpaint" and max(pads) > OUTPAINT_MIN * max(image.size) and not painted \
                and cid not in forced:  # W023: no stretched stand-in while the balance is empty
            print(f"{cid}: needs a background extension; left as it was")
            continue
        if forced.get(cid, "stretch") != "stretch":  # an outpaint attempt chosen in review
            canvas, entry = compose(image, Image.open(route_dir / "outpaint" / forced[cid]))
            ox, oy, fill = *entry["offset"], "outpaint"
        elif args.fill == "outpaint" and max(pads) > OUTPAINT_MIN * max(image.size) and entry.get("ok") \
                and {k: entry.get(k) for k in ("file", "mtime")} == stamp(src) and cid not in forced:
            canvas, (ox, oy), fill = Image.open(route_dir / "outpaint" / f"{cid}.png"), entry["offset"], "outpaint"
        else:
            if max(pads) > OUTPAINT_MIN * max(image.size):  # stretching: keep off the sides the object touches
                win = window(image.size, box, category, True)
                pads = overrun(image.size, win)
            canvas, (ox, oy) = stretch_pad(image, *pads), pads[:2]
            fill = "stretch" if max(pads) else "none"
        left, top, cw, ch = win
        crop = (round(left + ox), round(top + oy), round(left + ox + cw), round(top + oy + ch))
        final.parent.mkdir(exist_ok=True)
        canvas.crop(crop).resize((OUT_W, OUT_H), Image.LANCZOS).save(final)
        W, H = image.size
        bw, bh = (box[3] - box[1]) / 1000 * W, (box[2] - box[0]) / 1000 * H
        log[cid] = {"zoom": round(H / ch, 3), "pad": pads, "fill": fill, "extent": round(max(bw / cw, bh / ch), 3),
                    "room_above": round((box[0] / 1000 * H - top) / ch, 3)}
        if fill == "outpaint":
            log[cid]["seam"] = entry["seam"]
        if "override" in cache[cid]:
            log[cid]["override"] = cache[cid]["override"]
        print(f"{cid} {card['name']}: zoom {log[cid]['zoom']}, extent {log[cid]['extent']}, "
              f"room above {log[cid]['room_above']}, pad {pads} ({fill})")
    log_path.write_text(json.dumps(log, indent=1, sort_keys=True), encoding="utf-8")
    if done:
        print(f"outpainted {done} cards, estimated ${cost:.2f}")
    route_sheets(plan, args.plan, args.route, route_dir)
    if billing:
        print(gemini_image.BILLING_HELP)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
