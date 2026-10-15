# BENCH-01 result (miro_v1)

**Pavel: score `sheets/miro_v1/compare_large.png` before reading this file. It names which model made which image.**

Run: 2026-10-13, about 02:19–02:25 Berlin time. Plan: `plan.md` (v3). Prompt: `prompt_v1.md`, identical for both arms.

## Setup

| Item | Value |
|---|---|
| References | 8 Miro originals (430×480), 2 per category; the 4 hidden targets were never sent |
| Arms | `gemini-nano-banana-2.1` and `gemini-3-pro-image`; 1:1, 1K, thinking at model default |
| Attempts | One per target and arm, no retries, no cherry-picking: 8 images, all kept |
| Logs | `runs/miro_v1_<arm>_<target>.request.json` / `.response.json` (exact text and reference hashes; responses redacted) |
| Outputs | `outputs/miro_v1_<arm>_<target>.jpg`, 1024×1024 JPEG returned by the API, SynthID watermarked per the docs |

## Cost and time (measured from API usage)

| Model | Images | Input tokens | Est. cost | Avg time |
|---|---|---|---|---|
| Nano Banana 2.1 | 4 | 37,723 | $0.19 (≈$0.048/image) | 18.4 s |
| Nano Banana Pro | 4 | 19,803 | $0.58 (≈$0.144/image) | 19.0 s |

Cost = input tokens × list price + image output price, using the pricing page as read on 2026-10-13. Thought tokens (3,311 and 748) are not priced here. Total is about $0.77, matching the "under $1" estimate.

## Blind assistant scores (made before the key was opened)

Full table: `scores_assistant_miro_v1.csv`. Scale 1–5.

| Code | Target | Model | Style | Category | Readability | Clean | Scale | Mean |
|---|---|---|---|---|---|---|---|---|
| K7 | Bottle | 2.1 | 3 | 4 | 3 | 5 | 4 | 3.8 |
| U5 | Bottle | Pro | 3 | 4 | 4 | 5 | 4 | 4.0 |
| V5 | Tea Cup | 2.1 | 4 | 3 | 4 | 4 | 4 | 3.8 |
| Y3 | Tea Cup | Pro | 3 | 5 | 3 | 5 | 4 | 4.0 |
| R2 | Bumpers | 2.1 | 4 | 3 | 4 | 5 | 4 | 4.0 |
| K2 | Bumpers | Pro | 4 | 5 | 5 | 5 | 4 | 4.6 |
| L3 | Lighthouse | 2.1 | 4 | 5 | 3 | 5 | 3 | 4.0 |
| C6 | Lighthouse | Pro | 4 | 5 | 4 | 5 | 3 | 4.2 |

**Arm means:**

| Model | Style | Category | Overall |
|---|---|---|---|
| Nano Banana 2.1 | 3.75 | 3.75 | 3.9 |
| Nano Banana Pro | 3.50 | 4.75 | 4.2 |

With n = 4 per arm and one attempt each, this is a direction, not a conclusion. Pavel's blind scores are still pending.

## Observations

- **Both models already produce casual mobile-game art.** All eight are clean (no text, frames or UI) and readable at card size (`sheets/miro_v1/compare_card_size.png`).
- **2.1 has the more game-like saturation and chunkiness, but drifts on categories and detail.**
  - Category: a wooden table under the category-2 tea cup; string lights and a barrier behind the category-3 bumper car.
  - Detail: mesh, droplets and flame decals.
- **Pro follows the category rules more closely, but two outputs miss on style:** a pastel, low-saturation tea cup and a dark outline on the bottle.
- **Systematic misses, all addressable in the prompt:**
  1. **Background colour doesn't contrast with the object.** Both bottles are blue on blue; the references pair the object with a contrasting saturated colour.
  2. **Detail budget is exceeded** ("no small details" is ignored).
  3. **Saturation drops** (Pro's tea cup).
  4. **Category-4 framing.** The reference lighthouse fills the frame and is cut off by the bottom edge; both outputs show the whole tower smaller.
  5. **Outlines appear,** which the references don't use.

## Decision rule outcome (proposed)

- Neither arm reaches a mean style score of ≥4. Under plan.md, that means: don't build the pipeline yet; test stronger conditioning first.
- Proposed next step, **BENCH-02**:
  - prompt v2 with explicit rules for the five misses above;
  - optionally 12 references (3 per category);
  - same hidden targets, both arms; about $0.80.
- This also measures how much the prompt fixes, which is useful evidence for Miro.

## Human and external ratings (added in W007)

Sources:

- Pavel scored `compare_large.png` blind: `scores_pavel_miro_v1.csv` (style plus notes; the spreadsheet saved each row as one quoted field).
- An external model's ratings, relayed by Pavel; the model is not named: `scores_external_model_miro_v1.csv`.

| Code | Model | Pavel | Assistant (blind) | External | Players would notice (Pavel) |
|---|---|---|---|---|---|
| K7 | 2.1 | 3 | 3 | 3 | yes |
| U5 | Pro | 3 | 3 | 2 | yes |
| V5 | 2.1 | 4 | 4 | 3 | yes |
| Y3 | Pro | 3 | 3 | 2 | yes |
| K2 | Pro | 4 | 4 | 3 | yes |
| R2 | 2.1 | 4 | 4 | 4 | yes |
| C6 | Pro | 4 | 4 | 3 | yes |
| L3 | 2.1 | 4 | 4 | 3 | yes |

**Mean style score by rater:**

| Model | Pavel | Assistant | External |
|---|---|---|---|
| Nano Banana 2.1 | 3.75 | 3.75 | 3.25 |
| Nano Banana Pro | 3.50 | 3.50 | 2.50 |

### Agreement

- **Pavel and the assistant gave identical style scores on all 8 images.** Both scored blind. This assumes Pavel scored before opening this file, as asked.
  - The scale is coarse and the sample small, so this is encouraging but not proof that automated QA can replace a human.
- **The external model averaged 0.75 points lower,** with the same model ranking.
- **All three raters put 2.1 ahead of or level with Pro on style.**
- **Pavel judged that players would notice all 8 images.** The external model said 7 of 8, all except R2. **No image passes the brief's test yet.**

### Decision

**D-002 resolved: Nano Banana 2.1 is the main model.**

- It led on style for all three raters.
- It costs about a third as much ($0.048 vs $0.144 per image).
- It matches Pavel's original choice.
- Pro is not used in BENCH-02.

### New rules from the notes, used in prompt v2 (`../BENCH-02/prompt_v2.md`)

**From Pavel:**

- Too many details (K7) versus too few (Y3): aim for medium detail.
- Too glossy (U5).
- Background the same colour as the object, weak contrast (K7, U5).
- Holder doesn't read as a bottle (U5): use the most typical silhouette.
- Steam not in the reference style (V5).
- Wooden table makes it read as category 3 (V5).
- Object colour blends with the background (V5).
- Background should be round to fit the object (K2).
- Floor should mirror the object (K2).
- Background too detailed (R2).
- Category 4: low angle so the object feels big; terrain is left out of the references on purpose (C6).
- Object too small; sky style off (L3).

**From the external model:** rendering is the main inconsistency.

- Outlines and flatter shading (U5).
- Harder highlight shapes and graphic shading (V5).
- Photographic soft lighting (Y3).
- Too flat and toy-like (K2).
- Too soft, losing crisp material definition (C6).
- Painterly (L3).

**Conflict:** the external model said colours and designs were not the main issue. Pavel's notes flag background contrast repeatedly, so Pavel's notes take priority.

## Human/AI contributions

- **Assistant:** chose the targets and pack, wrote the prompt and scripts, ran the calls, scored blind, analysed the results.
- **Manual interventions:** none. The images are unedited model outputs.
- **Pavel:** blind scoring pending.
