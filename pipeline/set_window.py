"""Lay a finished variant into the brief's empty set template, as players would see it in the game.

    python -I pipeline/set_window.py sets/<slug>/plan.json B [--final-dir gpt/final] [--template pink]

The template (references/miro_v1/set_templates/) is picked by the variant's window_color (or --template).
The cards go into its 10 transparent slots in plan order. That is star order in schema-2 plans, and the
template's slot stars are 1,1,2,2,3 / 3,4,4,5,5. The placeholder title and card names are painted out
(each row is filled from the plate or banner colour on either side) and replaced with the set title and
card names. Output: <plan folder>/<final-dir parent>/sheets/window_<variant>.png plus a smaller _preview.jpg.
The templates are the hiring company's assets, so these images stay out of any public repository.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

TEMPLATES = ROOT / "references" / "miro_v1" / "set_templates"
TEMPLATE_FILES = {"orange": "template1_Orange.png", "pink": "template2_Pink.png",
                  "violet": "template3_Violet.png", "blue": "template4_Blue.png"}
FONT = Path("C:/Windows/Fonts/BRLNSDB.TTF")  # Berlin Sans FB Demi: rounded and bold, close to the game's UI font
# fallbacks for machines without it: Windows, macOS, Linux; Pillow's built-in font as the last resort
FALLBACK_FONTS = [Path("C:/Windows/Fonts/ariblk.ttf"), Path("/System/Library/Fonts/Supplemental/Arial Black.ttf"),
                  Path("/Library/Fonts/Arial Black.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")]
TITLE_SEARCH = (1600, 80, 3900, 340)  # banner area that holds the placeholder title
BLEED = 14  # art extends this far under the frame on every side


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in [FONT, *FALLBACK_FONTS]:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def find_slots(template: Image.Image) -> list[tuple[int, int, int, int]]:
    """The 10 transparent card areas, row by row, found on a 1/4-scale alpha mask."""
    alpha = template.getchannel("A").resize((template.width // 4, template.height // 4))
    w, h = alpha.size
    px = alpha.load()
    seen = bytearray(w * h)
    boxes = []
    for y in range(h):
        for x in range(w):
            if px[x, y] >= 16 or seen[y * w + x]:
                continue
            stack, seen[y * w + x] = [(x, y)], 1
            x0, y0, x1, y1, n = x, y, x, y, 0
            while stack:
                cx, cy = stack.pop()
                n += 1
                x0, y0, x1, y1 = min(x0, cx), min(y0, cy), max(x1, cx), max(y1, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and px[nx, ny] < 16:
                        seen[ny * w + nx] = 1
                        stack.append((nx, ny))
            box = (x0 * 4, y0 * 4, (x1 + 1) * 4, (y1 + 1) * 4)
            if n > 200 and box[2] - box[0] < template.width // 2:  # skip the transparent area around the window
                boxes.append(box)
    if len(boxes) != 10:
        raise SystemExit(f"expected 10 card slots in the template, found {len(boxes)}")
    return sorted(boxes, key=lambda b: (b[1] // 200, b[0]))


def text_bbox(image: Image.Image, area: tuple[int, int, int, int], threshold: int = 60) -> tuple[int, int, int, int] | None:
    """Pixels in the area that differ from the row's edge colour (the plate or banner) are text."""
    x0, y0, x1, y1 = area
    px = image.load()
    found = None
    for y in range(y0, y1):
        left, right = px[x0, y], px[x1 - 1, y]
        for x in range(x0, x1, 2):
            t = (x - x0) / max(1, x1 - 1 - x0)
            ref = [left[i] * (1 - t) + right[i] * t for i in range(3)]
            if sum(abs(px[x, y][i] - ref[i]) for i in range(3)) > threshold:
                found = (min(found[0], x), min(found[1], y), max(found[2], x), max(found[3], y)) if found else (x, y, x, y)
    return found


def paint_out(image: Image.Image, box: tuple[int, int, int, int], margin: int = 8) -> None:
    """Fill each row of the box from the colours just left and right of it (keeps vertical gradients)."""
    x0, y0, x1, y1 = box[0] - margin, box[1] - margin, box[2] + margin, box[3] + margin
    px = image.load()
    for y in range(y0, y1 + 1):
        left, right = px[x0 - 1, y], px[x1 + 1, y]
        for x in range(x0, x1 + 1):
            t = (x - x0) / max(1, x1 - x0)
            px[x, y] = tuple(round(left[i] * (1 - t) + right[i] * t) for i in range(4))


def draw_fitted(draw: ImageDraw.ImageDraw, text: str, centre: tuple[int, int], max_width: int, size: int,
                fill: str, stroke: str, stroke_width: int, shadow: int = 0) -> None:
    while size > 10 and draw.textlength(text, font=font(size)) > max_width:
        size -= 2
    f = font(size)
    if shadow:
        draw.text((centre[0], centre[1] + shadow), text, font=f, fill=(60, 20, 0, 150), anchor="mm",
                  stroke_width=stroke_width, stroke_fill=(60, 20, 0, 150))
    draw.text(centre, text, font=f, fill=fill, anchor="mm", stroke_width=stroke_width, stroke_fill=stroke)


def build(plan_path: Path, variant_id: str, final_dir: str, template_name: str | None) -> Path:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    variant = next(v for v in plan["variants"] if v["id"] == variant_id)
    colour = template_name or variant.get("window_color") or "blue"
    template = Image.open(TEMPLATES / TEMPLATE_FILES[colour]).convert("RGBA")
    slots = find_slots(template)
    art = Image.new("RGBA", template.size, (0, 0, 0, 0))
    for card, (x0, y0, x1, y1) in zip(variant["cards"], slots):
        image = Image.open(plan_path.parent / final_dir / f"{card['id']}.png").convert("RGBA")
        w, h = x1 - x0 + 2 * BLEED, y1 - y0 + 2 * BLEED
        scale = max(w / image.width, h / image.height)  # cover the slot, centre-cropping the rest
        image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
        left, top = (image.width - w) // 2, (image.height - h) // 2
        art.paste(image.crop((left, top, left + w, top + h)), (x0 - BLEED, y0 - BLEED))
    window = Image.alpha_composite(art, template)
    title_box = text_bbox(window, TITLE_SEARCH)
    if title_box:
        paint_out(window, title_box)
    plates = []
    for x0, y0, x1, y1 in slots:
        area = (x0 + 20, y1 + 26, x1 - 20, y1 + 104)
        box = text_bbox(window, area)
        if box:
            paint_out(window, box, margin=6)
        plates.append(((x0 + x1) // 2, y1 + 66, x1 - x0 - 50))
    draw = ImageDraw.Draw(window)
    title_centre = ((TITLE_SEARCH[0] + TITLE_SEARCH[2]) // 2, (title_box[1] + title_box[3]) // 2 if title_box else 210)
    draw_fitted(draw, plan["set"].upper(), title_centre, 2000, 190, "#ffd84a", "#7a2e00", 12, shadow=10)
    for card, (cx, cy, max_w) in zip(variant["cards"], plates):
        draw_fitted(draw, card["name"].upper(), (cx, cy), max_w, 62, "#ffffff", "#4a1e08", 6)
    out_dir = plan_path.parent / Path(final_dir).parent / "sheets"
    out_dir.mkdir(parents=True, exist_ok=True)
    background = Image.new("RGBA", window.size, (22, 28, 52, 255))
    result = Image.alpha_composite(background, window).convert("RGB")
    bbox = window.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()  # trim to the window itself
    result = result.crop((max(0, bbox[0] - 40), max(0, bbox[1] - 40), min(result.width, bbox[2] + 40), min(result.height, bbox[3] + 40)))
    out = out_dir / f"window_{variant_id}.png"
    result.save(out)
    preview = result.resize((1800, round(result.height * 1800 / result.width)), Image.LANCZOS)
    preview.save(out_dir / f"window_{variant_id}_preview.jpg", quality=90)
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path)
    parser.add_argument("variant")
    parser.add_argument("--final-dir", default="final")
    parser.add_argument("--template", choices=sorted(TEMPLATE_FILES))
    args = parser.parse_args(argv)
    print(build(args.plan, args.variant, args.final_dir, args.template))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
