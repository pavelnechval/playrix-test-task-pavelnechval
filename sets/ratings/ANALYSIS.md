# Rating round 1: 120 Cinema cards (W016)

**What was rated:** 4 sets × 3 variants × 10 cards = 120 cards. Each card got three verdicts:

- **Pavel:** 1–5, an optional comment, and one variant pick per set (`card_ratings_v1.xlsx`).
- **An external vision model:** 1–5, "players would notice" yes/no, and a one-line reason (`external/card_art_style_evaluation.md`).
- **The pipeline's own QA judge,** from each set's `summary.json`.

**Pass rule:** a rating of 4–5, or "notice = no" from the external model.

All numbers come from `rating_numbers.md`, which `pipeline/rating_report.py` generates, and from `merged.csv`, one row per card, semicolon-separated for Excel.

## Headline

- **Pavel passed 86 of 120 cards (72%); the external model passed 85 (71%).** Pavel's mean score was 3.99.
- **Every set has a variant Pavel would ship.** His picks have 70–100% of their cards rated 4–5:

| Set | Pavel's pick | Pass in the pick | External pick |
|---|---|---|---|
| Love in the City | B | 9/10 | A |
| Picture-Perfect Suburbia | A ("more consistent, even though cards in set B might be better individually") | 7/10 | A |
| Once Upon a Garden | A | 10/10 | A |
| The Lost Island | C | 8/10 | B |

- **Redo rule:** Pavel's note in every set was "3 and below". That leaves 6 cards to regenerate in the chosen variants; Once Upon a Garden A has none.
- **Compared with the benchmark:** Pavel's last benchmark (BENCH-03) passed 5 of 8 known reference objects. The tasks differ (re-drawing hidden references vs new genre objects), so the numbers are not directly comparable. Scaling from 8 test images to 120 production cards did not lower the pass rate.

## Three findings about judging

**1. Two judges, same totals, different cards.**

- Pavel and the external model pass almost the same share, but they agree on which cards pass only 64% of the time (77 of 120).
- That is barely above chance: Cohen's kappa = 0.13, and the score correlation is r = 0.03.
- **On the 14 cards 2+ points apart, the external model judged rendering only, as asked.**
  - It failed busy compositions Pavel loved, such as LI-C03 X Marks the Spot ("idea and execution are great here"), LC-B10 Love Locks and OG-A06 Beanstalk.
  - It passed clean renders Pavel failed for idea or appeal, such as LI-B01 Gold Coin ("do not see connection to set"), PP-A08 Hula Hoop and LI-A05 Conch Shell.
- **Consequence:** an AI judge can estimate how many cards pass, but it cannot choose them. The final choice of cards stays with a person.

**2. Our QA judge does not predict Pavel either.**

| Group | Cards | Pavel pass | External pass |
|---|---|---|---|
| QA passed | 110 | 73% | 75% |
| QA flagged ("accepted with issues") | 10 | 60% | 30% |
| Accepted on the 1st attempt | 75 | 72% | 75% |
| Needed 2–3 attempts | 45 | 71% | 64% |

- The QA judge and the external model share a bias: both dislike busy compositions.
- QA retries made the cards look acceptable to the AI judges, but did not change Pavel's verdict.
- **Consequence:** QA is now a gate for following the brief and for visible defects (D-022). Taste is settled by the human rating loop, which the pipeline now supports end to end: workbook, merge, redo list, before/after sheet.

**3. A simple pixel check beats the vision judge on one thing: background colour.**

- Two cards ignored their planned background: PP-A08 Hula Hoop (teal instead of orange) and LI-A04 Pineapple (red instead of green). Pavel rated them 2 and 3, and the QA judge passed both.
- A pixel test of the card's border colour (`pipeline/colour_check.py`) fails exactly those two among all 84 cards with a plain background. Two near misses get warnings only.
- It now runs after every generation, and a failure triggers a retry.

## What Pavel's ratings say about the art

**By category:**

| | C1 floating | C2 plain surface | C3 realistic surface | C4 environment |
|---|---|---|---|---|
| Pavel pass | **21/36 (58%)** | 18/24 (75%) | 21/24 (88%) | 26/36 (72%) |
| External pass | 32/36 (89%) | 16/24 (67%) | 18/24 (75%) | 19/36 (53%) |

**Pavel's 29 comments fall into six groups:**

| Theme | Comments | Examples |
|---|---|---|
| Too much detail | 6 | LC-C05 "Too detailed", OG-B06 "Overdetailed", LC-C02 "roses should be more simplistic" |
| Material doesn't read | 6 | LC-C01 "rings look like plastic more than metal", PP-B01 "does not look like cloth", PP-C03 "water does not look like water", LC-B05 steam |
| Colour or background | 6 | LI-C02 "background color blending with light", PP-C08 "different color so image would be happier" |
| Idea or readability | 5 | LI-B01 "do not see connection to set", PP-C04 "not obvious it is Casserole" |
| Scene ground or sky (C4) | 4 | LC-A06 "floating in the air instead of terrain", LI-B10 "does not always have to be blue sky? Check all given references on Miro" |
| Praise | 2 | LI-C03 "Idea and execution are great here", OG-C08 "Nice idea" |

The external model's 35 fails mostly cite detail density (17) and soft or plastic-looking materials (17); 11 cite a small or divided focal object. The two raters agree on these themes, even though they disagree on individual cards.

## Pavel's sky question: checking all the references

- **What we had:** all 36 of our scene cards (C4) had a blue sky.
- **Why:** two causes, both ours.
  - The v1 rule ("strip of setting, mostly sky") was learned from one benchmark target, the lighthouse.
  - The three C4 cards in our reference pack were all sky scenes.
- **What the full library shows:** we reviewed all 160 reference cards (111 originals plus 49 PDF crops). The game's scene cards also use parks and garden walls (gate, swing, planter), forest (tent, campfire), desert and sunset (fuel pump, ship), night (motel sign), city streets (bus, viewer), pools, underwater and stages.
- **The objects stand on solid ground.**
- **Lesson:** a rule learned from one example must be checked against the whole reference library before it applies to a whole category.

## A hypothesis we tested and rejected

- **Hypothesis:** "a warm object on a warm background" causes low scores. The assistant formed it from the low-rated C1 cards.
- **Data:** warm-on-warm cards passed 69% (20/29) against 73% for the rest. That is no real difference, so the hypothesis did not become a rule.
- **The narrower case did hold up:** an object in the same colour family as its background passed 3 of 7 times. That is now a planner warning.

## Changes made (D-022)

- **Rulebook v2:**
  - C4 stands on wide ground, with the object's natural setting as the backdrop.
  - Materials must read correctly.
  - Bold, sparse decoration.
  - Light sources don't spill onto the background.
  - Generic objects get a theme cue.
  - C1 objects have chunky silhouettes.
- **Prompt `card_v5`, QA `qa_v2`:** the QA now sees the planned background.
- **Reference pack v2:** the Tent with its forest backdrop replaces the Ferris Wheel (sky).
- **Pipeline:**
  - pixel colour check;
  - the producer's note now survives QA retries (before, a reviewer's fix replaced it after the first retry);
  - `regen` keeps the old image until a new one exists;
  - same-colour-family warning in the validator;
  - the rating loop scripts: `export_ratings.ps1`, `rating_report.py`, `redo.py`.

## Redo round 1

`redo_round1.json` lists the 6 cards. Each has the reason for the redo and the note sent to the generator. Pavel commented on only one of the six, so the other five notes are the assistant's reading of the card and are labelled as such. The sheets are `redo_round1/before_after.png` and `redo_round1/chosen_sets.png` (the four chosen variants with the new cards in place).

**Results:**

- **QA:** all 6 passed, 4 on the first attempt.
  - The Hula Hoop's first new attempt failed style (a dented tube). Its retry got the producer's note plus the reviewer's fix, which confirms the retry fix works.
  - The TV Dinner's first new attempt failed on detail.
- **Cost:** about $0.49 (QA rates unverified).
- **Pixel audit afterwards:**
  - The Hula Hoop is now orange, as planned.
  - The Storm Lantern's wall came out blue-violet: a warning, since purple was planned and blue is its neighbour on the colour wheel.
  - LI-A04 Pineapple, in a variant that was not chosen, still fails.
- **The assistant's reading before Pavel re-rates:**
  - **Clear fixes:** the Hula Hoop (orange rays, chunky tube) and the Storm Lantern (the glow stays inside clear glass, on a simple tabletop). The lantern's wall is now a duller lavender.
  - **Partly fixed:** the Shovel is chunkier with a neat sand heap, but the coin cue is faint.
  - **Modest changes:** the Balloon (smooth foil and a simple ribbon, slightly smaller in the frame), the Milk Bottle (crisper glass) and the TV Dinner (brighter yellow, tilted tray, glossier food).
- **Pending:** Pavel's re-rating of the 6 cards.
