# BENCH-02 result

Run: 2026-10-13, evening (W007). Script: `bench.py`. Prompt: `prompt_v2.md`.

## Setup

| Item | Value |
|---|---|
| What changed vs BENCH-01 | Prompt v2 (rules from all BENCH-01 feedback) and reference pack v2 (12 Miro originals, 3 per category, chosen to show those rules). Both changed together, so this measures their combined effect |
| Unchanged | Hidden targets, subject text, model (`gemini-nano-banana-2.1`), 1:1, 1K, thinking at default |
| Samples | 2 per target (a, b) to check consistency: 8 images, all kept, no retries |
| Comparison | `sheets/compare_large.png` and `sheets/compare_card_size.png`: real \| BENCH-01 v1 output \| v2-a \| v2-b |

## Cost and time (from API usage)

- 8 images, about 14.3k input tokens each (12 references), **≈ $0.44 total (≈ $0.055/image)**, average 23.2 s.
- Each call costs about $0.007 more than BENCH-01 because there are 4 more references.

## Assistant review

Not blind: v1 and v2 are labelled on the sheet.

| Target | v1 problem (BENCH-01 notes) | v2-a / v2-b | Style a / b |
|---|---|---|---|
| T1 Bottle (C1) | Blue on blue, droplets and mesh | Fixed: orange rays (complementary), floating, tilted. Still more moulded detail (ridges, stripes) than the very simple reference bottle | 4 / 4 |
| T2 Tea Cup (C2) | Wooden table read as category 3; colours blended | Fixed: plain one-colour surface and wall in one colour family (blue / teal) behind a red cup; soft steam. A tea-bag tag on (a) is a small extra detail | 4 / 4 |
| T3 Bumpers (C3) | Busy background (string lights, barrier) | Fixed: glossy floor with a mirrored reflection; simple rays centred behind | 4 / 4 |
| T4 Lighthouse (C4) | Small in frame; busy cliff, waves and sky | Fixed: low angle, large, only a hint of grass, clean sky with puffy clouds. At card size it is very close to the real card | 4 / 4 |

**Summary:**

- **Style mean: 4.0 (v1: 3.75).** It meets the ≥4 decision threshold, but only just.
- **Consistency:** both samples of each target follow the same rules, with similar composition and colour logic.
- **Remaining gaps:** detail level on the bottle; generic "red cup" design choices. These belong to the planner (object design and colour choices), not to rendering.

## Pavel and external-model ratings (added in W008)

Files: `scores_pavel.csv` and `scores_external_model.csv` (the external model's ratings were relayed by Pavel).

| Image | Pavel | External | Assistant (not blind) | Pavel: notice? | External: notice? |
|---|---|---|---|---|---|
| T1 v2-a | 3 | 3 | 4 | yes | yes |
| T1 v2-b | 4 | 4 | 4 | yes | no |
| T2 v2-a | 4 | 4 | 4 | **no** | **no** |
| T2 v2-b | 3 | 3 | 4 | yes | yes |
| T3 v2-a | 4 | 4 | 4 | yes | no |
| T3 v2-b | 3 | 4 | 4 | yes | no |
| T4 v2-a | 4 | 3 | 4 | **no** | yes |
| T4 v2-b | 4 | 3 | 4 | **no** | yes |

**Same model (Nano Banana 2.1), v1 → v2:**

| Rater | Style mean, v1 → v2 | Pass rate ("players wouldn't notice"), v1 → v2 |
|---|---|---|
| Pavel | 3.75 → 3.63 | 0/4 → **3/8** |
| External | 3.25 → 3.50 | 1/4 → **4/8** |
| Assistant (not blind) | 3.75 → 4.0 | — |

### Reading

- **Pass rate improved for both raters.** The prompt fixed composition and category problems.
- **Pavel's style mean held steady** while his notes moved to finer issues: warmth of the reds, steam style, cloud realism, object smoothness. As the obvious problems disappear, the subtle ones decide the score.
- **Pavel and the external model agree exactly on 5 of 8 images.** Both pass only T2 v2-a.
- **They disagree on the lighthouses.** Pavel approves the composition. The external model says the smooth tower loses the reference's crafted brick and railing detail.
- **Prompt v3 takes both points:** keep architectural detail on built structures, keep manufactured objects smooth.

### Lesson about the assistant's scoring

- In BENCH-01, scoring blind, the assistant matched Pavel on 8 of 8.
- Here, scoring without blinding, it was too generous: 4.0 against 3.63 and 3.50.
- From now on every comparison sheet is blind (BENCH-03), and the pass rate is the main measure (D-015).

## Pending

- Pavel's scores in `scores_pavel.csv` (style 1–5, plus "would players notice").
- Optionally, external-model ratings for comparison.

## Implication (proposed, D-013)

Adopt prompt v2 and the per-category reference pack as the pipeline's starting generation step. Then move on to building the pipeline: planner → generator → QA → contact sheets. Keep the bottle-detail note for the QA rubric.
