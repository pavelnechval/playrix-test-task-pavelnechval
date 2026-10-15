# BENCH-03 result

## Final scores (W011): Pavel and the external model, both blind

Files: `scores_pavel.csv`, `scores_external_model.csv` (relayed by Pavel), `scores_assistant.csv`.

| Arm | Pavel: mean / pass | External: mean / pass | Assistant (blind): mean / pass |
|---|---|---|---|
| Nano Banana 2.1 (API, 12 separate references, 1:1) | **3.88 / 5 of 8** | **3.75 / 6 of 8** | 3.50 / 3 of 8 |
| ChatGPT via Codex (reference sheet, portrait output, cropped) | 3.50 / 3 of 8 | 3.63 / 3 of 8 | 3.75 / 5 of 8 |

**Crop confound, confirmed from the uncropped originals:**

- Pavel's four lowest ChatGPT scores (H5, L5, P7, Y2: 3 / yes) are the bottles and lighthouses that our crop to card shape made "too large vs frame", with the nozzle and roof cut off and the angle looking "weird".
- Uncropped, they are complete.
- Two ChatGPT misses are genuine: no saucer (D8) and no pole on the kart (S8).
- On the targets the crop didn't touch (T2, T3), the models are about even: ChatGPT 4.0 (Pavel: J2 4, D8 3, F9 4, S8 5) against Nano Banana 3.75 (T8 4, H8 4, A8 3, B2 4).

**Nano Banana improved with each prompt version** (same model, same hidden targets):

| Prompt | Pavel pass rate | External pass rate |
|---|---|---|
| v1 | 0 of 4 | 1 of 4 |
| v2 | 3 of 8 | 4 of 8 |
| v3 | 5 of 8 | 6 of 8 |

Pavel's best-in-row picks for v3: P2 lighthouse (5), S8 kart (5, ChatGPT), J2 cup ("maybe best overall", ChatGPT).

**Rater agreement:**

| Pair | Exact style score | Within ±1 | Same "notice" answer |
|---|---|---|---|
| Pavel – external | 10 of 16 | — | 13 of 16 |
| Pavel – assistant | 7 of 16 | 16 of 16 | 8 of 16 |

- The assistant was too lenient on big, edge-crowding objects and too strict on decoration and warm tints. Its judgement needs calibrating with Pavel's rules before it can run QA automatically (D-018).

**New rules from Pavel's v3 notes (for prompt v4 and the QA rubric):**

- Object not too large: clear margins on all sides, never touching the frame (H5, L5).
- Complete object with its standard parts: a cup with its saucer, a dodgem with its vertical pole (D8, S8).
- One distinctive, charming detail (like the flower on the reference cup) instead of generic bands (D8, H8, J2, T8).
- Vehicles in two main colours (B2).
- The background pattern clearly visible, not bleak; the object never blending into the background (U7).
- Floor and wall in separate tones (F9).
- An overall bright image (Q9).
- Steam still off on Nano Banana (H8).
- Background still too detailed (A8).

**Decisions (proposed):**

- D-017: Nano Banana 2.1 is the pipeline model; GPT Image through the API is deferred.
- D-018: QA rubric calibrated to Pavel.

---

## Provisional section written before the human scores (kept for the record)

**Pavel: score `sheets/compare_large.png` before reading this file. It names which model made which image.**

## What ran (2026-10-13 evening, W010)

| Arm | Route | References | Output | Cost | Time |
|---|---|---|---|---|---|
| nb21 | `gemini-nano-banana-2.1` through the Gemini API (`bench.py run nb21`) | 12 separate Miro originals | 1:1, 1K | ≈ $0.44 ($0.055 each) | ≈ 24 s each |
| chatgpt | Codex `image_gen.imagegen` on Pavel's ChatGPT plan (`codex_task.md`); model not exposed | The 3×4 reference sheet (the tool accepts at most 5 paths) | Portrait, 1028×1530 | $0 extra (plan) | 23–43 s each |

- Both arms used prompt v3 with identical text. The OpenAI-format prompt had the one sheet sentence added.
- 2 samples × 4 hidden targets per arm, one attempt each, nothing edited. Codex's log: `runs/chatgpt_log.md`.

## Assistant blind scores

Scored from `sheets/compare_large.png` before `blind_key.json` was opened. Full notes: `scores_assistant.csv`.

| Target | ChatGPT (code: style / notice) | Nano Banana 2.1 (code: style / notice) |
|---|---|---|
| T1 Bottle | L5 4 / no, H5 4 / no | U7 3 / yes, S5 3 / yes |
| T2 Tea Cup | J2 4 / no, D8 4 / no | T8 4 / no, H8 4 / yes |
| T3 Bumpers | F9 4 / no, S8 4 / yes | A8 4 / no, B2 3 / yes |
| T4 Lighthouse | P7 3 / yes, Y2 3 / yes | Q9 3 / yes, P2 4 / no |
| **Mean style / pass rate** | **3.75 / 5 of 8** | **3.50 / 3 of 8** |

## Finding after unblinding: the crop, not the model, failed the ChatGPT lighthouses

- Codex returns portrait images, and the sheets centre-crop every image to the card aspect (0.896). That removes about 25% of the height, and on both ChatGPT lighthouses it cut off the lamp room.
- The uncropped originals (`sheets/AFTER_SCORING_chatgpt_uncropped.png`) show complete, on-style lighthouses: warm red, low angle, strip of sea, soft clouds.
- Through the API, GPT Image 2.5 can be asked for the card aspect directly (`1024x1136`), so this problem would not exist in the pipeline.
- The blind scores above stay as recorded. The assistant's view after unblinding, not blind: P7 and Y2 would likely pass uncropped.

## Other observations

- **ChatGPT bottles** (smooth body, one band, warm rays) and **tea cups** (white cup and saucer, wispy steam, dark tea, warm background) are the closest to the references so far.
- **Nano Banana with prompt v3** regressed in places:
  - water droplets (U7);
  - a toy-like dark bottle (S5);
  - busy car decoration and a teal background (B2);
  - a sunset tint (Q9).
  These suggest the longer v3 prompt does not help Nano Banana reliably. Pavel's scores will show whether v3 beats v2 for this model.

## Possible implication (hypothesis; depends on Pavel's scores)

A hybrid: Nano Banana 2.1 for cheap set variants and exploration, and GPT Image 2.5 through the API (exact card aspect) for the final renders of the chosen set. That means about 30 final images at an estimated $0.25–0.60 each. It would also match the brief's "pick the right model for each task".
