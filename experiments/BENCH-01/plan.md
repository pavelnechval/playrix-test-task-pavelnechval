# BENCH-01: leave-one-out style benchmark

**Status:** **run on 2026-10-13 (W006)** with Miro originals: 8 of 8 images, about $0.77. Results are in `result.md`; Pavel's blind scores are pending.

**v3 (W005):**

- The style pack and ground truth now come from the Miro originals (430×480 px, sent as-is): `--refs miro_v1`, the default.
- The PDF-crop version stays available as an optional comparison (`--refs pdf_v0`).
- All commands below accept `--refs`.
**Informs:** D-002, the model and settings the pipeline is built around.

Changelog:

- v1 (W003): plan drafted.
- v2 (W004):
  - Model family fixed to Nano Banana, with 2.1 as the main arm and Pro for comparison.
  - The C3 target changed from Coffee Pot to Bumpers.
  - Tooling written.

## Question

Can Nano Banana draw a **new** object in the reference style and the correct composition category, reliably enough that it doesn't stand out next to the real cards? Is 2.1 enough, or is Pro clearly better?

## Design

- **Hidden targets:** official category examples (brief pp. 3–4) with clean ground truth on the p. 6 sheet. They are never sent to a model.

  | ID | Card | Category | Sheet cell | Subject text sent |
  |---|---|---|---|---|
  | T1 | Bottle | 1 | r05c07 | "a sports water bottle" |
  | T2 | Tea Cup | 2 | r07c06 | "a tea cup" |
  | T3 | Bumpers | 3 | r06c02 | "a bumper car (a fairground dodgem)" |
  | T4 | Lighthouse | 4 | r14c08 | "a lighthouse" |

- **Style pack:** the same 8 cards for every call, 2 per category, each labelled with its category in the prompt.
  - Cards: R1 Fan Fold, R2 Popsicle, R3 Mojito, R4 Beach Bag, R5 Fruit Plate, R6 Computer, R7 Field Ball, R8 Coaster.
  - Basis: R1, R3, R4, R7 and R8 are official category examples. R2, R5 and R6 are categorised by our reading of the rules.
  - Format: PDF crops of ≈60×66 px, sent enlarged 4×.
  - Verified visually in `sheets/refs_overview.png`; the script blocks any target leaking into the pack.
- **Prompt:** `prompt_v1.md`, identical for every model. The fully expanded requests are in `prompts/`.
- **Arms:** one attempt per target, no cherry-picking.

  | Arm | Model | Size | Images | Est. output cost |
  |---|---|---|---|---|
  | nb21 | `gemini-nano-banana-2.1` | 1:1, 1K | 4 | $0.13 |
  | nbpro | `gemini-3-pro-image` | 1:1, 1K | 4 | $0.54 |

  Input tokens add a few cents per call. Thinking is left at the model default.
- **Optional second pass:** repeat with Miro originals (`REFERENCE_SET = "miro_v1"`). This measures how much better references help, for about the same cost again.

## Evaluation

- `bench.py sheets` builds blind comparison sheets: the real card next to the outputs, which are labelled with random codes.
  - Two versions: real card size (66 px tall) and enlarged.
  - The code-to-arm mapping is kept in `blind_key.json`.
- Pavel scores in `scores_pavel.csv`, 1–5 on:
  - Style match
  - Category correctness
  - Readability at card size
  - Clean output (no text, UI, frame or extra objects)
  - Object-to-frame scale
  - Plus a yes/no: would players notice?
- The assistant scores separately with the same rubric (not blind, because it ran the calls). Comparing the two scores shows whether automated QA can be trusted.
- Logged per call: timing, retries, images returned and the estimated cost (`runs/`).

## Decision rule (proposed)

- Build on the arm with the best mean score for style and category, weighing cost per image.
- If neither arm averages ≥4/5 on style, don't start the pipeline. First test stronger conditioning: Miro originals, more references, or approved anchor images.

## Commands

```
python -I experiments/BENCH-01/bench.py prepare        # done (free)
python -I pipeline/gemini_image.py check               # free: verifies the key, lists models
python -I experiments/BENCH-01/bench.py run            # paid: both arms (or: run nb21)
python -I experiments/BENCH-01/bench.py sheets         # blind sheets + score template
```
