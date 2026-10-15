# Reference images (Playrix assets: do not publish)

These are the hiring team's reference cards. Keep them out of any public repository; see `NOTICE.md`.

## pdf_v0

- `source_sheet_p6.png`: the "Только карточки" sheet (brief p. 6) as embedded in the PDF, 733×1312 px. The earlier Codex session (W001) extracted it to `D:\JOB2026HUNT\tmp\pdfs\ai-pilled-brief\page-1-6.png`; it was copied here on 2026-10-13.
- `cards/`: 160 crops of ≈60×66 px each, made by `pipeline/refs_from_sheet.py`.
  - Names follow rRRcCC (row and column, 1-based).
  - `index.json` stores the crop boxes and the hash of the source sheet.

## miro_v1

Original card images from Pavel's copy of the Miro board (https://miro.com/app/board/uXjVEdsb-i4=/), fetched through the Miro connector on 2026-10-13.

- `board_map.json`: Miro item ids of all 160 cards in the "Примеры карточек" frame, laid out on the same row/column grid as the PDF sheet.
- `cards/`: the originals downloaded so far, each 430×480 px opaque PNG, named rRRcCC.
  - `manifest.json` records each file's size, original file name (`CardC6_card_NN.png`) and Miro item id.
  - All 160 downloaded (W017), plus the 16 set windows of the "Summer" collection (`collection_summer/`) and the 4 empty window templates (`set_templates/`).
  - The signed links expire about 15 minutes after they're issued, so each batch is downloaded immediately.
