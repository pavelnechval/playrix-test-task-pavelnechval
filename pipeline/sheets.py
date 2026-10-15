"""Comparison sheets: labelled rows of card images at a chosen display height.

Every image is centre-cropped to the reference card aspect before scaling, so
generated squares and reference cards compare like for like.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

CARD_ASPECT = 430 / 480  # Miro originals are 430x480 px (D-005)


def to_card(image: Image.Image, height: int) -> Image.Image:
    w, h = image.size
    if w / h > CARD_ASPECT:  # too wide: trim the sides
        new_w = round(h * CARD_ASPECT)
        left = (w - new_w) // 2
        image = image.crop((left, 0, left + new_w, h))
    else:  # too tall: trim top and bottom
        new_h = round(w / CARD_ASPECT)
        top = (h - new_h) // 2
        image = image.crop((0, top, w, top + new_h))
    return image.resize((round(height * CARD_ASPECT), height), Image.LANCZOS)


def extend_to_card(image: Image.Image, height: int) -> Image.Image:
    """Fit a square (or wider) image to the card shape without cutting its sides: keep the full width and
    extend the background above and below by stretching the outermost rows, with a soft 12 px seam.

    W019: the ChatGPT route draws squares with margins much like the reference cards'. Cutting about 5% off
    each side (to_card) pushed wide objects into the edges, so this keeps the sides and adds room above.
    """
    w = round(height * CARD_ASPECT)
    scaled = image.convert("RGB").resize((w, round(image.height * w / image.width)), Image.LANCZOS)
    pad = height - scaled.height
    if pad <= 0:
        return to_card(image, height)
    top, bottom = pad // 2, pad - pad // 2
    canvas = Image.new("RGB", (w, height))
    canvas.paste(scaled, (0, top))
    seam, rows = 12, 6
    band_top = scaled.crop((0, 0, w, rows)).resize((w, top + seam), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
    band_bot = scaled.crop((0, scaled.height - rows, w, scaled.height)).resize((w, bottom + seam), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
    fade_in = Image.linear_gradient("L").resize((w, seam))  # 0 at the top row, 255 at the bottom row
    canvas.paste(band_top.crop((0, 0, w, top)), (0, 0))
    canvas.paste(band_top.crop((0, top, w, top + seam)), (0, top), fade_in.transpose(Image.FLIP_TOP_BOTTOM))
    canvas.paste(band_bot.crop((0, seam, w, bottom + seam)), (0, height - bottom))
    canvas.paste(band_bot.crop((0, 0, w, seam)), (0, height - bottom - seam), fade_in)
    return canvas


# Caption fonts with accented Latin letters (W023: Pillow's built-in font drew "Fête" as "F□te"); the built-in one is the last resort
CAPTION_FONTS = [Path("C:/Windows/Fonts/arial.ttf"), Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
                 Path("/Library/Fonts/Arial.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]


def caption_font(size: int) -> ImageFont.FreeTypeFont:
    for path in CAPTION_FONTS:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def build_sheet(rows: list[tuple[str, list[tuple[str, Path]]]], out_path: Path, cell_height: int, title: str = "") -> None:
    """rows: [(row label, [(caption, image path), ...]), ...]"""
    font_size = 14 if cell_height < 150 else 22
    font = caption_font(font_size)
    cell_w = round(cell_height * CARD_ASPECT)
    gap, margin, label_w = 12, 16, 170
    caption_h = font_size + 10
    title_h = font_size + 20 if title else 0
    n_cols = max(len(items) for _, items in rows)
    width = margin * 2 + label_w + n_cols * (cell_w + gap)
    height = margin * 2 + title_h + len(rows) * (cell_height + caption_h + gap)
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    if title:
        draw.text((margin, margin), title, fill="black", font=font)
    y = margin + title_h
    for label, items in rows:
        draw.text((margin, y + cell_height // 2 - font_size // 2), label, fill="black", font=font)
        x = margin + label_w
        for caption, path in items:
            sheet.paste(to_card(Image.open(path).convert("RGB"), cell_height), (x, y))
            size = font_size  # shrink a long caption to its own cell, so it never runs into the next one (W018)
            while size > 10 and draw.textlength(caption, font=caption_font(size)) > cell_w:
                size -= 1
            draw.text((x, y + cell_height + 3), caption, fill="black", font=caption_font(size))
            x += cell_w + gap
        y += cell_height + caption_h + gap
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
