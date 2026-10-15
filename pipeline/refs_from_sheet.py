"""Crop the brief's 16x10 card sheet ("Только карточки", p. 6) into one PNG per card.

Usage:
    python -I pipeline/refs_from_sheet.py SHEET_PNG OUT_DIR

Cards are located from the white gutters between them, so no pixel positions
are hard-coded. Writes rRRcCC.png (row, column; 1-based) plus index.json.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

WHITE = 240  # grey level treated as page background
MIN_CARD = 40  # px; shorter content runs are noise


def content_runs(white_fractions: list[float]) -> list[tuple[int, int]]:
    """(start, length) of runs where fewer than half of the pixels are white."""
    runs, start = [], None
    for i, white in enumerate(white_fractions + [1.0]):
        if white < 0.5 and start is None:
            start = i
        elif white >= 0.5 and start is not None:
            runs.append((start, i - start))
            start = None
    return runs


def find_grid(image: Image.Image) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    grey = image.convert("L")
    width, height = grey.size
    px = grey.load()
    row_white = [sum(px[x, y] > WHITE for x in range(width)) / width for y in range(height)]
    rows = [r for r in content_runs(row_white) if r[1] >= MIN_CARD]
    # The grey title bar is also a content run; card rows share one height, so keep the typical one.
    typical = sorted(h for _, h in rows)[len(rows) // 2]
    rows = [r for r in rows if abs(r[1] - typical) <= 4]
    top, bottom = rows[0][0], rows[-1][0] + rows[-1][1]
    col_white = [sum(px[x, y] > WHITE for y in range(top, bottom)) / (bottom - top) for x in range(width)]
    cols = [c for c in content_runs(col_white) if c[1] >= MIN_CARD]
    return rows, cols


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    sheet, out_dir = Path(argv[0]), Path(argv[1])
    image = Image.open(sheet).convert("RGB")
    rows, cols = find_grid(image)
    out_dir.mkdir(parents=True, exist_ok=True)
    cells = {}
    for r, (y, h) in enumerate(rows, 1):
        for c, (x, w) in enumerate(cols, 1):
            box = (x + 1, y + 1, x + w - 1, y + h - 1)  # 1 px inset drops anti-aliased gutter edges
            name = f"r{r:02d}c{c:02d}"
            image.crop(box).save(out_dir / f"{name}.png")
            cells[name] = box
    index = {
        "source": sheet.name,
        "source_sha256": hashlib.sha256(sheet.read_bytes()).hexdigest(),
        "source_size": list(image.size),
        "rows": len(rows),
        "cols": len(cols),
        "cells": cells,
    }
    (out_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"{len(rows)} rows x {len(cols)} cols -> {len(cells)} cards in {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
