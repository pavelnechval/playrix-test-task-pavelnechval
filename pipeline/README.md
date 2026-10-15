# cardgen: collectible-card set generator

Give it a set theme and free-form wishes. It returns 3–5 alternative 10-card sets of illustrations in the reference art style, already quality-checked, as 430×480 PNGs plus contact sheets.

## Quick start (game designer)

1. **One-time setup:** run `python prepare.py` in the repository root (`python3` on macOS and Linux). It creates `.venv` with the dependencies, asks for the Gemini key if there is none (saved to the git-ignored `.env`), checks access for free and offers a $0.1 one-card test. Or by hand:
   - Install Python 3 and Pillow (`pip install pillow`); tested with Python 3.14 and Pillow 12.3.
   - Create the user environment variable `GEMINI_API_KEY`. On Windows: Start → "Edit environment variables for your account" → New.
   - On macOS or Linux, in the repository folder: `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`, `export GEMINI_API_KEY="..."`.
     - Start Claude Code (`claude`) from that same terminal, so it inherits the key.
     - Tested on Windows only; the core pipeline uses only Python and Pillow and is meant to run on macOS and Linux too.
2. **The easy way:** open this folder in Claude Code and say, for example (Codex works too: `AGENTS.md` points it to the same skill):
   > Make a card set for the Cinema collection: "Love in the City", romantic comedy. Wishes: cosy, lots of hearts, no food. 3 variants.

   The `card-set` skill (`.claude/skills/card-set/SKILL.md`) does everything: it plans the set by the rulebook, then validates, generates, checks, retries and shows the sheets.
3. **The manual way:** write `sets/<slug>/plan.json` (schema in `rulebook.md` §6), then run:
   ```
   python -I pipeline/cardgen.py validate sets/<slug>/plan.json
   python -I pipeline/cardgen.py run sets/<slug>/plan.json
   ```
4. **Look at the results:**
   - `sets/<slug>/sheets/overview.png`: all variants;
   - `variant_<X>.png`: one variant as a 5×2 set window;
   - `final/`: the PNGs to place in the set templates;
   - `summary.md`: status and cost. Its "Estimated cost" line adds generation and QA (from the attempt files) to the other paid calls in `costs.jsonl` (background extension and vision measurements), without counting anything twice. The scripts refresh it as they run.
   - A card marked `unchecked` has no QA verdict, for example because the QA call failed. It is never counted as passed.
5. **Fix single cards** without touching the rest:
   ```
   python -I pipeline/cardgen.py regen sets/<slug>/plan.json B04 --fix "make the balloon string pink"
   ```
   - The new image is framed like the rest of the set, once the set has been framed (step 9), and the sheets are rebuilt.
   - Every attempt stays in `cards/<id>/`. To bring an earlier one back:
     ```
     python -I pipeline/cardgen.py choose sets/<slug>/plan.json B04 try2
     ```
   - **Empty balance:** if the Gemini balance runs out (HTTP 402), every script stops with a message saying so and leaves finished cards as they are. Top it up in AI Studio and run the same command again.
6. **Rate and redo** (the human taste loop). Steps 2 and 3, the Excel workbook, are optional and need Excel on Windows. Without them, for example on macOS, the designer gives scores and comments in the conversation, and the agent writes the redo list (`sets/ratings/redo_roundN.json`) for step 5 directly.
   1. Make the rating pack: thumbnails, plus sheets and a request for an optional external model.
      ```
      python -I pipeline/review_pack.py sets/ratings sets/<slug>/plan.json [more plans]
      ```
   2. Build the rating workbook: a 1–5 dropdown, comments and set picks per card.
      ```
      powershell -ExecutionPolicy Bypass -File pipeline/build_rating_workbook.ps1 -Manifest sets/ratings/manifest.json -Out sets/ratings/card_ratings_v1.xlsx
      ```
   3. After rating, export the ratings.
      ```
      powershell -ExecutionPolicy Bypass -File pipeline/export_ratings.ps1 -Path sets/ratings/card_ratings_v1.xlsx -OutJson sets/ratings/pavel_ratings.json
      ```
   4. Merge them with the external ratings and the QA verdicts. This writes `rating_numbers.md` (picks, agreement, redo list) and `merged.csv`.
      ```
      python -I pipeline/rating_report.py sets/ratings/pavel_ratings.json <external table .md> sets/ratings sets/<slug>/plan.json [more plans]
      ```
   5. Regenerate the redo list (one note per card) and get a before/after sheet to re-rate.
      ```
      python -I pipeline/redo.py sets/ratings/redo_round1.json
      ```
   6. Audit the background colours of a finished set (pixel check, free).
      ```
      python -I pipeline/colour_check.py sets/<slug>/plan.json
      ```
7. **Check and show the set as a whole** (set guidelines):
   - Measure the finished set against the checklist; this writes `setcheck.md`.
     ```
     python -I pipeline/cardgen.py setcheck sets/<slug>/plan.json
     ```
   - Lay a variant into its template, as players see it; this writes `sheets/window_<X>.png`.
     ```
     python -I pipeline/set_window.py sets/<slug>/plan.json B
     ```
8. **ChatGPT route** (optional, second image model, on your ChatGPT plan via the Codex command line). It uses the same card text and writes to `sets/<slug>/gpt/`. Squares are fitted to card shape by extending the background, not by cutting the sides.
   ```
   python -I pipeline/codex_images.py run sets/<slug>/plan.json B
   ```
9. **Standardise size and breathing room, and measure** (the final pass, W019):
   - Reframe the cards so each object has the reference median size for its category and the reference margins; use `--route gpt` for the ChatGPT route.
     ```
     python -I pipeline/reframe.py sets/<slug>/plan.json --route gemini
     ```
     - Where the card window runs past the generated picture, the image model continues the background outward (outpainting, about $0.035 per card). The original pixels are kept, and a seam check falls back to stretching the edge if the model moved the picture (W022). `--fill stretch` makes no calls.
     - It rebuilds the variant sheets from the framed cards.
     - After looking at the cards, set any framing override with its reason. It is stored in `sets/<slug>/framing.json` and holds only for the image it was made for.
       - A hand-set box (y0,x0,y1,x1 on a 0–1000 scale of the generated image), for a scene whose subject is more than the box the vision model found. It needs no API call.
         ```
         python -I pipeline/reframe.py sets/<slug>/plan.json --route gemini --override C10 --box 0,0,940,1000 --why "the hammock with its palm trees"
         ```
       - `--fill stretch`, or a saved outpaint attempt such as `C05.try2.model.png`, overrides how the background is extended.
       - `--clear-override C10` removes an override.
   - Measure the cards against the reference norms and print the flags.
     ```
     python -I pipeline/card_metrics.py plan sets/<slug>/plan.json
     python -I pipeline/card_metrics.py report sets/<slug>/plan.json
     ```
   - Turn the flags into correction notes for `regen` or the ChatGPT route's `--fixes`.
     ```
     python -I pipeline/card_metrics.py fixes sets/<slug>/plan.json
     ```

## What happens inside

```
theme + wishes
  → plan.json            (agent; rules: rulebook.md)
  → validate             (10 cards, all 4 categories, colour rhythm, no IP, text or people)
  → per card:
      generate           (Nano Banana 2.1 + 12 reference cards + prompt card_v7)
      → QA               (gemini-3.8-flash + rubric qa_v4: subject, category, clean, framing, colour, detail, style)
                         + pixel check of the background colour family (colour_check.py, categories 1-3)
      → retry up to 2×   with the reviewer's fix sentence (added to any producer note, never replacing it)
  → export 430×480 + contact sheets + summary (cost, attempts, verdicts)
  → human rating → rating_report → redo list → redo.py → before/after sheet
```

The QA judge enforces the brief and catches visible defects. Taste is settled by the human rating loop: in the Cinema round, the judge's pass did not predict Pavel's (W016).

**Per card, every attempt is kept with:**

- its exact prompt;
- the reference hashes;
- the redacted API response;
- the QA verdict.

**Cost:** about $0.06 per image plus about $0.005 per QA call, so about $2–3 for a 3-variant set. **Time:** about 5–10 minutes with 4 parallel workers.

## Files

| File | Purpose |
|---|---|
| `rulebook.md` | Set-design and art rules, each with its source |
| `set_guidelines.md` | What makes a set good; the planner's checklist |
| `prompts/card_v7.md` | Generation prompt template (older versions are kept for the cards made with them) |
| `prompts/qa_v4.md` | QA rubric; v4 also sees the card's planned context cue (older versions are kept likewise) |
| `set_window.py` | Lays a variant into the brief's set template (window colour, title, names, stars) |
| `codex_images.py` | ChatGPT route: the same cards through Codex's image tool |
| `set_palette.py` | Backdrop-colour profile of reference sets and ours |
| `card_metrics.py` | Object size, margins, room above, detail lost at card size and category, against reference norms |
| `reframe.py` | Standardises object size and breathing room to the reference norms (crop, or extend the background by outpainting) |
| `compare_routes.py` | Blind side-by-side of the Gemini and ChatGPT versions of a plan |
| `refs_production.json` | The 12 reference cards sent with every generation |
| `cardgen.py` | CLI: validate / run / regen / choose / sheets / summary / setcheck |
| `costs.py` | Spend log (`costs.jsonl` per set) and the price assumptions |
| `colour_check.py` | Pixel check of the background colour family against the plan |
| `review_pack.py`, `build_rating_workbook.ps1` | Rating pack: thumbnails, external-model sheets, Excel workbook |
| `export_ratings.ps1`, `rating_report.py` | Read the filled workbook; merge with external ratings and QA |
| `redo.py` | Regenerate a redo list with producer notes; before/after sheet |
| `gemini_image.py`, `openai_image.py`, `keys.py`, `sheets.py` | API clients (standard library only), key reader, sheet builder |

The reference images (`references/`) belong to the hiring company and are not part of a public repository.
