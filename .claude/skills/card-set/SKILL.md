---
name: card-set
description: Produce a ready-to-use set of collectible-card illustrations (10 cards, in 3-5 alternative variants) for a casual mobile game, in the art style of the reference cards. Use when a game designer or producer asks for a new card set, a set variant, or a remake of individual cards. Input is a set theme plus free-form producer wishes.
---

# Card set skill

You turn a set theme and free-form producer wishes into 3–5 complete variants of a 10-card set: planned, generated, quality-checked and laid out on contact sheets. The designer only chooses a variant at the end.

## Inputs to collect (ask only if missing)

- **Collection and set theme.** Example: collection "Cinema", set "Love in the City" (romantic comedy).
- **Producer wishes.** Free text: mood, objects to include or avoid, colour wishes. Defaults: warm, cosy, family-friendly.
- **Number of variants:** 3 to 5, default 3.
- **Set name.** If none is given, choose one yourself and offer two alternatives in the report (W023).

## Before you start

- **Which Python.** If the repository has a `.venv` folder (made by `prepare.py`), run every command below with its interpreter in place of `python`: `.venv/bin/python` on macOS and Linux, `.venv\Scripts\python.exe` on Windows.
- **The key.** If `python -I pipeline/gemini_image.py check` fails, ask the designer to run `python prepare.py` once (`python3 prepare.py` on macOS) and wait until it says Ready.
- **Say what it will cost.** Before generating, tell the designer the expected cost and time: about $1.5 and 15–20 minutes per variant, including framing and regens. In the two reviewer tests, 3 variants took 45–55 minutes and cost $3.3–4.6. The request itself is the go-ahead, so don't wait for a confirmation.
- **Quick demonstration.** The designer may ask to see the tool work rather than for a new theme. Then rerun an existing plan:
  1. Copy `sets/<set>/plan.json` (for example `sets/cosy-mystery/plan.json`) into a new folder `sets/<set>-demo/`.
  2. Start at step 3. Add `--variants A` to the run for a single variant (about $1.5 and 15 minutes).
  3. Say that this shows the pipeline, not the planning of a new theme.

## Steps

1. **Read `pipeline/set_guidelines.md`, then `pipeline/rulebook.md`.**
   - The set guidelines say what makes ten cards a good set: one moment, a mood, a kit of object roles, a crescendo by rarity, and a mood-led palette with a window colour. Their §5 checklist is your planning brief.
   - The rulebook holds the card and art rules, and plan schema 2 in its §6.
2. **Write `sets/<slug>/plan.json` in schema 2.** For each variant, in this order:
   1. **Set bible.** Write the `moment` (one sentence), the `mood`, a `lead_color` that expresses the mood, a `window_color` and a `motif`. Each variant takes a different angle on the theme, so each has its own moment.
   2. **The kit.** Choose 10 iconic objects that belong in that moment, covering at least 4 roles: carry, food, gear, vehicle, place, nature.
      - Mix small, medium and large objects, and give them distinct silhouettes.
      - Use the default category mix of 3 × C1, 2 × C2, 2 × C3, 3 × C4.
      - Use no brand names, film titles, characters or text.
      - **Producer wishes come before these defaults.** For example, "more objects than locations" means at most one place card per variant, category 4 scenes that show an object in its surroundings (a rocket on its pad, a rover on a dune), and a 3/2/3/2 mix if needed. Keep all four categories. Note in `plan.json` and in the report which defaults you changed and why.
      - **Category 3 surface:** prefer a wooden or textured tabletop or a podium. A plain glossy floor is often measured as category 2.
      - **No ground (space, underwater, sky):** ships and stations float as category 1. A category 4 scene stands on a planet surface, a deck or the sea floor. Open space counts as a night scene in saturated blue.
   3. **The crescendo.** Give stars 1, 1, 2, 2, 3, 3, 4, 4, 5, 5 and order the cards by stars: small props first, then signature items, then the big places and the most iconic objects, ending on the climax.
      - Small doesn't mean generic. Every common must pass the name test on its own: Sandcastle, Diving Mask, Grad Cap, not pancakes or a handbag.
   4. **The palette.** Put the lead colour on 3–5 cards. Use 5–6 colour families in total, with at most 2 same-colour neighbours in the 5×2 window (cards 1–5 above 6–10).
      - Keep the light sunny, with at most 2 sunset or night cards, used deliberately.
      - Give each card one charming detail, and put the motif into 1–3 C1 backgrounds or details.
   5. **Names:** 1–2 words, with one or two playful ones.
3. **Validate:** `python -I pipeline/cardgen.py validate sets/<slug>/plan.json`. Fix the plan until it prints `Plan OK`. Treat warnings as design questions and answer them in the plan. The validator also warns when a card repeats the object of a finished set in the collection (for example a second scooter); the QA judge can't see other sets.
4. **Generate:** `python -I pipeline/cardgen.py run sets/<slug>/plan.json`.
   - The command generates each card with Nano Banana 2.1 and the 12 production reference cards.
   - A vision model checks each card, and a pixel check confirms the planned background colour. Failed cards are regenerated with the reviewer's fix sentence, up to 2 retries.
   - Finished cards are skipped, so it is safe to re-run after an interruption.
   - Cost: about $0.06–0.10 per card for generation and QA. Time: about 10 minutes.
   - A whole 3-variant run by the skill, with framing, measuring and regens, took 45–55 minutes and cost $3.3–4.6 in the two reviewer tests (W023, W030).
5. **Frame, measure, set check, then review.**
   - Run `python -I pipeline/reframe.py sets/<slug>/plan.json --route gemini`. It gives every card the reference cards' object size and breathing room, measured on the 160 originals. Models draw objects at uneven sizes, so this step standardises them without regenerating anything.
     - Where a card needs more background than the model drew, the image model extends it (outpainting, about $0.035 per card); the drawn picture itself is kept.
     - It rebuilds `sheets/variant_<X>.png` from the framed cards, so the review below sees what the set window will show.
     - Check the scene cards. If the vision box missed part of the subject (a hammock without its palm trees), set the box by hand: `python -I pipeline/reframe.py sets/<slug>/plan.json --route gemini --override <card id> --box y0,x0,y1,x1 --why "<reason>"`.
       - The box is on a 0–1000 scale of the generated image.
       - `--fill stretch` (or a saved attempt file such as `A06.try2.model.png`) overrides how the background is extended.
       - `--clear-override <card id>` removes an override.
       - A hand-set box needs no API call.
   - Run `python -I pipeline/card_metrics.py plan sets/<slug>/plan.json`, then `... report sets/<slug>/plan.json`.
     - It flags cards whose size, margins, room above or fine detail fall outside the reference norms, and cards whose composition reads as a different category.
     - `card_metrics.py fixes` turns the flags into correction notes for `regen`. It leaves out size and room flags on framed cards, because framing sets those, not the drawing.
   - Run `python -I pipeline/cardgen.py setcheck sets/<slug>/plan.json`. It measures the finished backdrops against the plan and the reference ranges, and writes `setcheck.md`.
   - Then look at each `sheets/variant_<X>.png` (in star order) and judge the visual checklist items yourself:
     - Can you name the set from any three cards?
     - Is it one world?
     - Does the mood come through?
     - Is the motif visible?
     - Does it overlap with the collection's other sets?
   - Also read `summary.md`.
   - **Your review is the set-level check.** QA judges one card at a time. In the first autonomous run, QA passed all four problems that the sheet review caught: an orchestra triangle, a teapot look, a treasure chest overlapping another set, and a motif that read as orange slices.
   - For any card that still looks wrong, run `python -I pipeline/cardgen.py regen sets/<slug>/plan.json <card id> --fix "<one precise sentence>"`.
     - A regen makes up to 2 paid attempts (about $0.12). It replaces `final/<id>.png` with the best new attempt, frames it like the rest of the set and rebuilds the sheets.
     - Compare the new attempt with the earlier ones in `cards/<id>/`. To make any other attempt final: `python -I pipeline/cardgen.py choose sets/<slug>/plan.json <card id> try<n>`.
     - After regens or `choose`, run `card_metrics.py plan` and `report` and `cardgen.py setcheck` again, so the report describes the final images.
     - `card_metrics.py`'s category reading is a model estimate. A category 3 card on a real surface that reads as category 2 is a judgement call: decide by eye and say so in the report.
   - If the problem is the object choice itself, change that card in the plan first.
   - Lay each variant into its template: `python -I pipeline/set_window.py sets/<slug>/plan.json <X>`. Look at `sheets/window_<X>_preview.jpg` as a player would see the set. The "+2" badges, the 8/25 bar and "Set 4/10" are the template's game UI from the brief, not part of your cards.
6. **Report to the designer:**
   - the windows and one line per variant (concept, strongest cards, weak spots);
   - the cost: the "Estimated cost" line in `summary.md`. It covers generation, QA, background extension and the vision measurements;
   - where the final 430×480 PNGs are: `sets/<slug>/final/`.
   - Recommend one variant, but let the designer choose.
   - Once the designer has chosen, assemble the deliverable: `python -I pipeline/assemble_final.py sets/<slug>/plan.json <X> --from final`.
     - Use `--from gpt/final` for the ChatGPT route, and `--override <card>=<folder>` for single cards.
     - It writes `final_set/` with `sources.json` and the set window.
   - Only if the designer asks for a second image model: `python -I pipeline/codex_images.py run sets/<slug>/plan.json <X>`. It uses ChatGPT through the Codex command line, with the same card text, and writes to `gpt/`.
     - Then run `python -I pipeline/reframe.py sets/<slug>/plan.json --route gpt`, and `python -I pipeline/compare_routes.py sets/<slug>/plan.json` for a blind side-by-side.
     - The ChatGPT plan allows about 50 images per usage window (W019); Codex reports the reset time.
7. **Rating loop,** when the designer wants to rate. The commands are in `pipeline/README.md`, step 6.
   1. Build the rating workbook, plus an optional external-model pack. The workbook needs Windows and Excel. Without them, for example on macOS, ask the designer for scores and comments in the conversation and go straight to step 3.
   2. After rating, export the ratings and run `rating_report.py`.
   3. Write `sets/ratings/redo_roundN.json` from the designer's own redo rule (for example "3 and below in the chosen variant"). Give each card one precise note.
      - Where the designer left no comment, say in `reason` that the note is your reading, not theirs.
      - If a note contradicts the card's brief, edit the brief in `plan.json` first.
   4. Run `redo.py`, then show the before/after sheet for re-rating.
   5. Put recurring lessons into `rulebook.md` (with the source) and into the prompts, but only when the ratings support them. Test a hypothesis on the data before turning it into a rule.

## Rules

- Requires the environment variable `GEMINI_API_KEY`. Never print, log, commit or paste API keys.
- If a command stops with "The Gemini API balance is empty", stop and tell the designer to top it up in AI Studio. Nothing is lost: finished work is kept, and re-running the same command continues. Don't work around it with hand-made boxes or stretched backgrounds unless the designer asks for that.
- The reference images in `references/` are licensed assets of the hiring company. Use them only as generation references; never publish them.
- Keep every attempt. `cards/<id>/try*` are never deleted; the logs are part of the deliverable. Reports (sheets, `summary.*`, `setcheck.md`) are rebuilt by the scripts, so copy one first if you need to keep that version.
- Don't claim a card passed if `summary.md` says `accepted_with_issues`. Say what is still wrong.
- A QA pass is not the designer's approval. In the Cinema round, the QA judge did not predict the designer's ratings, so never present QA results as a quality verdict.
