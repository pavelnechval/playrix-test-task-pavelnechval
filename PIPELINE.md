# Card-set pipeline: architecture proposal (draft, W010)

> **Historical document.** This is the design proposal from W010–W016, kept for the record. The current workflow is in `README.md` (Russian), `pipeline/README.md` and the skill `.claude/skills/card-set/SKILL.md`. Since then: prompt v7, QA v4, plan schema 2, framing and outpainting (`reframe.py`), measurements (`card_metrics.py`), the ChatGPT route and the spend log.

Status: **v1 implemented in W012** (D-020). Code: `pipeline/cardgen.py`. Rules: `pipeline/rulebook.md`. Prompts: `pipeline/prompts/`. Skill: `.claude/skills/card-set/SKILL.md`. The sections below remain the design rationale. In v1 the QA judge is `gemini-3.8-flash`, scripted, rather than the agent, so runs are reproducible; the agent still does a final visual review (skill step 5).

**v2 (W016, D-022), after the first rating round of 120 cards:**

- **Rules and prompts:** rulebook v2, prompt `card_v5`, QA `qa_v2` and reference pack v2. W018 moved them to prompt `card_v6` and QA `qa_v3`, plan schema 2 (the set bible) and `setcheck`; see D-024.
- **New checks:**
  - a pixel check of each card's background colour against the plan (`colour_check.py`);
  - a validator warning when an object and its background share a colour family.
- **Producer notes** now stay in every retry.
- **A human rating loop** after the run: workbook → `rating_report.py` → redo list → `redo.py` → before/after sheet.

The main lesson changes step 4 below. The QA judge is a gate for following the brief and for visible defects, not a proxy for the designer's taste: on 120 cards its pass did not predict Pavel's. So the designer's role is choosing a variant and rating the cards, and the rating feeds the next round.

## What a game designer does

```
/card-set "Cinema: Western" --variants 3 --wishes "cosy, not violent; more props than locations"
```

In Claude Code (the skill) or the same command line. The designer receives:

- 3 set variants, each with 10 card illustrations;
- a contact sheet per variant;
- one overview sheet;
- a run log.

The only human step is choosing a variant.

## Steps

| # | Step | Who / which model | Output | What it enforces |
|---|---|---|---|---|
| 1 | **Plan** the set variants | Claude, following the set rulebook (from the analysis) | `plan.json`: 10 cards per variant, each with object, defining features, main colour, category, background colour and pattern, context cue | 10 distinct objects that read as the sub-theme; all 4 categories; varied silhouettes; neighbouring cards in different background colours; theme motifs for category-1 patterns; no IP, text or characters |
| 2 | **Check the plan** | Script | Errors or OK | Category coverage, duplicates, forbidden words (brands, film titles), colour rhythm |
| 3 | **Generate** each card | Nano Banana 2.1 (default; GPT Image optional after BENCH-03) with the current best prompt (v3+) and a per-category reference pack | One image per card | Art-style rules from BENCH-01–03 |
| 4 | **QA** each card | Claude vision with a rubric distilled from Pavel's notes (blind scoring matched Pavel 8/8 in BENCH-01), plus simple pixel checks (aspect, crop) | Pass, or fail with a reason | Category, contrast, detail level, warmth, no text or frames, readable at 66 px |
| 5 | **Retry** failed cards | Generator plus a targeted fix sentence, at most 2 retries | Replacement image | Keeps the cost of a run bounded |
| 6 | **Present** | Script | Contact sheets laid out as the game's 5×2 set window; PNGs at 430×480 (2× optional) | Ready to drop into the Miro templates |
| 7 | **Log** | Script | `runs/<id>/`: plan, prompts, responses (redacted), QA verdicts, cost, time | Transparency for Miro and reproducibility |

## Costs (measured)

Nano Banana 2.1 ≈ $0.055 per image with 12 references. One variant with retries ≈ 13 images ≈ $0.70, so 3 variants ≈ $2.

## Open questions for Pavel

1. Pick the 3 Cinema genres, or let the planner propose 5 and choose?
2. Final export size: 430×480 like the originals, or 2× for retina?
