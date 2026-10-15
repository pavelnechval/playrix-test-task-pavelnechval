# Work log: Playrix AI-pilled producer test

Chronological record of prompts, actions, results and decisions. It exists so the process can be shown on Miro and explained in interviews.

- Decisions: `DECISIONS.md`. Status "proposed" means an assistant suggestion; "accepted" means Pavel confirmed it.
- Experiments: `experiments/<RUN-ID>/`, holding the plan, exact prompts, all outputs and the result.
- Rules (from the README "Working agreement"): save prompts before sending them, keep failed outputs, never invent costs, times or scores, and record every manual intervention.

## Earlier sessions (Codex, folder `D:\JOB2026HUNT\AI-PILLED`)

- **W001, 2026-10-07**: reviewed the brief. Wrote requirements and open questions to README.md and drafted prompt library v0.1 (PROMPTS.md, never executed). Full entry: `D:\JOB2026HUNT\AI-PILLED\WORKLOG.md`.
- **W002, 2026-10-09**: recorded Nico's suggested route (GPT for reference matching, Nano Banana for iteration) as a hypothesis. **GPT-001**: one image that recreated the blue-bottle reference while the reference was visible. Subject, palette and floating composition were right, but the result was glossier and more sculpted than the reference. Not approved as a style anchor. Now copied to `experiments/GPT-001/`, with `output.png` as a copy of the original Codex output path given in result.md.

README.md and PROMPTS.md in this folder are identical copies of the AI-PILLED files (file hashes matched on 2026-10-13).

---

## 2026-10-13 / W003 / Kickoff in PLAYRIX_PRODUCER (Claude Code, Opus 5.5)

### Pavel's prompt (verbatim)

> Read the attached test assignment PDF and folder and help me get started. Summarize the deliverables and main challenges, then suggest 2–3 practical approaches with their tools, trade-offs, and likely effort. Recommend one approach and a small first experiment. Keep it concise, ask only essential questions, and track our prompts, decisions, and results so I can explain the process.

### Actions

- Re-read the 9-page brief, README.md, PROMPTS.md, the AI-PILLED log and GPT-001.
- Measured the reference images embedded in the PDF with Python and Pillow (read-only; earlier extractions are in `D:\JOB2026HUNT\tmp\pdfs\ai-pilled-brief\`).
- Zoomed 2–3× into the category examples (brief pp. 3–4), card-sheet rows (p. 6), a set screenshot (p. 7) and the final-set templates (p. 8).
- Checked current image models on the web (sources below).
- Created this log, DECISIONS.md and `experiments/BENCH-01/plan.md`. Copied GPT-001 into `experiments/GPT-001/`.
- Generated no images, called no APIs, published nothing and spent no money.

### Findings

1. **Reference resolution is the binding constraint.** The "Только карточки" sheet is embedded at 733×1312 px, so each card is ≈60×66 px (W:H ≈ 0.91). The earlier `render-*.png` files are upscales of the same pixels. As a result, a style LoRA can't realistically be trained from the PDF, and image models get only weak style evidence. Full-resolution originals from Miro would be the biggest single quality lever.
2. **Aspect ratio.** GPT-001 requested 4:5 (0.80), but the reference art measures ≈0.91 (D-005).
3. **Structure.** The sheet has 16 rows × 10 cards, matching the brief's 16 sets × 10 cards. Rows 1, 2, 5, 6, 7 and 13 have no character cards; all 10 are objects. The p. 8 templates show 10 regular slots. A gold-free set of 10 object cards therefore has direct precedent (D-004).
4. **Label errors in the category examples.** On p. 3, Cat 2 "Lifeguard Tower" shows sunscreen and sunglasses. On p. 4, Cat 4 "Sunblock" shows a lifeguard tower, so those two labels are swapped. Cat 2 "Risotto" shows a potted citrus tree. Choose references by image content, not by label, and mention this in the analysis frame.
5. **A gold frame doesn't mean a character card.** Cat 4 "Coaster" is an object card with 5★ in a gold frame. We read "no gold cards" as "no character/story (category 5) art".
6. **Preliminary style and set observations (low resolution; verify later):**
   - Backgrounds come from a small vocabulary: radial rays, stripes, flat gradients, thematic repeat patterns (for example, π signs behind the calculator) and simple rooms or outdoor scenes for categories 3–4.
   - Neighbouring cards in a set rarely share a background colour.
   - Objects are chunky, saturated, softly shaded and centred with clear margins.
7. **Current models (web check on 2026-10-13; verify IDs before use):**
   - Google: Nano Banana 2.1 `gemini-nano-banana-2.1` (stable, up to 14 reference images, per Google docs) and Nano Banana Pro `gemini-3-pro-image`.
   - OpenAI: GPT Image 2 `gpt-image-2`, from third-party listings. A GPT Image 2.5 from Sep 2026 is reported but not verified in OpenAI docs.
   - Others: FLUX.2 / FLUX Kontext and Seedream.
   - Game-art platforms with style training: Scenario, Layer.ai and Leonardo.

### Options presented to Pavel

- A. Agent skill plus hosted image APIs: ~4–6 days.
- B. ComfyUI plus a trained style LoRA: ~7–10+ days, high risk.
- C. Game-art platform or no-code flow: ~3–5 days.

Effort figures are rough assistant estimates, not measurements. Recommended: A, starting with a benchmark.

### Decisions (all proposed; see DECISIONS.md)

- D-001: approach A.
- D-002: run a benchmark before building.
- D-003: leave-one-out test design.
- D-004: scope of 3 sets × 10 object cards.
- D-005: aspect ratio ≈0.91.
- D-006: a variant is a full alternative set.

### Questions sent to Pavel

1. What is the submission deadline?
2. Which image-model access is available, and what is the budget cap?
3. Can the original card images be downloaded from the Miro board?

### Explain it simply

Before building anything, we measured what the references can give us: 60-pixel thumbnails. That rules out training a custom model on them for now. The plan is to build an agent skill around a hosted image model. We pick that model with a blind test: it draws real cards it has never seen, and we compare them with the originals.

### Sources

- Google, Nano Banana 2.1 model page: https://ai.google.dev/gemini-api/docs/models/gemini-nano-banana-2.1
- GPT Image 2 listing (third-party): https://openrouter.ai/openai/gpt-image-2
- GPT Image 2.5 report (third-party, unverified): https://www.imagine.art/announcements/chatgpt-images-2-5
- Reference-consistency comparison (vendor blog): https://sorceress.games/blog/ai-character-generator-stay-on-model-with-reference-images-2026
- Game-art platform ranking (third-party): https://knowara.com/?p=2424

---

## 2026-10-13 / W004 / Go decision, connections and BENCH-01 setup

### Pavel's prompt (verbatim, API key redacted)

> Main challenges - Matching the style from thumbnails - we can use Miro skill to check my copy https://miro.com/app/board/uXjVEdsb-i4=/, it should have higher resolution pictures which would unblock this challenge.
>
> Agent skill + image APIs - yes, let's go with this approcach. We will use Claude Code + Nano Banana 2.1 (I have google AI subscription - let me know how to connect it for this assignment).
>
> Let's start with first experiment.
>
> What's the deadline? - 3 days, but I have enough time on my hands.
> Which image-model access do you have, and what's your budget cap? Gemini, API key [REDACTED: never stored in project files] (image attached)
>
> Can you download the original card images from the Miro board? Let's try accessing Miro with my account and connecting to board I linked

The attached screenshot showed the AI Studio key dialog with the key itself. The key was not copied into the project. (Key name and project number removed from this log before the repository was shared, W023.)

### Facts recorded

- Deadline: 3 days from 2026-10-13, so about **2026-10-16**.
- Budget: no cap given yet.
- Pavel's Miro copy of the board: https://miro.com/app/board/uXjVEdsb-i4=/

### Actions

- **API key:** did not use or store the key pasted in chat. Asked Pavel to set it himself as the user environment variable `GEMINI_API_KEY`, and recommended rotating it, since it now appears in the chat and in a screenshot (D-007).
- **Miro:** found the official Miro connector (`https://mcp.miro.com/`) in the connector registry and showed Pavel a Connect button (D-009).
- **Gemini docs (read 2026-10-13):**
  - The image-generation docs now use the Interactions API (`POST /v1beta/interactions`).
  - Nano Banana 2.1 accepts up to 14 reference images. Outputs carry a SynthID watermark.
  - From the pricing page: these image models have **no free API tier**.
  - Per-image output prices: Nano Banana 2.1 $0.0336 (1K) / $0.0504 (2K) / $0.113 (4K). Nano Banana Pro $0.134 (1K/2K). The Batch API costs half.
  - The pricing page does not say that a Google AI Pro/Ultra subscription covers API calls.
- **Code (D-008):**
  - `pipeline/gemini_image.py`: Gemini client using only the standard library; reads the key at runtime and never logs it.
  - `pipeline/refs_from_sheet.py`: grid cropper.
  - `pipeline/sheets.py`: comparison sheets.
  - `experiments/BENCH-01/prompt_v1.md` and `bench.py`: the experiment (prepare / run / sheets).
- **Free dry run:** ran `bench.py prepare` with no API calls.
  - 160 reference crops written to `references/pdf_v0/cards/`.
  - Style pack and hidden targets checked visually: `experiments/BENCH-01/sheets/refs_overview.png`.
  - Expanded prompts saved: `experiments/BENCH-01/prompts/T1-T4.md`.
- **Plan refinement (D-003):** the category-3 target changed from Coffee Pot to Bumpers. All four hidden targets are now official category examples with clean ground truth on the p. 6 sheet.
- **Status check:** `GEMINI_API_KEY` not set yet; Miro connector not connected yet.

### Results

BENCH-01 is fully prepared. It is waiting for the key; the Miro originals are optional for the first run. No images generated, nothing spent.

### Decisions

- Now accepted: D-001 (approach A with Nano Banana 2.1) and D-003 (leave-one-out).
- D-002: benchmark-first is accepted; adding a Nano Banana Pro comparison arm is proposed.
- New, proposed: D-007 (key handling), D-008 (REST client using only the standard library), D-009 (Miro connector) and D-010 (3-day schedule).

### Explain it simply

We set up the experiment so it can be repeated exactly. The prompt and reference images are saved before every call. The model never sees the four cards it has to draw, so we can put its drawings next to the real cards and judge honestly.

---

## 2026-10-13 / W005 / Miro originals

### Pavel's prompt (verbatim)

> Use Miro for this

Context: Pavel had just connected the official Miro connector with his Miro account. "This" refers to getting higher-resolution reference images from his copy of the board.

### Actions

- **Read the board structure** (read-only; nothing on the board was changed).
  - Four frames:
    - "Примеры карточек" (162 items)
    - "Пример коллекции" (19)
    - "Фрейм для описания хода работы и результатов" (7)
    - "Анализ принципов составления коллекций (идеи / арт)" (2)
  - Three text blocks holding the brief.
  - 180 images in total.
- **Mapped all 160 card images** in "Примеры карточек" to the same row/column grid as the PDF p. 6 sheet: `references/miro_v1/board_map.json`.
- **Downloaded 13 originals** using the connector's signed links (`image_get_url`): the 12 BENCH-01 cards plus one probe (r01c01).
  - Each is a 430×480 px PNG, fully opaque, with an original file name like `CardC6_card_NN.png`.
  - Provenance is recorded in `references/miro_v1/cards/manifest.json`. The temporary URLs are not stored.
  - Download script: `pipeline/fetch_images.py`.
- **Benchmark update:** `bench.py` now takes `--refs miro_v1` (the default) or `--refs pdf_v0`. Re-ran the free `prepare` step for both sets and checked the Miro set visually: `experiments/BENCH-01/sheets/miro_v1/refs_overview.png`.
- **Status check:** `GEMINI_API_KEY` is still not set, so no images were generated and nothing was spent.

### Findings

1. The Miro originals are **430×480 px**, about 7× the linear resolution of the PDF crops (≈60×66). The exact card aspect is **0.896** (D-005 updated).
2. Full resolution shows a richer background vocabulary than the thumbnails did:
   - concentric rings (graduation cap, mojito)
   - wavy pattern (fan)
   - radial rays (popsicle, bottle)
   - vertical stripes (beach bag)
   - wooden tabletops and desks (fruit plate, computer)
   - outdoor scenes (field ball, coaster, lighthouse)
   This feeds the style rulebook.
3. The board's card grid has the same order as the PDF sheet. All 12 benchmark cards were confirmed visually.

### Decisions

- D-009 is accepted and done.
- D-005 is refined.
- New, proposed: D-011, Miro originals as the reference library and the default for BENCH-01, with PDF crops kept only as a comparison.

### Next

- Pavel sets `GEMINI_API_KEY`.
- Then: a free key check and BENCH-01 on Miro references (8 images).
- In parallel: fetch the other 147 originals for the analysis and rulebook.

### Explain it simply

The PDF only had tiny thumbnails. Through the Miro connector we got the original card files at seven times the resolution, so the model now learns the style from the real artwork rather than from blurry previews.

---

## 2026-10-13 / W006 / BENCH-01 run

### Pavel's prompt (verbatim)

> Go

This approved the plan from W005: a free key check, then BENCH-01 with both arms (8 images, under $1), then downloading the remaining Miro cards.

### Actions

- **Key check:** `GEMINI_API_KEY` found in Pavel's user environment (read from the registry; never printed). Ran `gemini_image.py check`, a free call:
  - The key works and 62 models are visible.
  - Present: `gemini-nano-banana-2.1`, `gemini-3-pro-image`, `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image`, `gemini-2.5-flash-image`.
- **BENCH-01, Nano Banana 2.1 arm** (4 calls, run in the background).
  - The first responses confirmed the Interactions API format: one `thought` step plus one `model_output` image (1024×1024 JPEG).
  - Image extraction works as intended. No retries were needed.
- **BENCH-01, Nano Banana Pro arm** (4 calls): all succeeded.
- **Miro downloads** in parallel: 61 of 160 originals are now local; 99 are still to fetch. One `image_get_url` call (r06c06) failed on Miro's side and will be retried.
  - Finding: the signed links expire about 15 minutes after they're issued, so each batch is downloaded immediately.
- **Scoring:** built blind sheets and the score template (`bench.py sheets`). The assistant scored blind before opening `blind_key_miro_v1.json`. Wrote `experiments/BENCH-01/result.md`.

### Results (details in result.md; Pavel's blind scores pending)

- **All 8 images** are clean (no text, frames or UI) and readable at card size.
- **Cost from API usage:** Nano Banana 2.1 ≈ $0.048/image, Pro ≈ $0.144/image, total ≈ $0.77 (thought tokens not priced). About 18–19 s per image.
- **Assistant blind means:**

  | Model | Style | Category | Overall |
  |---|---|---|---|
  | Nano Banana 2.1 | 3.75 | 3.75 | 3.9 |
  | Nano Banana Pro | 3.50 | 4.75 | 4.2 |

  Small sample (n = 4 per arm), so this is a direction, not a conclusion.
- **Systematic, prompt-fixable misses in both models:**
  1. Background colour doesn't contrast with the object.
  2. Too much small detail.
  3. Saturation drops.
  4. Category-4 object too small in frame.
  5. Outlines.
- **Decision rule:** neither arm reaches a style score of ≥4, so stronger conditioning (BENCH-02) comes before building the pipeline.

### Decisions

- D-002: result recorded, final model choice pending Pavel's scores.
- New, proposed: D-012 (BENCH-02).

### Explain it simply

Both Google models already draw in roughly the right style. Pro follows the composition rules better, while 2.1 feels closer to the game's colours. Both make the same few mistakes, such as a blue bottle on a blue background. Those mistakes can be fixed in the instructions, so the next step is to test a corrected prompt before automating anything.

---

## 2026-10-13 / W007 / Ratings consolidated, BENCH-02 (prompt v2)

### Pavel's prompt (verbatim; the pasted ratings are stored in full in `experiments/BENCH-01/scores_external_model_miro_v1.csv`)

> Rated my sheet, check
>
> Also these ratings from another model, take them into account:
>
> [pasted ratings for K7, U5, V5, Y3, K2, R2, C6, L3 from an unnamed model, plus a summary: "R2 is the strongest match … the main inconsistency is rendering—outlines, surface detail and shading—rather than the objects' colours or designs."]

### Actions

- **Parsed Pavel's blind sheet** (`scores_pavel_miro_v1.csv`): style scores plus detailed notes. The spreadsheet saved each row as one quoted field.
- **Compared the three raters** (`BENCH-01/result.md`, "Human and external ratings").
- **Reviewed rows 1–6 of the Miro originals** to check the notes against the real cards:
  - category-4 cards use a low camera angle with large, cropped objects;
  - category-2 surfaces are plain;
  - backgrounds use complementary colours and centred rays or rings.
- **Wrote `experiments/BENCH-02/prompt_v2.md`.** Every new rule is traced to its source: Pavel, the external model, the assistant, or the originals.
- **Chose reference pack v2:** 12 Miro originals, 3 per category, each picked to show one rule. The pack is checked for leaks of the hidden targets.
- **Ran BENCH-02:** Nano Banana 2.1 only, 2 samples × 4 hidden targets = 8 images. Built the before/after sheets (real | v1 | v2-a | v2-b).
- **Downloaded batch 4 of the Miro originals,** including the r06c06 retry: 86 of 160 are now local.

### Results

- **Raters, BENCH-01:**
  - Pavel and the assistant gave **identical style scores on all 8 images** (both blind).
  - The external model scored 0.75 lower on average, with the same model ranking.
  - Everyone put 2.1 ahead of or level with Pro.
  - Pavel judged that players would notice all 8, so none passed the brief's test.
- **D-002 resolved:** Nano Banana 2.1.
- **BENCH-02** (`BENCH-02/result.md`): prompt v2 fixed the systematic misses.
  - Complementary backgrounds; plain category-2 surfaces; reflective category-3 floors with simple backgrounds; low-angle category-4 framing with minimal terrain.
  - Both samples per target are consistent.
  - Assistant style mean is 4.0, up from 3.75 for v1, so it just meets the threshold. That score is not blind, and Pavel's scores are pending.
  - Cost ≈ $0.44 ($0.055/image), average 23 s.
- **Total API spend so far:** ≈ $1.21 (BENCH-01 $0.77 + BENCH-02 $0.44), thought tokens not priced.

### Decisions

- D-002 resolved.
- D-012 run, with a changed design (2.1 only, 2 samples).
- New, proposed: D-013, use prompt v2 and the per-category pack as the starting generation step of the pipeline.

### Explain it simply

We turned the reviewers' comments into explicit art-direction rules: contrasting background colour, how much detail, camera angle, plain surfaces. The same model then got noticeably closer to the real cards, and did so consistently across repeat attempts. The remaining gaps are about which object design to draw, which is the job of the planning step we build next.

---

## 2026-10-13 / W008 / v2 ratings, choosing a second model, OpenAI setup

### Pavel's prompts (verbatim)

> Rated v2 sheet, check. Also, which model we should try in addition, how do I connect CHATGPT image generation API

A message added mid-turn:

> Other model rating for latest generated batch
>
> [table of ratings for T1–T4 v2-a/v2-b from the same unnamed model; stored in full in `experiments/BENCH-02/scores_external_model.csv`]

### Actions

- **Parsed Pavel's v2 scores and the external model's,** and compared them with v1 and the assistant's scores (`BENCH-02/result.md`, "Pavel and external-model ratings").
- **Reviewed rows 7–9 of the Miro originals.** Findings:
  - The reference reds are warm.
  - Category-1 patterns use the set's theme motifs: music notes, scout lilies, π symbols.
  - The thin, wispy steam appears only on the hidden tea cup, so v3 describes it in words.
- **Checked OpenAI's image API** (sources below):
  - Current models: `gpt-image-2.5-sunburst` (precision) and `gpt-image-2.5-flare` (speed), released 2026-09-08; `gpt-image-2` is also available.
  - The `/v1/images/edits` endpoint accepts up to 16 reference images, custom sizes in multiples of 16, and quality settings up to `xhigh`/`max` on 2.5.
  - The docs say API Organization Verification may be needed for GPT Image models.
- **Code:**
  - Added `pipeline/keys.py`, a shared key reader. `gemini_image.py` now uses it; re-checked with the free call.
  - Added `pipeline/openai_image.py`: a standard-library multipart client with a free `check` command. It currently reports the missing `OPENAI_API_KEY`, as expected.
- **Wrote prompt v3** (`experiments/BENCH-03/prompt_v3.md`) with every rule traced to a source, and prepared BENCH-03: `plan.md`, `bench.py`, and the prompts in both provider formats. No API calls.

### Results

- **Pass rate improved:**

  | Rater | v1 | v2 |
  |---|---|---|
  | Pavel | 0/4 | 3/8 |
  | External | 1/4 | 4/8 |

- **Style means:** Pavel 3.75 → 3.63 (his notes shifted to finer issues); external 3.25 → 3.50.
- **Pavel and the external model agree exactly on 5 of 8;** both pass only T2 v2-a. They disagree on the lighthouses: composition approved by Pavel, structural detail missing for the external model.
- **The assistant's non-blind v2 scores were too generous** (4.0), so all future sheets are blind (D-015).

### Decisions (proposed)

- D-014: add GPT Image 2.5 Sunburst.
- D-015: pass rate as the main measure, blind sheets.
- D-016: prompt v3.

### Sources

- OpenAI image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- GPT Images 2.5 announcement: https://community.openai.com/t/introducing-gpt-images-2-5-in-the-api-and-chatgpt/1395897
- Organization verification forum threads: https://community.openai.com/t/new-gpt-image-model-in-the-api/1239462
- gpt-image-2 pricing (third-party): https://www.segmind.com/models/gpt-image-2/pricing

### Explain it simply

The second round passed the "would players notice" test more often. The reviewers' new comments are finer points: warmth of the colours, how steam looks, smooth versus detailed surfaces. Those went into a third prompt version. Next we test it on Google's model and on OpenAI's newest image model side by side, scored blind.

---

## 2026-10-13 / W009 / ChatGPT samples without API credits

### Pavel's prompt (verbatim)

> can we do CHATGPT samples with my account without adding API credits?

### Actions

- **Checked the machine.**
  - Found: the Codex desktop app (the `%USERPROFILE%\.codex` folder, active today), which made GPT-001 with its built-in image tool on Pavel's ChatGPT plan.
  - Not found: the Codex CLI on PATH, so the assistant cannot call Codex directly.
  - Credential files in that folder were not opened.
- **Wrote `experiments/BENCH-03/codex_task.md`,** a ready-to-paste Codex task. It generates 8 images with the exact BENCH-03 OpenAI-format prompts and the same 12 references, saves them as `outputs/chatgpt_*.png`, and writes a log.
- **Built `refs/refs_sheet_3x4.png`,** a single-image fallback in case the tool won't take 12 references.
- Updated `plan.md` (new chatgpt arm) and D-014.

### Decision

D-014 updated: test GPT through the ChatGPT plan first; buy API credits only if GPT clearly beats Nano Banana.

### Explain it simply

Pavel's ChatGPT subscription already includes OpenAI's image model through Codex. We use it to test GPT's quality at no extra cost, with the same prompt and references. We only pay for API access if GPT turns out clearly better, because the final tool must run automatically.

---

## 2026-10-13 / W010 / BENCH-03: Nano Banana (API) vs ChatGPT (Codex)

### Pavel's prompt (verbatim)

> Yes, let's continue. Also Codex is finished with its images

### Actions

- **Ran the Nano Banana arm of BENCH-03:** 8 images, about $0.44, no errors.
- **Read Codex's log** (`BENCH-03/runs/chatgpt_log.md`):
  - 8 images from `image_gen.imagegen`; model not exposed.
  - The tool accepts **at most 5 reference paths**, so every image used the 3×4 sheet fallback.
  - Portrait 1028×1530; one retry; 23–43 s per image.
  - Codex only created the 8 outputs and the log. Checked with a file comparison.
- **Built blind sheets for all 16 outputs.** The assistant scored blind first (`scores_assistant.csv`), then opened the key.
- **Inspected the uncropped ChatGPT lighthouses** after unblinding: the sheet's centre crop removed their lamp rooms. Made `AFTER_SCORING_chatgpt_uncropped.png`.
- **Wrote `BENCH-03/result.md`** (provisional). Added `rating_request.md` (a fixed prompt for the external model) and `PIPELINE.md` (architecture proposal).
- **Downloaded Miro batch 5:** 111 of 160 originals are now local.

### Results (assistant blind; Pavel and external pending)

| Arm | Mean style | Pass rate |
|---|---|---|
| ChatGPT | 3.75 | 5/8 |
| Nano Banana | 3.50 | 3/8 |

- Both ChatGPT failures were lighthouses cut by our crop.
- **API spend so far:** ≈ $1.65 (BENCH-01 $0.77, BENCH-02 $0.44, BENCH-03 $0.44).

### Decisions

None final. Proposed hypothesis, pending scores: Nano Banana for variants, GPT Image 2.5 through the API for the final set (`result.md`).

### Explain it simply

We gave the same instructions to Google's and OpenAI's image models and judged the results without knowing which model made which image. OpenAI's model, used free through Pavel's ChatGPT plan, came out ahead on the blind assistant scores. Its only misses were caused by our cropping, not by the model.

---

## 2026-10-13 / W011 / BENCH-03 human scores and model decision

### Pavel's prompt (verbatim; the pasted table is stored in `experiments/BENCH-03/scores_external_model.csv`)

> Rated v3 sheet, check, these are from other model:
>
> [table with code, score, notice and commentary for H5, L5, S5, U7, D8, H8, J2, T8, A8, B2, F9, S8, P2, P7, Q9, Y2]

### Actions

- **Parsed Pavel's blind scores** (`BENCH-03/scores_pavel.csv`) and saved the external model's.
- **Compared the three raters:** means, pass rates, exact agreement, agreement on "notice".
- **Checked the crop confound** against the uncropped ChatGPT originals.
- **Updated `BENCH-03/result.md`** (final section) and DECISIONS (D-017, D-018).

### Results

- **Nano Banana 2.1 (prompt v3):**
  - Pavel 3.88, 5 of 8 pass; external 3.75, 6 of 8. Best so far for both.
  - Pass-rate trend over v1 → v2 → v3: Pavel 0/4 → 3/8 → 5/8; external 1/4 → 4/8 → 6/8.
- **ChatGPT via Codex:**
  - Pavel 3.50, 3 of 8; external 3.63, 3 of 8.
  - Four of its lowest scores come from our crop of portrait outputs (bottles, lighthouses).
  - On the uncropped targets the two models are about even. Pavel's favourites include the ChatGPT kart (5) and cup (4), and the Nano Banana lighthouse (5).
- **Agreement:**
  - Pavel and the external model agree exactly on 10 of 16.
  - The assistant matched Pavel on only 7 of 16 (all within ±1). It was lenient on oversized objects and strict on decoration. That is a calibration task for automated QA.
- **New rules from Pavel's notes:**
  - clear margins;
  - complete objects (saucer, kart pole);
  - one charming unique detail instead of generic bands;
  - two-colour vehicles;
  - a visible background pattern;
  - floor and wall in separate tones;
  - a brighter overall image.

### Decisions (proposed)

- D-017: Nano Banana 2.1 for the pipeline; GPT API deferred; prompt v4 validated on the first real Cinema set.
- D-018: QA calibrated to Pavel's rules and his scored examples.

### Explain it simply

Three prompt revisions took Google's model from "every card noticeably off" to "most cards pass". OpenAI's model looked comparable but was hurt by a format limit of the free route, which only outputs portrait images. So we keep the cheaper, fully automatable model and spend the remaining time building the tool, with Pavel's notes turned into automatic checks.

---

## 2026-10-13 / W012 / Genres chosen; pipeline v1 built; first set generated

### Pavel's prompt (verbatim)

> Genres:
>
> 1. Romantic comedy — "Love in the City"
> 2. 1950s suburban comedy — "Picture-Perfect Suburbia"
> 3. Fairytale fantasy — "Once Upon a Garden"
> 4. Family treasure adventure — "The Lost Island"

### Actions

- **Recorded the four genres** (D-019). The brief asks for three; the fourth fills the fourth template.
- **Checked the available Gemini text models.** Chose `gemini-3.8-flash` as the QA judge and added `generate_text()` to the Gemini client (tested: about 5 s per call).
- **Wrote the rulebook** (`pipeline/rulebook.md`), with every rule tagged by source: brief, references, Pavel's or the external model's notes, or estimate.
  - It includes a category-mix estimate from about 50 classified reference cards: 3 × C1, 2 × C2, 2 × C3, 3 × C4.
- **Wrote the rest of pipeline v1:**
  - prompts `card_v4` (v3 plus Pavel's BENCH-03 rules plus a card brief) and `qa_v1`;
  - `refs_production.json` (12 originals, now including the former hidden targets);
  - `cardgen.py` (validate / run / regen / sheets);
  - the skill `SKILL.md`.
- **Planned "Love in the City"** as the agent: 3 variants (First Date, Meet-Cute, Happily Ever After) × 10 cards (`sets/love-in-the-city/plan.json`). The validator printed "Plan OK".
- **Smoke test** on A01 and A03:
  - A01 passed first time.
  - A03 failed QA ("houses along the horizon": a plan mistake, the plan asked for rooftops), retried with the reviewer's fix and passed.
  - 3 images, about $0.18.
- **Started the full run** of the other 28 cards (4 in parallel).
- **While it ran, planned the other three sets** (3 variants × 10 each):
  - `sets/picture-perfect-suburbia/plan.json`: Home Sweet Home, Saturday in the Suburbs, Household Hijinks;
  - `sets/once-upon-a-garden/plan.json`: Enchanted Garden, Royal Tale, Wonderland Tea Party;
  - `sets/the-lost-island/plan.json`: Shipwrecked, Jungle Expedition, Treasure Hunt.
- **Rules followed in all plans:**
  - no repeated objects across the four sets;
  - avoid objects the reference collection already has (the Seafaring and Diving props, ring box, rose arch, topiary, lawn mower, pie);
  - public-domain fairy-tale forms only.
- **Validator fix:** the people check now matches whole words, so "paperboy" and "peeking" no longer trigger false warnings.
- **Wrote `pipeline/README.md`,** the designer-facing quick start.
- **Crash and fix.**
  - The full run crashed near the end: the API dropped one connection (`RemoteDisconnected` on A02), the client didn't catch it, and the exception stopped the run before the summary was written.
  - The chained start of sets 2–4 correctly refused to run after the crash.
  - Fixes:
    - network drops and timeouts are now retryable `GeminiError`s;
    - one card's crash no longer stops the set;
    - the summary is rebuilt from the per-card files on disk (`cardgen.py summary`), and an interrupted attempt is recorded as such.
  - Resumed: only A02 was redone, and it passed.
- **"Love in the City" result** (`sets/love-in-the-city/summary.md`, sheets in `sheets/`):
  - 30 of 30 cards: 28 passed QA, 2 accepted with issues (A06 Park Bench: category, the tree crowds the frame; B10 Love Locks: framing).
  - 22 of 30 passed on the first try. 40 images and 40 QA reviews; about $2.45 (QA rates unverified).
  - Assistant review: coherent romantic-comedy sets with consistent style and colour rhythm. The weakest thumbnails are B06 Cafe Table (thin chairs) and B10 Love Locks (busy).
- **Started sets 2–4 in sequence** (about 90 cards).

### Explain it simply

The tool now works end to end. The agent writes a set plan following the rulebook; the script draws each card, has a second AI review it against the rules, and redraws failures with a precise correction.

---

## 2026-10-14 / W013 / Sets 2–4 generated (background run finished; no new prompt from Pavel)

### Results (summaries in `sets/<slug>/summary.md`, sheets in `sets/<slug>/sheets/`)

| Set | Passed QA | Accepted with issues | First-try pass | Images | Est. cost |
|---|---|---|---|---|---|
| Love in the City | 28 | 2 (A06, B10) | 22/30 | 40 | $2.45 |
| Picture-Perfect Suburbia | 27 | 3 (B03 Drive-In, C06 Paperboy Bike, C07 Vacuum) | 16/30 | 47 | $2.88 |
| Once Upon a Garden | 28 | 2 (A02 Fairy Lantern, A06 Beanstalk) | 19/30 | 41 | $2.46 |
| The Lost Island | 27 | 3 (A02 Coconut Cups, A06 Rope Bridge, C03 X Marks the Spot) | 18/30 | 46 | $2.81 |
| **Total** | **110 / 120** | **10** | **75 / 120** | **174** | **≈ $10.60** |

- No crashes; the network fix from W012 held.
- **Total API spend so far:** ≈ $12.25 (benchmarks $1.65 + sets $10.60). The QA rates in that figure are still an unverified assumption, about $0.25 per set.
- **Assistant review** (not blind):
  - All four sets read as coherent genre sub-themes, with consistent rendering and varied colour rhythm.
  - Weak cards mostly match the QA flags: busy C4 scenes (beanstalk, rope bridge, love locks), unclear identity (Drive-In), surfaces (carpet, wall panelling).
  - One cyan-teal background (Suburbia A08 Hula Hoop) slipped past QA despite the no-teal rule.

### Explain it simply

The same tool, given four different genres, produced 120 cards in one evening. Nine in ten passed the automatic art review, and the rest are flagged with a precise reason, so they can be redone one by one.

---

## 2026-10-14 / W014 / Rating workbook and external-model request for the 120 cards

### Pavel's prompt (verbatim)

> Let's rate them first, build spreadsheet I can fill easily here with 1-5 rating and optional commentary
> Also do one for another model in same format we did before

### Actions

- **Loaded the xlsx skill.** openpyxl and LibreOffice are not installed, so the assistant used **Microsoft Excel 16 via COM**, which is installed locally. No download needed, and Excel itself calculates the formulas.
- **`pipeline/review_pack.py`:**
  - builds thumbnails (200×223) and a manifest;
  - builds one sheet per set for the external model, with 10 real reference cards on top and 3 variants with codes below;
  - writes `rating_request.md` in the same table format as the BENCH requests (code | score | notice | commentary), plus an optional pick per set;
  - codes are LC, PP, OG and LI plus the card id.
- **`pipeline/build_rating_workbook.ps1`** builds `sets/ratings/card_ratings_v1.xlsx` with five sheets:
  - How to rate: legend, scale and an example row.
  - Ratings: 120 rows with an embedded thumbnail, a yellow 1–5 dropdown, an optional comment, a link to the full-size card, a colour scale, filters and a frozen header.
  - Set picks: A/B/C/Mix dropdown plus notes.
  - Summary: COUNTIFS/AVERAGEIFS per set and variant.
  - References: the 12 real cards.
- **Fixed two PowerShell/Excel COM issues:**
  - Values taken out of PowerShell arrays reach COM wrapped and fail to convert. Every assignment now has an explicit `[string]` or `[double]` cast.
  - This Russian-locale Excel rejects the English format "0.0" over COM, so the script falls back to the local separator.
- **Verified:**
  - 120 rows, 120 pictures, 120 links, the 1–5 validation, and 0 formula errors after a full calculation.
  - A formula test with temporary ratings (4, 2 → average 3.0, 50% rated 4–5; set and overall totals correct) was discarded without saving.
  - The layout was checked through a PDF export.

### Outputs

- `sets/ratings/card_ratings_v1.xlsx` (for Pavel).
- `sets/ratings/external/LC_…png, PP_…png, OG_…png, LI_…png` and `rating_request.md` (for the external model).

### Explain it simply

Every card now has one row in an Excel file: a picture, a 1–5 dropdown and a comment box. Averages per variant fill in by themselves, so the best variant per set shows up as soon as the ratings are in.

---

## 2026-10-14 / W015 / Fix: the rating dropdown offered one option, "1,2,3,4,5"

### Pavel's prompt (verbatim)

> Why am I not being able to select one number here?

The attached screenshot showed the I2 dropdown in `card_ratings_v1.xlsx` with a single option, "1,2,3,4,5".

### Actions

- **Cause:**
  - Pavel's Windows and Excel use the Russian locale: list separator ";", decimal separator ",".
  - Over COM, Excel parses a dropdown list with the local separator, so "1,2,3,4,5" became one option. The Set picks list "A,B,C,Mix" had the same bug.
  - The W014 check only read back the list text the script had set, so it missed this.
- **Fix in `pipeline/build_rating_workbook.ps1`:**
  - Lists are now joined with `$xl.International(5)`, the local list separator.
  - A new check before saving enters 3 in a rating cell and "Mix" in a pick cell. Excel's `Validation.Value` must accept both, or the build fails.
- **Verified before and after** with a read-only probe on the real file (nothing saved):
  - Old file: rating 3 rejected, the string "1,2,3,4,5" accepted, pick "Mix" rejected.
  - Rebuilt file: rating 3 accepted, "1,2,3,4,5" rejected, "Mix" accepted.
  - The rebuilt file stores the standard list `<formula1>"1,2,3,4,5"</formula1>`. The broken one also carried Excel's `x12ac:list` extension.
- **Rebuilt in place:** the file contents showed Pavel had saved no ratings yet, so nothing was overwritten. 0 formula errors.

### Outputs

- `sets/ratings/card_ratings_v1.xlsx` (rebuilt, same path).

### Explain it simply

Russian Excel separates list items with ";" rather than ",", so the dropdown saw one long option instead of five numbers. The script now asks Excel which separator it uses and tests a real pick before saving.

---

## 2026-10-14 / W016 / Rating round 1: analysis, rules v2, redo of 6 cards

### Pavel's prompt (verbatim)

> ok, I did my rating and other model rating is in /D:/JOB2026HUNT/PLAYRIX_PRODUCER/sets/ratings/external/card_art_style_evaluation.md

### Inputs

- **`sets/ratings/card_ratings_v1.xlsx`**, saved by Pavel at 02:45. It holds:
  - 120 ratings and 29 comments;
  - set picks LC B, PP A, OG A, LI C, each with the note "3 and below".
- **`sets/ratings/external/card_art_style_evaluation.md`:** the external model's table for all 120 codes, plus one ship pick per set (A, A, A, B).

### Actions

1. **Merged the three verdicts.**
   - New `pipeline/export_ratings.ps1` reads the workbook read-only through Excel.
   - New `pipeline/rating_report.py` merges it with the external table and each set's QA `summary.json`. It writes `sets/ratings/rating_numbers.md` and `merged.csv` (semicolon-separated for Russian Excel).
   - The script's per-variant averages match the workbook's own Summary sheet.
2. **Looked at the cards.** Built sheets by category, sorted by Pavel's score and shown next to the real cards. Then reviewed all 160 reference cards (111 originals, plus 49 PDF crops for rows 12–16), following Pavel's request to check all references.
3. **Tested hypotheses before writing rules.**
   - "A warm object on a warm background scores lower": **rejected**. It passed 69% against 73% for the rest.
   - "Object and background in the same colour family": weak signal (3 of 7 passed), kept as a validator warning only.
4. **Built a pixel check of background colour** (`pipeline/colour_check.py`).
   - On all 84 cards in categories 1–3 it fails exactly the 2 cards that ignored the planned colour: PP-A08 came out teal instead of orange, LI-A04 red instead of green. Pavel rated them 2 and 3; the QA judge had passed both.
   - It gives 2 warnings and no false fails.
5. **Pipeline v2 (D-022):**
   - rulebook v2, prompt `card_v5`, QA `qa_v2` (the judge now sees the planned background), reference pack v2 (the Tent with its forest backdrop replaces the Ferris Wheel);
   - the colour check runs inside QA;
   - same-family warning in the validator;
   - README, SKILL.md and PIPELINE.md updated.
6. **Fixed two bugs in `cardgen.py`.**
   - A reviewer's fix used to replace the producer's `--fix` note from the second retry on. Now the reviewer's fix is added to the note.
   - `regen` used to delete the accepted image before a new one existed.
7. **Ran redo round 1** (D-021) with new `pipeline/redo.py` and `sets/ratings/redo_round1.json`.
   - The 6 cards: LC-B04 Heart Balloon, PP-A05 Milk Bottle, PP-A08 Hula Hoop, PP-A09 TV Dinner, LI-C01 Shovel, LI-C02 Storm Lantern.
   - Four briefs were edited first, so that a note would not contradict its brief: B04, A08, C01 and C02. The old values are logged in each card's earlier `try*.request.json`.
   - Five of the six notes are the assistant's reading, labelled as such, because Pavel commented only on LI-C02.

### Results

- **Pass rates:** Pavel 86/120 (72%), mean 3.99; external 85/120 (71%).
- **Pavel vs external, card by card:** same verdict on 77/120 cards, kappa 0.13, score r 0.03. Similar totals, different cards.
- **QA vs Pavel:** Pavel passed 73% of the cards QA passed and 60% of those it flagged. Cards that needed retries were rated the same as first-try cards (71% vs 72%).
- **Weakest category for Pavel:** C1 floating objects (21/36). For the external model it is C4 (19/36).
- **Pavel's comment themes:** detail 6, materials 6, colour or background 6, idea or readability 5, C4 ground or sky 4, praise 2.
- **C4 backgrounds:** all 36 of ours were blue sky. The references use many backdrops (parks, forest, desert, night, city, pool, underwater). The cause was the v1 rule learned from a single lighthouse benchmark, plus three sky-only C4 references.
- **Write-up:** `sets/ratings/ANALYSIS.md`.
- **Redo round 1:** all 6 cards passed QA, 4 on the first attempt.
  - The Hula Hoop's retry carried both the producer's note and the reviewer's fix.
  - Cost about $0.49, so total spend is about $12.74 (QA rates unverified).
  - Pixel audit: the Hula Hoop is now orange. The Storm Lantern's wall measured blue-violet, a warning.
  - Sheets: `sets/ratings/redo_round1/before_after.png` and `chosen_sets.png`.
  - Awaiting Pavel's re-rating.

### Decisions

- **D-021** (picks and redo rule): accepted by Pavel.
- **D-022** (rules v2): implemented.
- **D-018** revised: QA is a gate for the brief, not a stand-in for Pavel's taste.

### Explain it simply

Pavel and a second AI rated all 120 cards and passed about the same number, but mostly different ones. Our automatic checker didn't predict Pavel's picks either. So a person makes the final call, and the tool makes that quick: a spreadsheet, an automatic merge, and one command that remakes the weak cards. Pavel's comments became new rules, but only the ones the ratings back up. The weak cards in his chosen sets were remade for him to check again.

---

## 2026-10-14 / W017 / All Miro references saved; set guidelines v1

### Pavel's prompt (verbatim)

> ok, what's next for us? let's also make sure we have all references saved from Miro. let's try to make set guidelines - what makes set good? I think it is visual coherence and mood it provokes. Playrix games are very good at that, I would say they were pioneers in this renovation genre at that scale

### Actions

1. **Inventoried the board** with the Miro connector, read-only. It has 180 images:
   - 160 cards in "Примеры карточек";
   - 16 set windows in "Пример коллекции", the "Summer" collection shown in the game UI;
   - 4 empty set templates (orange, pink, violet, blue) in "Итоговые наборы".
   - Also present: the empty "Анализ" frame and the three brief texts. Their full text was read; it matches the PDF, and it asks to analyse "how separate objects are organised into a harmonious and logical set".
2. **Downloaded the 69 missing originals** with `image_get_url` and `pipeline/fetch_images.py`: 49 cards (rows 12–16), the 16 windows and the 4 templates. Every folder now has a `manifest.json` with item ids and original file names, and no URLs. The temporary link files were deleted. `board_map.json` now maps each grid row to its set name.
3. **Studied the 16 windows.**
   - Set names; short, playful card names; one window colour per set.
   - Stars 1, 1, 2, 2, 3, 3, 4, 4, 5, 5 in the final windows and the templates, with gold character cards at 5 stars.
   - The windows carry a "Town Cards" logo.
4. **Measured the backdrop colour of all 160 cards and of our 4 chosen sets.** New `pipeline/set_palette.py` writes `analysis/set_palette_profile.md`.
5. **Wrote `pipeline/set_guidelines.md`** (v1, a draft): sources, findings labelled [seen] or [reading], a 10-point set checklist, our 4 sets checked against it, and the next integration steps. `SKILL.md` and `rulebook.md` now point to it.

### Results

- **References:** complete locally (180 of 180).
- **Palette profile:**
  - Reference object sets: 5.5 families per set; the most common family covers 3.8 of 10 cards and often follows the theme (Diving teal or blue 8/10, Beach blue 6/10, Countrystead green 4/10, Coolness orange 4/10); 1.7 of 13 neighbour pairs share a family.
  - Ours: 5.8 families, 3.8 of 10, 1.0 of 13, so the rhythm already fits. But blue leads in all four, because every scene card had a sky.
- **Gaps in our sets:** no star order or crescendo, no window colours, and the palettes don't carry the mood (LC, OG).

### Decisions

- **D-023:** set guidelines v1 (proposed, for Pavel's feedback).

### Explain it simply

Everything on the Miro board is now saved, including the screenshots of the whole "Summer" collection as players see it. They show what makes a set work: a single situation you recognise at once, a mood carried by colour and light, and an order that builds from small everyday things to the most special cards. Our cards already fit the colour rhythm, but not yet the mood colours or that build-up. The guidelines write this down as a checklist the tool will follow.

---

## 2026-10-14 / W018 / The guidelines go into the tool; a Western set with Gemini and ChatGPT

### Pavel's prompt (verbatim)

> Set guidelines are good, you summarized it in clean and simple way. Let's try to make new set for new Genre with Gemini and ChatGPT (even though it may take few attemps). I want to make sure that tool is going to create set according to what we found

### Actions

1. **Built the guidelines into the tool** (D-024):
   - **Plan schema 2:** a set bible per variant (moment, mood, lead colour, window colour, motif) and, per card, a role, stars and light. Card order is star order.
   - **`cardgen validate`** enforces the set checklist (roles, stars, lead colour, 5×2 neighbours, light, name length). A variant can opt in on its own (`"schema": 2` in the variant).
   - **`cardgen setcheck`** measures a finished set against the plan and the reference ranges and writes `setcheck.md`.
   - **Prompt `card_v6` and QA `qa_v3`** keep a planned sunset or night bright.
   - **Docs:** rulebook §5–6 rewritten (palette and schema 2); SKILL.md planning and review steps rewritten; README updated.
2. **Automated the ChatGPT route** with new `pipeline/codex_images.py`. It writes the same card text and 4 references (3 of the card's category plus a sheet of all 12), runs `codex exec` on Pavel's ChatGPT plan, then crops the results, builds sheets and runs the set check.
   - One-card test (LC-B04): Codex accepted all 4 references and returned a square 1254×1254 image in about 30 s, so the BENCH-03 portrait crop problem is gone.
3. **New `pipeline/set_window.py`** lays a variant into the brief's empty set template:
   - transparent slots found automatically;
   - the placeholder title and names painted out;
   - our title and names written in Berlin Sans FB Demi.
4. **Applied the guidelines to Pavel's 4 chosen variants:**
   - added a set bible, roles and stars;
   - reordered the cards by stars, with the fewest same-colour neighbours (measured): LC-B 2, PP-A 1, OG-A 1, LI-C 1;
   - backups saved as `plan.before_W018.json`;
   - built 4 windows (pink, orange, violet, blue): `sets/ratings/chosen_windows_W018.jpg`.
5. **Started the autonomy test:** a fresh agent with no conversation context, only the skill and the tool's files, was asked for "a family Western" (3 variants, Gemini only), including the plan, run, set check and its own review.
6. **Ran ChatGPT on the agent's plan** (all 3 variants, via `codex_images.py`). Afterwards, 2 cards (A03, A04) were redone, because the agent changed their briefs after their ChatGPT prompts were written; the old versions are kept in `gpt/old_brief/`.
7. **Blind comparison:** `compare_routes.py` laid both versions of each variant into the template and gave them codes A1/A2, B1/B2, C1/C2 in random order (key in `compare/blind_key.json`).
8. **Fixed the tool problems the test agent reported (its section 6):**
   - setcheck crashed on a cp1251 console over "→": now ASCII, and the CLIs replace any character the console can't print;
   - banned terms are now whole words, so "branding iron" passes, and weapon, alcohol and tobacco words were added;
   - captions shrink to fit their cell;
   - summary.md shows only open reviewer fixes;
   - out-of-date mentions of the old prompt versions corrected.
   - **Rulebook additions:**
     - a C4 `bg_color` is the colour of the upper backdrop, usually the sky;
     - reusing a window colour is normal;
     - tiny animal details are fine;
     - warm-led sets are fine for warm themes;
     - commons must pass the name test on their own;
     - the top stars go to the big places and iconic objects.
   - **Set guidelines → v1.1.**
   - **SKILL.md:** the review is the set-level check; regen cost and behaviour; the window step; the optional ChatGPT route; which outputs are kept and which are rebuilt.

### Results

- **Autonomy test, planning:** the fresh agent's plan ("Sunny Frontier": Ranch Day, Wagon Trail, Frontier Town) passed validation on the first try with 0 warnings. It followed every checklist item from the files alone:
  - a moment and mood per variant;
  - lead colours orange, yellow and red; windows orange, blue and pink;
  - motifs (horseshoes, wagon wheels, small cacti);
  - 5–6 roles; stars in order, with big places at 4–5 stars;
  - one deliberate sunset or night card per variant;
  - a few playful names ("Prickly Pal", "Chow Time!", "Hoedown");
  - no guns or alcohol.
- **Gemini:** 30/30 passed QA (39 images, $2.37). The agent's own sheet review caught 4 set-level problems that QA passed and fixed them with regens: an orchestra triangle, a teapot-looking coffee pot, a trunk that overlapped the Lost Island treasure, and a motif ring that read as orange slices.
  - Measured set check: lead colour 3/4/3 cards, 5–6 families, 1–2 same-colour neighbours. All within the reference ranges.
  - It recommends variant A.
- **ChatGPT via Codex:** 32 images (30 plus 2 redone), all square 1254×1254, about 30 s each, $0 extra on the ChatGPT plan, no tool errors. Every pixel check of categories 1–3 passed.
  - The measured palettes of the two models are nearly identical, so the plan drives the set's look whichever model draws it.
- **Blind windows:** `sets/sunny-frontier/compare/all_windows_blind.jpg`, waiting for Pavel's picks.

### Explain it simply

A brand-new agent that had never seen our conversation was handed only the tool and asked for a Western set. It planned the set the way our guidelines describe: one situation per set, a mood colour, a build-up from small props to big places, and a recurring symbol. It also spotted problems the automatic checker missed. Gemini and ChatGPT then drew the same plan, and the two versions are laid out side by side, without saying which is which, for Pavel to judge.

---

## 2026-10-14 / W019 / Blind pick: ChatGPT; size measured; final pass (prompt v7)

### Pavel's prompt (verbatim)

> First image: A1, B2, C1 are better in my opinion, but they have issue with object size and breathing room, in seems to me reference has than cleaner, can you check?
> What is your preference?
>
> The most useful final pass would be to:
>
> * Standardize object size and breathing room within cards.
> * Simplify details that disappear at normal card size.
> * Align highlight strength and material shading across each set.
> * Make sure that each card belong to category provided in test task clearly (it mostly does)
>
> Can I write to your copy of the Miro board (the "Analysis", "Final sets" and "Process" frames), and should it be in Russian like the brief? Yes, but let's make it as final step, we will use Russian for Miro and we will also have readme and history files in repo in Russian so process is clearly described.
>
> For GitHub: a private repository under your account, with the Playrix references left out? Either you create it, or I install the GitHub command-line tool and push. Also let's wait until we have final results ready. Do we need to leave Playrix references out if they will test tool? It could be private repo only shared with them. What is best approach here?

### Actions and results

1. **Unblinded the key:** Pavel's picks A1, B2 and C1 are all **ChatGPT** (3 of 3). The assistant's preference matches; see the reply.
2. **Measured "size and breathing room" instead of judging by eye.** New `pipeline/card_metrics.py` (one vision call per card plus pixel measures).
   - **Per card:** the main object's box and the composition category as the brief defines them (5 = characters); extent (the object's largest dimension), smallest margin, room above, detail lost at 66 px, and highlight share.
   - **Reference norms** (all 160 cards; the category reading matched all 12 known categories), median extent by category: C1 0.82, C2 0.85, C3 0.89, C4 0.85. Smallest margin 0.04–0.08; room above 0.12–0.16.
   - **ChatGPT Western:** extent 0.89 (middle half 0.85–0.94); margins often 0–2% and little room above; 24/30 flagged.
     - Part of it is the pipeline: the square output loses about 5% per side in the crop to the card shape.
     - Detail lost 12.1 vs 9.6 for the references (scene cards 15–20).
   - **Gemini Western:** extent 0.82 (0.78–0.86), on target.
   - **The 4 chosen sets (older prompts):** uneven, 0.68–0.91. Several C1 objects are small (0.62–0.73), some objects too big, and C2 objects sit low with an empty wall above (room above 0.27–0.42).
   - **Category:** every Western card reads as planned, and 39/40 chosen cards; only PP-A07 Stand Mixer reads as C2 instead of C3.
   - The highlight measure counts white objects as shine (the mailbox), so highlights are judged by eye within each set.
3. **Prompt v7, used by both routes:**
   - framing targets measured on the reference cards (extent 80–88%, at least 5% clear on every side, 12–16% room above, a safe area for the 9:10 crop, the object vertically centred, no low objects under an empty wall);
   - simplicity at card size (no details under about 1/20 of the width; simple scene masses);
   - moderate, even highlights shared by the set.
4. **Automatic correction notes:** `card_metrics.py fixes` writes a measured note for each flagged card (for example "The object spans 93% of the card; make it smaller, about 82%").
5. **ChatGPT route:** `codex_images.py` takes `--route-dir` (keeps earlier runs) and `--fixes` (per-card notes).
6. **Pilot:** re-render the ChatGPT Western with v7 into `gpt_v7/`, measure it, give the flagged cards one correction round, then compare before and after.
7. **The pilot showed that the prompt doesn't control ChatGPT's framing.**
   - v7 variant A came out at extent 0.90 (vs 0.88 with v6), 8/10 flagged.
   - Then the ChatGPT plan hit its usage limit: Codex said "try again at Oct 15th, 2026 1:15 AM", after 19 of 30 v7 images, about 52 ChatGPT images that day. The partial run stays in `gpt_v7/` as evidence.
8. **Root cause, measured on the uncropped squares:** ChatGPT's squares are already close to the reference norms (extent 0.81–0.91, margins 2–7%).
   - Our centre crop to 9:10 cut about 5% off each side and pushed wide objects into the edges: the hat 0.89→0.97, the gate 0.88→0.98, the barn 0.91→1.00.
   - **Fix 1:** `sheets.extend_to_card` keeps the full width and stretches the background above and below; the default for the ChatGPT route. Alone, it took extent from 0.89 to 0.81.
   - **Fix 2:** new `pipeline/reframe.py`. Per card, it finds the object's box on the full image and picks the 9:10 window (crop, or stretched-background extension up to 12% per side) that gives:
     - the reference median size for the category;
     - at least 5% margins;
     - 14–21% room above.
9. **Applied reframing to every final set,** with no new art:
   - ChatGPT Western: extent 0.83 (middle half 0.81–0.85, was 0.85–0.94).
   - The 4 chosen Gemini sets: 0.81–0.86 each (was 0.68–0.91).
   - Windows rebuilt: `sets/ratings/chosen_windows_reframed.jpg`, `sets/sunny-frontier/compare_reframe/western_gpt_reframed.jpg`.
   - Older Gemini cards without `chosen.json` use the run's own choice rule (`cardgen.collect_card`).
10. **Remade 3 chosen cards with Gemini** (prompt v7, measured notes, then reframed); all 3 are now flag-free:
    - PP-A07 Stand Mixer: category, now a wooden countertop;
    - OG-A10 Wishing Well: detail lost 14.8→11.8;
    - LI-C02 Storm Lantern: detail lost 17.5→11.3.
    - Left alone despite detail flags, because Pavel rated them 5: LC-B10 Love Locks, PP-A10 Station Wagon.
11. **Highlights:** by eye, no card in the final sets stands out from its set's finish. The measure isn't reliable here (white objects count as shine).
12. **Docs:** SKILL.md, README and rulebook now include the reframe and measure steps and the measured framing norms.

### Results

- Pavel's list:
  - (1) Size and breathing room: standardised for every final set, measured.
  - (2) Detail: fixed on 2 chosen cards; the Western's ChatGPT scene cards still run high, and fixing them needs ChatGPT regens after the limit resets.
  - (3) Highlights: no outliers seen.
  - (4) Category: the one mismatch is fixed.
- Cost this round: about $0.5 for vision calls (about 300 at the flash rate, unverified) plus about $0.2 for 3 regens, so total spend is about $15.8.

---

## 2026-10-15 / W020 / The 4 final sets redrawn with ChatGPT for a blind pick

### Pavel's prompt (verbatim)

> One limit: your ChatGPT plan hit its usage cap after about 50 images today. It resets around 01:15. - Just reset limit
>
> (b) redraw all 40 cards with ChatGPT tomorrow (one usage window), reframe them, and you pick blind per set?

### Actions

1. **Carried over the art-direction notes** from redo round 1 and the W019 final pass (`sets/ratings/gpt_final_notes.json`, 8 cards), rephrased as directions because ChatGPT draws these cards fresh. `codex_images.py` now labels such notes "Art direction for this card".
2. **Redrew the 4 chosen variants** (LC-B, PP-A, OG-A, LI-C, 40 cards) with ChatGPT through Codex. Same plans, prompt v7, 4 references per card; output in `sets/<slug>/gpt_v7/`.
3. **Then:** reframe with `reframe.py --route gpt_v7`, measure with `card_metrics.py`, and lay out blind windows with `compare_routes.py --gpt-dir gpt_v7` against the current final Gemini versions (reframed, with the W019 remakes).

### Results

- **Generation:** 40/40 ChatGPT images (all Codex runs exited 0), about 8–9 minutes per set, 00:01–00:33. About 10 images remain in this usage window, kept for after Pavel's picks.
- **After reframing,** the ChatGPT versions sit at extent 0.82–0.85 per set (middle halves 0.81–0.89).
- **Flags** (ChatGPT versions): LC 5, PP 5, OG 2, LI 5 of 10. Mostly fine detail in scene and C3 cards; detail lost up to 24.9 on the PP Station Wagon, against a reference median of 9.6.
- **Measured palettes** of the two versions are nearly identical per set; the plan drives the colours.
- **Blind sheet:** `sets/ratings/final_sets_blind.jpg`. Keys are in `sets/<slug>/compare/blind_key.json`, unopened until Pavel picks.

---

## 2026-10-15 / W021 / Picks: ChatGPT for all 4 final sets; measured cleanup; final_set/

### Pavel's prompt (verbatim)

> Yeah, I like version 1 for all of them

### Actions and results

1. **Unblinded:** version 1 was ChatGPT in all four sets, so Pavel picked ChatGPT 4/4 (and 3/3 on the Western, 7/7 in all).
   - **Protocol caveat:** `compare_routes.py` reused one seed per call, so ChatGPT sat in slot 1 in all four sets, and this round alone can't separate position bias from preference.
   - The Western round had mixed positions and also went 3/3 ChatGPT, so the preference stands.
   - Fixed: each set now gets its own random order (seed plus set name).
2. **Measured cleanup of the winners:** 14 cards are flagged for "fine detail lost". The 10 with the largest excess over their category's reference upper quartile get specific simplification notes (`sets/ratings/cleanup_round1.json`).
   - They are redrawn with ChatGPT into `gpt_v7_clean/` and reframed; the picked versions stay in `gpt_v7/`.
   - The remaining 4 (LC-B06, LC-B10, OG-A02, PP-A05) are left for the next usage window, if needed.
3. **New `pipeline/assemble_final.py`:** builds each set's deliverable folder `final_set/` from the chosen sources, with `sources.json` recording each card's origin, and lays out its window.
4. **Cleanup results:** all 10 redrawn (Codex exit 0, no usage limit). Acceptance rule: detail lost drops by 2+ points, the same category, and the size moves no further from the category target than 0.08.
   - **Accepted (6):**

     | Card | Detail lost (old → new) |
     |---|---|
     | PP-A10 Station Wagon | 24.9 → 21.0 |
     | PP-A03 Dream House | 19.2 → 14.8 |
     | LI-C06 Waterfall Cave | 17.1 → 11.9 |
     | LI-C07 Jewel Goblet | 16.9 → 13.9 |
     | LI-C08 Bag of Gold | 12.1 → 9.0 |
     | LC-B03 Vintage Scooter | 17.4 → 14.6 |

   - **Kept as picked (4):** PP-A09 TV Dinner (−1.3), LI-C02 Storm Lantern (+0.6), LI-C10 Palm Hammock (−1.6), LC-B02 Typewriter (−1.7).
   - Sheet: `sets/ratings/cleanup_round1_before_after.png`.
5. **Final sets assembled** in `sets/<slug>/final_set/` (with `sources.json`); windows in `sets/<slug>/sheets/`, combined in `sets/ratings/final_sets_W021.jpg`.
   - **Set check** (measured on `final_set/`):
     - stars in order;
     - lead colour 4/4/3/3 cards as planned;
     - 5–7 families;
     - 1–2 same-colour neighbours;
     - extent medians 0.82–0.85, middle halves within 0.81–0.87.
   - Remaining card flags are mostly scene detail, which is ChatGPT's style; one cleanup round has been done.

### Explain it simply

Pavel chose ChatGPT's drawings in every comparison. The four final sets now use them, resized to the real cards' proportions, with the busiest pictures simplified where that clearly helped. Each set sits in the game's own set window, ready for the presentation.

---

## 2026-10-15 / W022 / Cleanup round 2; background extension by outpainting

### Pavel's prompt (verbatim)

> Please do, no need to Western cards revision

It answers the question "Or should I spend the next ChatGPT window on one more cleanup of the remaining detailed cards, plus the Western's scene cards?"

### Actions and results

1. **Cleanup round 2** (`sets/ratings/cleanup_round2.json`): the 11 cards still flagged for "detail lost at 66 px" in `final_set/`. Cards already tried once get a more concrete description of a simpler object. Same acceptance rule as round 1; redraws go to `gpt_v7_clean2/`.
   - **Redrawn 6**, then the ChatGPT usage limit ("try again at 5:01 AM").
   - **Accepted (4):**

     | Card | Detail lost (old → new) |
     |---|---|
     | PP-A09 TV Dinner | 20.7 → 17.6 |
     | PP-A05 Milk Bottle | 11.9 → 8.4 |
     | LI-C02 Storm Lantern | 20.1 → 13.8 |
     | LI-C10 Palm Hammock | 15.4 → 13.1 |

   - **Kept as before (2):** PP-A10 Station Wagon (20.9 → 23.9, more detail), PP-A03 Dream House (drop 1.9, under 2).
   - **Not redrawn yet (5):** LC-B02, B06, B10, B03 and OG-A02. They wait for the ChatGPT window and Gemini credits (item 4).
   - Decisions: `sets/ratings/cleanup_round2_decisions.json`.
2. **Stretched backgrounds replaced by outpainting** (`pipeline/reframe.py`, D-027).
   - **Problem:** at full size, the stretched background extension left streaks on the scene cards (PP-A10 road and lawn, LC-B10 sky, OG-A06 grass) and on a ring backdrop (LI-C05).
   - **Two rule fixes for stretching did not hold.** Anchoring scenes at the bottom, never stretching a side the object touches, and fixing an inverted seam mask traded the streaks for cropping (LC-B03 scooter, LI-C10 palm tops) and a smeared beanstalk.
   - **New step:** Nano Banana 2.1 continues the picture outward.
     - The model gets the picture on a square canvas 12% larger per side, with the stretched border as a colour hint.
     - The script matches the model's colours to the original at the seam and keeps the original pixels, blended in over a 2% seam.
     - A seam check rejects a copy that moved (difference above 5 of 255). After one retry, the card falls back to stretching.
     - Every attempt is kept in `<route>/outpaint/`.
   - **Test on PP-A10:** seam difference 2.1 with the colour hint, against 8.8 on a white canvas. The road, lawn and sky continue naturally.
   - **Framing geometry is back to W021's**, the version Pavel picked from. The stretch-only rules now apply only when stretching.
   - **On the 40 final cards:**
     - 37 outpainted;
     - 1 stretched: LI-C04 Ruby Necklace. Both attempts added a dark table edge and failed the seam check; its plain backdrop stretches cleanly;
     - 2 need no extension.
   - Cost: 43 calls, about $1.5, plus 2 test calls.
   - **Review overrides** (`sets/the-lost-island/framing.json`, new in `reframe.py`):
     - **LI-C10:** the vision box covered only the hammock, so the framing cut the palm tops. A hand-set box frames the hammock with its palms.
     - **LI-C05:** both attempts scored just above the seam limit (5.9 and 5.6), but attempt 2 has no visible seam, while stretching smears the ring backdrop.
3. **Final sets re-assembled:** `final_set/` and the windows; combined sheet `sets/ratings/final_sets_W022.jpg`.
   - Object size from the framing log (same vision boxes): set medians 0.815–0.85, all cards 0.81–0.90.
   - The `card_metrics` report on the new files isn't re-run yet, because it needs Gemini (item 4).
4. **Blocker:** at about 02:45 the Gemini API returned HTTP 402, "Your prepayment credits are depleted". No Gemini call works (generation, QA, vision boxes, outpainting) until Pavel tops up the prepaid credits in AI Studio. The 5 remaining redraws need Gemini for framing and measuring.

### Explain it simply

Some pictures had to be widened to fit the card shape. Before, we smeared the edge pixels outward, which looked blurry on skies and grass. Now the image model paints the missing strip of background, and the original drawing stays untouched. All four sets look clean at full size.

---

## 2026-10-15 / W023 / Last redraws; sets final; repository prepared; reviewer test 1

### Pavel's prompt (verbatim)

> Last 5 redraws - reset ChatGPT usage and added Gemini credits
> Final sets - yeah, they are good for final, but we need 2 test runs like reviewer of task would do, so we'll do one before commiting to repo. For github what should I prepare? I confirm private repo that includes reference with property of playrix notice
> Miro write will be last step we will iterate on

### Actions and results

1. **The last 5 cleanup redraws** (ChatGPT, `gpt_v7_clean2/`), reframed with outpainting and measured. Same acceptance rule.
   - **Accepted (2):**

     | Card | Detail lost (old → new) |
     |---|---|
     | LC-B02 Typewriter | 16.6 → 13.2 |
     | LC-B06 Cafe Table | 15.2 → 12.3 |

   - **Kept (3):**
     - LC-B10 Love Locks: 17.6 → 21.4, more detail;
     - LC-B03 Vintage Scooter: drop 0.8;
     - OG-A02 Fairy Lantern: drop 0.7.
   - Checked by eye on `sets/ratings/cleanup_round2_last5.png`.
   - Round 2 in total: 6 of 11 accepted.
2. **Final sets confirmed by Pavel.**
   - Re-measured on `final_set/`. Every card reads as its planned category.
   - Set extent medians 0.82–0.85.
   - Flags: LC 5, PP 4, OG 2, LI 2. Most are scene cards that fill the card (extent 1.00 for Love Locks, Palm Hammock, Waterfall Cave) and "much room above" on C2 cards.
   - Windows and `sets/ratings/final_sets_W022.jpg` rebuilt.
3. **Repository prepared** (D-028). Nothing is committed or pushed yet.
   - New Russian `README.md` (what is here, quick start, how it works, why, structure, limits) and `HISTORY.md` (the story of the work).
   - The old English README moved to `docs/start_notes_2026-10-07.md`.
   - `references/NOTICE.md`: property of Playrix, references only, do not share outside the private repository.
   - `.gitignore`: bulky intermediates stay local (raw ChatGPT squares, Gemini attempt images, outpaint canvases, `final_prev/`), as do the brief PDF and Python caches; their JSON logs stay in. Result: 2,340 files, 384 MB. A scan found no API key in any file.
   - `git init` (branch `main`) in the project folder.
   - `set_window.py` now falls back to fonts that exist on macOS and Linux, then to Pillow's built-in font. Before, it only knew the Windows paths, so a reviewer on a Mac would have hit a crash at the window step.
4. **Reviewer test 1** (Pavel's request: two test runs as a reviewer would do them, the first before the repository commit).
   - The repository contents were copied into a clean folder, `D:\JOB2026HUNT\PLAYRIX_TEST1`.
   - A fresh agent with no conversation context works only inside that folder. It is given a reviewer's request in Russian: "Сделай, пожалуйста, набор карточек для коллекции «Кино»: жанр — детектив. Пожелания: уютная загадка в духе классического английского детектива, без оружия и крови. 3 варианта."
   - It may not edit the tool or docs, and it writes `sets/<slug>/review_notes.md`: the designer report, every problem met, and what would block a reviewer.
5. **Test 1 results** (`sets/cosy-mystery/`, notes in `review_notes.md`; Pavel then said he had topped up the Gemini credits).
   - **The tool worked end to end from the README and the skill alone.** A set the agent named "Cosy Mystery", with 3 variants:
     - A, The Great Detective: the sleuth's London;
     - B, Country House Weekend: a manor and a missing blue diamond;
     - C, Village Fête: a nibbled prize cake.
   - **Plan:** `Plan OK` on the first try, 0 warnings. The agent avoided objects from our other sets, plus guns, candlesticks, tobacco and protected designs (the phone box, the police box).
   - **Cards:** 30, of which 25 passed QA and 5 were accepted with issues. The agent's own sheet review caught a circus-looking tent, a lone narrow house and a shaving-brush look, and redrew them.
   - **Time:** about 54 minutes:

     | Stage | Minutes |
     |---|---|
     | Reading | 4 |
     | Planning | 17 |
     | Generation | 8.5 |
     | Framing | 2 |
     | Review and regens | 15 |
     | Windows and report | 6 |

   - **Cost:** about $4.6. That is $3.50 for generation and QA, $0.92 for background extension and about $0.1–0.2 for vision calls. Its recommendation: variant A.
   - **The Gemini balance ran out at 03:27 (HTTP 402).** The agent hand-framed 5 regenerated cards through `framing.json` and wrote down how to finish the set after a top-up.
   - **Problems it found, by severity, with the fixes:**
     1. **Critical: an empty balance was hidden or did damage.**
        - `regen` printed "passed".
        - `reframe.py` framed the new images with the old images' boxes.
        - `card_metrics.py` printed "5 measured" when none were.

        **Fix:**
        - HTTP 402 is now its own error (`BillingError`). Every script stops on it with one message: top up in AI Studio and run the same command again.
        - Unmeasured or unextended cards are left as they were.
        - The scripts count only what was actually measured.
        - A QA call that fails now leaves the card `unchecked`, never `passed`. Before, a failed QA call let the card pass.
     2. **The QA judge never saw the planned `context_cue`.** It failed planned cues as extra props (scones by the teapot, a magnifier by the bowler hat), which cost retries and dropped the cue. **Fix:** QA prompt v4 includes the cue. Re-test on B02: the scones passed on the first attempt.
     3. **The skill's step order left stale outputs:** sheets built before framing, regen images unframed, and no undo. **Fix:**
        - `reframe.py` rebuilds the variant sheets.
        - `regen` frames its card and rebuilds the sheets.
        - New `cardgen.py choose <plan> <id> try<n>` makes an earlier attempt final again.
     4. **Cost was incomplete:** `summary.json` held only generation and QA, and `outpaint.json` lost entries on a failed re-run. **Fix:**
        - new `costs.py` and `costs.jsonl`, which every paid call appends to (generation, QA, outpaint, vision);
        - `summary.md` totals it;
        - outpaint entries are kept and accumulate `spent`.
     5. **`framing.json` was hand-written**, with an mtime and a format documented only in code. **Fix:**
        - `reframe.py --override <id> --box ... | --fill ... --why "..."` and `--clear-override`;
        - a hand-set box needs no API call.
     6. **Smaller:**
        - `summary.md`'s open fix came from the last attempt, not the chosen one;
        - correction notes included framing flags that a redraw can't change; they're now left out for framed cards;
        - "Fête" showed as "F□te" on sheets; captions now use a font with accented letters;
        - `pipeline/README.md` named prompt v6;
        - the skill now says what to do without a set name;
        - the README states the full run's time and cost, and that a QA pass is not approval.
   - **Verified** without spending: HTTP 402 was simulated for `run`, `regen`, `reframe.py` (box and outpaint stages) and `card_metrics.py`. Each stopped with the message and left the final images unchanged (checksums). The override and `choose` commands were tested too. One real regen with QA v4 cost about $0.06.
   - **Finishing test 1's set after the top-up,** as its notes say:
     - cleared the 5 hand-made overrides;
     - reframed A06, A09, B04, B05 and C09 with the fixed tool (5 outpaints);
     - re-measured: 9 of 30 flagged, extent median 0.83;
     - rebuilt the windows: `sets/cosy-mystery/sheets/all_windows.jpg`.
     - A09 Townhouse failed the seam check twice (14.8 and 13.4: fine window frames make a small shift score high). Attempt 4 shows no visible seam, while stretching smears the clouds, so it is set as a review override with the reason. About $0.23, logged in its `costs.jsonl`.
   - The set and a note about what was done after the test (`after_test.md`) are now in `sets/cosy-mystery/`.
6. **Readiness review from another session** (written at 03:22 by a session Pavel started; now `docs/reviews/2026-10-15_readiness_review.md`, added in W027).
   - It confirmed the QA-failure-as-pass bug, already fixed in item 5.
   - It found that plan validation didn't reject category 5. **Fix:** every card's category must be 1–4, tested on the Western plan (a C1 card set to 5 is now an error) and on all 5 real plans (0 errors).
   - Other suggestions taken:
     - the README now makes the choice of renderer explicit (Gemini automated baseline, or the ChatGPT route used for the final art, which has no per-card judge);
     - "7 of 7" is labelled as Pavel's preference;
     - the QA result is worded as 73% vs 60%, not "no prediction";
     - "players would not notice" is labelled as the rater's judgement;
     - the README explains that the excluded intermediates mean old sets can't be re-framed from a clone;
     - metric flags are inspection prompts, with the accepted exceptions named;
     - costs are labelled as estimates;
     - `requirements.txt` added;
     - `PIPELINE.md` marked as a historical proposal.
   - **Not taken, for Pavel:**
     - The Lost Island has two shovels (C01 Shovel and C03 X Marks the Spot); a change would reopen a final set.
     - Whether to name three headline sets and label the fourth as additional.

---

## 2026-10-15 / W024 / The Lost Island's second shovel replaced; low objects re-centred

### Pavel's prompt (verbatim)

> Lost Island still repeats a shovel as the focal subject of two cards. This is worth changing. Is it done? Any other art task not finished yet?

### Actions and results

1. **LI-C01 Shovel → Explorer Hat** (D-030).
   - **Why this object.** It must not overlap the reference collection: Seafaring has a spyglass and a treasure map, Boyscout has binoculars. It must not overlap our own sets either: a brass compass would echo Once Upon a Garden's pocket watch. It also keeps the set's gold-coin motif, with a coin tucked in the hat band. X Marks the Spot keeps its shovel, because that is its story.
   - **Plan changes** (backup `plan.before_W024.json`):
     - name, subject, colours, role carry (gear 2, carry 4: still 4 roles);
     - the moment now reads "from putting on the explorer's hat to the jewel-filled goblet".
   - **Background.** A blue background was tried first. The validator refused it as a third same-colour neighbour pair (the card sits above X Marks the Spot). So the card keeps the original yellow rays, with an olive hat for contrast.
   - **Drawing.** ChatGPT drew it in `gpt_v7_w024/`.
     - Attempt 1: the rays came out yellow-orange (52% orange) beside the orange Fruit Basket. Kept in `gpt_v7_w024/try1/`.
     - Attempt 2, with the note "clear lemon-yellow, no orange": 100% yellow, category 1 as planned, extent 0.82, detail lost 7.5.
   - **Set check:** roles 4, stars in order, blue lead 3/3, 5 families, 2 of 13 same-colour neighbours.
2. **The open art item from W019, "breathing room":** three category-2 cards were drawn low under an empty wall. Room above: LC-B05 Matching Mugs 0.31, LC-B09 Heart Glasses 0.32, PP-A09 TV Dinner 0.27; reference median about 0.14, upper quartile 0.21.
   - **Cause:** framing could extend the background by only 12% below, so these three couldn't be centred.
   - **Fix:** new `MAX_PAD_BELOW` in `reframe.py`. Below an object on a plain backdrop or tabletop (categories 1–3), the image model may now extend up to 25%; scenes stay at 12%.
     - Canvases are outpainted with the margin they need, and a cached canvas is used only if it is wide enough.
     - A dry run over all 40 final cards changed exactly these three.
   - **Results:** room above 0.21 on all three. B05 and B09 have no flags left; A09 keeps only "fine detail lost".
   - **A09:** the first deeper extension continued the wall-to-table line at a different height on both sides, which the seam check doesn't catch. Of three attempts, attempt 3 joins cleanly, so it is set as a review override with the reason. Cost about $0.18 for 5 calls.
3. **Final sets re-assembled and re-measured;** combined sheet `sets/ratings/final_sets_W024.jpg`.
   - Flags now: LC 3, PP 4, OG 2, LI 3.
   - What remains:
     - fine detail on scene cards (2 cleanup rounds done);
     - full-width scenes;
     - the hat at the room-above cap.
   - **Other art tasks:** none open. The remaining flags are listed as accepted exceptions in the README.

---

## 2026-10-15 / W025 / A second outside review: two failure paths, the cost line, the Codex entry point

### Pavel's prompt (verbatim; the pasted review is stored in full in `docs/reviews/2026-10-15_second_review.md`, added to the repository in W027)

> Review from other model:
>
> "[pasted review: three findings (an unreadable QA answer still becomes "passed"; a balance failure during QA can replace the previous final image; Cosy Mystery's cost summary presents a partial log as the total), the Codex entry-point inconsistency, and a recommendation to finish the shovel, run the second clean-repository test, then build the Miro presentation]"
>
> Should we add ability to use CHATGPT API for reviewer?

### Actions and results

1. **An unreadable QA answer is now "no verdict", never a pass.**
   - `review()` gives `pass: None` when the answer can't be parsed, isn't a JSON object, or its `pass` isn't a true/false value.
   - New `judge()` asks the judge once more when there is no verdict, then applies the pixel colour check.
   - Checked offline with a fake judge answering in prose. The attempt was recorded "QA answer has no true/false verdict" and the review was asked twice; the colour check then decided the card.
2. **A balance failure during QA keeps the earlier final.** If the balance runs out before any new attempt passes, `produce_card` leaves `final/<id>.png` and `chosen.json` as they were. The new attempt waits in `cards/<id>/`.
   - On the next run, an attempt with an image but no verdict is reviewed before anything new is drawn, so the image isn't paid for twice.
   - `run` also picks up cards whose chosen status is `unchecked`.
   - **Checked offline:**
     - `regen` with the QA call failing on billing: checksum and choice unchanged, exit with the message.
     - The same `regen` after the "top-up": the waiting attempt was reviewed and became final, with no new request.
     - A new card interrupted the same way got no final image. An attempt that already has a verdict from the colour check is not re-reviewed, which is correct.
3. **One cost line in `summary.md`:** generation and QA from the attempt files, plus the other kinds from `costs.jsonl` (outpaint, vision), with nothing counted twice.
   - It says that `costs.jsonl` began in W023, so earlier extension and vision calls are missing.
   - Cosy Mystery now reads $3.50 + $0.229 = $3.73. Its `after_test.md` gives the whole cost: about $4.6 for the agent's run plus $0.23 to finish it.
4. **Codex entry point.** New `AGENTS.md` (read by Codex) points to the same skill. The README and `pipeline/README.md` name Claude Code as the entry point, with Codex through `AGENTS.md`.
5. **Pavel's question, an OpenAI (ChatGPT) API route for reviewers:** answered with a recommendation, see the reply. Not built.
6. **Reviewer test 2 started** from a fresh GitHub clone (`D:\test_task\reviewer_test2`, commit 19f0c4c), with the README's own example (space adventure, 3 variants).

---

## 2026-10-15 / W026 / The API route as a next step; macOS quick start; Excel optional

### Pavel's prompt (verbatim)

> Otherwise I'd list the API route as a next step in the README; the client code from our early tests is already in the repo.
>
> Ok, yeah let's just mention it as next step and not do it. Clearly Gemini and Codex route works.
>
> Another suggestion from model when I asked what would happen if reviewer would be on macos
> "
>
> Before handing it over, I'd make three small improvements:
>
> 1. Add a macOS quick-start: Python environment setup, dependency installation, setting `GEMINI_API_KEY`, and launching Claude Code from that terminal so it inherits the key.
> 2. Clearly mark the Excel workflow as optional and Windows-only, with a simple alternative: give ratings and corrections directly in the conversation.
> 3. Use the second reviewer test on a Mac, if available. Generate one card, run QA and framing, and build a preview window before spending on a complete set.
>
> For now, the accurate compatibility statement is: "Tested on Windows; the core pipeline is designed to work on macOS. Excel rating automation requires Windows."
> "
>
> Should Excel automation be built in a way that it would run on MacOS?

### Actions and results

1. **Windows-only code checked:**
   - the two Excel PowerShell scripts;
   - the key reader's registry lookup, which runs only on Windows;
   - fonts, which already fall back on macOS and Linux (W023).

   Everything else is Python and Pillow, and the ChatGPT route calls `codex`, which exists on macOS too.
2. **README (Russian):**
   - compatibility statement: tested on Windows; the core pipeline is meant to run on macOS and Linux but wasn't run there; the Excel workbook needs Windows;
   - setup for Windows and for macOS/Linux: venv, `pip install -r requirements.txt`, `export GEMINI_API_KEY`, start `claude` from the same terminal;
   - a $0.1 smoke test before a full run: one card generated, checked and framed. Verified once: $0.10, `final/A01.png`;
   - the rating workbook marked optional and Windows-only, with ratings in the conversation as the alternative;
   - new "Что дальше" (next steps) section:
     - the OpenAI API route;
     - the same QA judge for the ChatGPT route;
     - a rating table without Excel;
     - a run on macOS.
3. **`pipeline/README.md` and the skill:** the same macOS lines, and the rating loop's Excel steps marked optional. Without them, the agent takes scores and comments in the conversation and writes the redo list directly.
4. **Not done:** a run on a Mac (no Mac here).
5. **Pavel's question, a cross-platform Excel workbook:** recommended not now, see the reply.

---

## 2026-10-15 / W027 / The outside reviews go into the repository

### Pavel's prompt (verbatim)

> One question is still open from before: should the two outside reviews go into the repo under docs/reviews/, with a short note on what we fixed?
>
> Yes, let's add them

### Actions and results

1. **Both reviews moved into `docs/reviews/`, unchanged:**
   - `2026-10-15_readiness_review.md` (from another session, W023);
   - `2026-10-15_second_review.md` (pasted by Pavel, W025).

   They are no longer excluded from the repository.
2. **New `docs/reviews/README.md` (Russian):**
   - a table of every finding, with what was done and where (W/D);
   - what was not done, and why: the three-plus-one set split, the OpenAI API route, a rating table without Excel, a macOS run, the archive of intermediates, Miro.
3. **Pointers updated:** WORKLOG W023 and W025, the README structure and HISTORY.

---

## 2026-10-15 / W028 / Three reviewer steps: one-command setup, quick demonstration

### Pavel's prompt (verbatim)

> Pavel: Is there a way to shorten amount of steps needed for reviewer to generate?
>
> Other model:
> "Yes. The reviewer should see three steps: setup → describe the set → choose a result. Most of the previous list describes work the agent performs internally.
> The biggest improvement would be one setup command that:
> - Checks Python and creates the local environment.
> - Installs dependencies.
> - Checks whether the Gemini key is configured; prompts privately if missing.
> - Tests access and offers the small paid image test.
> - Clearly reports "Ready" or explains what needs fixing.
> Installing Claude Code, signing in and enabling Gemini billing remain external prerequisites for someone starting from scratch.
> Then the reviewer's experience becomes:
> Step	Reviewer action	Time
> 1. Prepare once	Download the repository, run setup and open the agent in that folder.	Target 5–10 minutes with prerequisites ready
> 2. Describe the set	"Make three cosy space-adventure variants."	1 minute of input; approximately 50–70 minutes processing
> 3. Choose	Review the previews and say "Use B."	3–5 minutes; agent exports everything
>
> For this submission, I'd add the setup helper and simplify the README around those three steps. Keep individual commands in an advanced section. The agent should automatically handle the smoke test, planning, validation, generation, framing, review and assembly—with the paid test clearly disclosed.
> This reduces reviewer effort, rather than generation time. To shorten the wait as well, offer an optional "preview only" mode using an existing plan: it skips the planning stage, which took about 17 minutes in the recorded test. Clearly distinguish that demonstration from testing a completely new theme.
> A hosted interface could remove local setup almost entirely, but it would introduce deployment, authentication and billing work. I wouldn't expand into that before submission."
>
> Yeah, we do not need hosted interface but other suggestion is good right?

### Actions and results

1. **New `prepare.py`** (standard library only, so it runs before anything is installed). Each step reports OK or what to fix, and it ends with "Ready":
   1. Python 3.9+.
   2. `.venv` with `requirements.txt`.
   3. The Gemini key: from the environment (or the Windows registry), or from `.env`. If there is none, it asks with hidden input and saves to `.env`, which git ignores; mode 600 on macOS and Linux.
   4. A free check of the key and of the two models the tool uses.
   5. An optional paid one-card test (about $0.10) in `sets/smoke-test/`.
   6. Whether the Codex CLI is installed.
   - `keys.py` now also reads `.env`.
   - `.gitignore` ignores `.venv/` and `sets/smoke-test/`.
   - **Tested** end to end in a scratch copy: all six steps; the one-card test passed QA and was framed, $0.10. Also tested: the `.env` parser, the cost parser, and a run skipping the paid test.
   - **Not tested:** installing Pillow into an empty `.venv`. The test venv saw the system Pillow, to avoid a download; that step is pip's standard install.
2. **README:** it now opens with "Быстрый старт: три шага" (prepare → describe → choose), with typical time and cost and the quick demonstration. The details (requirements, compatibility, manual setup, manual test, what the agent does) moved to "Подробнее о запуске".
3. **Skill: new "Before you start":**
   - use `.venv`'s Python when it exists;
   - point to `prepare.py` when the key check fails;
   - tell the designer the cost and time before generating (about $1.5 and 15–20 minutes per variant), without waiting for a confirmation;
   - the quick demonstration: copy an existing plan, start at validation, `--variants A`, and say it shows the pipeline, not planning.
4. **Not done:** a hosted interface, as agreed.

---

## 2026-10-15 / W029 / Miro: access checked, plan agreed, building the board

### Pavel's prompts (verbatim)

> ok, start building Miro, check if you have access to https://miro.com/app/board/uXjVEdsb-i4=/ first, confirm and let me know your plan briefly. i'll go to sleep and then we'll continue. next steps are: waiting for task #2 result (fix if needed), building Miro board narrative. Good suggestion about building it:
>
> "Build Miro around evidence, not the chronological log
> I'd use this sequence:
> 1. Final results and task requirements.
> 2. Reference principles, illustrated with actual examples.
> 3. Model comparisons and the chosen routes.
> 4. Workflow diagram, showing automated steps and human decisions.
> 5. Three before/after learning stories: backgrounds, framing, evaluation.
> 6. Final sets beside relevant references.
> 7. Fresh-run demonstration, costs, limitations and repository link.
> Preserve representative rejected images and before/after comparisons. Since intermediate images are excluded from Git, a private archive would support the brief's request for the iteration history; JSON logs alone cannot show visual failures."

> sounds good, looks like a solid plan. let's do it few with tweaks suggested by other model:
>
> "1. Give reviewers a clear reading order. Add a small "Начните здесь" note: Итог → Анализ → Как работает → Эксперименты → Проверка автономности. The main story should be understandable in 3–5 minutes; detailed iterations can sit below it.
> 2. State brief coverage explicitly beside the finals. Suggested wording: "4 жанровых набора: по 10 карточек, категории 1–4, без золотых карточек. Для каждой темы разработано 3 варианта; итоговые варианты выбраны продюсером." Present the fourth set as an additional result beyond the requested three.
> 3. Separate observations from your production rules. In "Анализ," distinguish: Observed in references: composition, lighting, palette distribution, framing. Adopted for the tool: default category mix, object-role checklist, motif frequency. This shows how you translated analysis into decisions without implying every rule came directly from the brief. Label model-estimated measurements as estimates.
> 4. Make the three improvement stories more distinct. Background variety: All-blue skies → context-appropriate environments and deliberate palette. Framing and extension: Crop damage → measured framing → rejected stretching → outpainting. Evaluation: Automatic QA → disagreement with your ratings → technical checks plus human selection. Stretching and outpainting belong with framing. This avoids telling the same story twice.
> 5. Put the caveats directly beside the headline numbers. 7/7: your preference in these comparisons; four final-set comparisons had ChatGPT consistently in the first position. 73% vs 60%: your acceptance among QA-passed versus QA-flagged cards; the flagged group contained only 10 cards. "Players wouldn't notice": a reviewer's judgement, not a player-test result. Small captions are enough. These qualifications make the evidence more credible.
> 6. Make autonomy evidence easy to inspect. Give each test a compact row: starting conditions → request → outputs → elapsed time/cost → interventions → remaining issues. Distinguish the original test result from fixes and finishing performed afterward. Only mark test 2 complete once its outcome is documented.
> 7. End with a practical handoff panel. Show the three reviewer actions: подготовить окружение → описать тему → выбрать вариант, with prerequisites, approximate runtime, estimated API cost and the private-repository access instructions. Keep the Gemini baseline and ChatGPT final-art route clearly labelled.
> For the iteration archive, prepare the ZIP, but keep the essential evidence visible on Miro. A reviewer should understand every major decision without downloading 450 MB. The archive can hold the exhaustive record, ideally with a short index.
> The most valuable addition is a consistent caption under each experiment: "Что заметил → что изменил → почему принял или отклонил результат." That will make your producer judgement visible throughout the board."

### Actions and results

1. **Board access checked** through the Miro connector, read-only. The board has four frames:
   - "Примеры карточек";
   - "Пример коллекции";
   - "Анализ принципов составления коллекций (идеи / арт)": empty except its header;
   - "Фрейм для описания хода работы и результатов": "Итоговые наборы" with the 4 empty templates, and "Описание хода работы", which is empty.

   Outside the frames are the three brief texts.
2. **Rules for the build:** in Russian; additions only; nothing existing is moved or deleted. The template sizes can't be read through the API (their width reads as 0), so a white panel covers the template area and the four filled windows sit on it in a 2×2 grid. The empty templates stay underneath, unchanged.
3. **First content on the board** (the results frame):
   - the panel;
   - the brief-coverage line in the suggested wording, with the fourth set as an addition;
   - the four final windows.

   One slip: the first two items were made outside the frame, because the frame wrapper lacked its title attribute. Moving items into a frame is refused, so these two items, made by the assistant seconds earlier and holding nothing else, were deleted and created again inside the frame. `image_create` takes centre coordinates; the first window was moved after the read-back showed this.
4. **"Описание хода работы"** (results frame), in the order the plan agreed:
   - **"1. Как работает":** a Mermaid flow of the tool. Blue steps are the agent and scripts; yellow steps are the human's.
   - **"2. Эксперименты":**
     - Models and routes, with the BENCH-03 sheet and Pavel's blind pick. The caveats sit beside the numbers: "players won't notice" is the rater's judgement; 7 of 7 is Pavel's preference, and ChatGPT stood first in the four final-set comparisons.
     - Three stories, each with before and after images and the same caption, «Что заметил → что изменил → почему принял»:
       - backgrounds and palette: all-blue skies, then scenes in their own setting. It also says that the four finals still lead with blue;
       - framing: crop damage, then measured framing; stretched edges rejected; outpainting;
       - evaluation: the judge against Pavel's ratings, 73% vs 60%, with the 10-card caveat; scripts check what can be measured, and the human chooses.
     - The final sets beside reference sets of the same kind, with a table measured by the same scripts as the references:
       - category as planned on 40 of 40;
       - extent medians 0.82–0.85;
       - 5–7 backdrop colours;
       - lead colour on 3–4 cards, blue in all four;
       - 1–2 same-colour neighbours;
       - 12 of 40 cards flagged.

       A caveat says these are estimates, and that framing aims at the reference medians, so that match is expected.
   - **"3. Проверка автономности":** one row per test (Western W018, test 1 W023, test 2 W030) with these columns:
     - starting conditions;
     - request;
     - result;
     - time and cost;
     - interventions;
     - fixes made afterwards.

     Each test's original result is kept apart from the fixes. Below the table are the 9 windows the agents made.
   - **"4. Как запустить":**
     - the three reviewer steps;
     - both routes, labelled;
     - the repository and how access works;
     - costs: about $26 of Gemini API over the project, an estimate from the logs;
     - limitations;
     - next steps.
5. **"Анализ" frame:**
   - a table of what the references show next to what the tool adopted, 11 topics. Estimates and interpretations are labelled;
   - the 12 production references by category;
   - the Beach and Road Trip windows, with captions.
6. **"Начните здесь"** panel above the frames:
   - the reading order (итог → анализ → как работает → эксперименты → проверка автономности → как запустить), each linked to its section;
   - the repository link.
7. **Frames grown downward only.** The areas below were checked empty first. The results frame is now 30,848 px tall, and "Анализ" went from 5,835 to 7,124. Nothing that was on the board before was moved or deleted. The tables are built from shapes, so their text matches the board's font sizes.
8. **Layout check.** The board is private and the in-app browser isn't signed in to Miro, so the check used Miro's measured text bounds:
   - three titles were wrapping into the line below and were widened;
   - one caption box was shortened.

   The flow diagram draws at its natural size, about 2,900 × 400 px. The API can't resize it, and it looks small next to the 48–56 px captions; scaling it up in Miro is left for Pavel.
9. **Archive of intermediate images:**
   - `D:\JOB2026HUNT\PLAYRIX_ARCHIVE\playrix-test-task-intermediates.zip`, 922 files, 678 MB;
   - `INDEX.md` inside and beside it lists every set, route and kind, with WORKLOG step numbers;
   - paths inside match the repository.

   Where to host it is Pavel's choice. Its size corrects the README's "about 450 MB", which predates both tests and the last cleanup rounds.
10. **Docs:** README (the intermediates' size and the archive), HISTORY (about $26 over the project, all three tests, the board).

---

## 2026-10-15 / W030 / Reviewer test 2 passed; its findings fixed

No new prompt from Pavel; this continues W029 ("waiting for task #2 result (fix if needed)").

### Results of test 2

- **Setup:** a fresh agent on a clean clone of GitHub commit 19f0c4c, with the README's own example (space adventure, "more objects than locations", 3 variants).
- **Outcome:** no crashes and no balance messages. It produced "Friendly Galaxy":
  - A, Moon Mission;
  - B, Friendly Planet (recommended);
  - C, Life in Orbit.
- **Numbers:** 30 cards, 41 images, 28 passed QA and 2 accepted with issues. About 45 minutes, $3.33.
- **Plan:** `Plan OK` on the first try, 0 warnings.
- **Review:** the agent's sheet review caught 6 cards that QA had passed and redrew them, editing their plan entries first:
  - paint-like food tubes;
  - a lumpy moon rock;
  - a Vespa repeating Love in the City's Vintage Scooter;
  - a cake-cover helmet;
  - a floor read as category 2;
  - a station like a steering wheel.

  It used `choose` once. The set and its notes are now in `sets/friendly-galaxy/`.

### Its findings and the fixes

1. **QA misses name-test failures and repeats from other sets.** The validator now warns when a card's object word repeats a card of a finished set (one with `final_set/sources.json`), with a stoplist of non-object words. On the galaxy plan as it was before the review, it flags exactly "Hover Scooter" against Vintage Scooter. The name test stays with the agent's sheet review, as the skill says.
2. **The cost line didn't match the docs and went stale after `card_metrics.py`.**
   - Fix: the docs now name the "Estimated cost" line.
   - `card_metrics.py plan` refreshes `summary.md`.
   - The "began before costs.jsonl" remark appears only for sets whose first request is more than 10 minutes older than their first log line. Cosy Mystery keeps it; Friendly Galaxy does not.
3. **Category 3 vs the measurement:** the rulebook and skill now prefer a wooden or textured tabletop or a podium over a plain glossy floor. The skill says the measured category is an estimate, to judge by eye and report.
4. **Wishes vs defaults:** the skill says producer wishes come before the defaults, with the "more objects than locations" example, and to note what changed.
5. **No ground (space, underwater, sky):**
   - `nature` now covers rocks, shells and celestial bodies;
   - ships and stations float as category 1;
   - category 4 stands on a planet surface, a deck or the sea floor;
   - open space counts as a saturated blue night.
6. **`reframe.py` without `--route`:** Gemini is now the default, and a missing route folder gives a clear message instead of a traceback.
7. **Smaller fixes:**
   - after regens or `choose`, the skill now lists what to re-run;
   - sheet titles shrink to fit;
   - the key check and the README say the balance isn't checked there;
   - the skill says the window's "+2", 8/25 and "Set 4/10" are the template's game UI;
   - the README and HISTORY list both tests, with a time table for each.

## 2026-10-15 / W031 / Board review: takeaways, a larger diagram, genre labels, comparable pairs

### Pavel's prompt (verbatim; the pasted review is stored in full in `docs/reviews/2026-10-15_board_review.md`)

> This is board review (from PDF file), let's do these improvements and then i'll review whole board

Asked whether, to split the process area into frames, the old copies may be deleted after recreating them, Pavel chose: "Don't split frames" (keep one long frame and apply only the other improvements).

### Actions and results

1. **Splitting into frames, tested and dropped.**
   - The Miro tools refuse to move an existing item into another frame ("target parent is not the actual parent").
   - So a split means recreating the sections and deleting the old copies. Pavel chose to keep the one frame.
   - The empty test frame the assistant had just made was deleted.
2. **Workflow diagram (review point 2).**
   - New hand-built flow of 6 stages in large type: theme and wishes → set plan → cards → framing and measures → review and windows → choice of variant.
   - Yellow marks the designer's or producer's decisions; blue marks the agent and scripts. A dashed loop shows optional ratings and notes leading to redraws.
   - The Mermaid diagram stays below it as the detailed scheme. Miro can't resize it.
3. **Takeaways (point 3).** A "Вывод: …" band sits above each comparison:
   - the models;
   - each of the three stories;
   - the comparison with the references;
   - the autonomy section.
4. **Framing pairs (point 3).** New image `framing_pairs.jpg`: two cards large, with the changed edges marked. Each shows the model's square with the old centre crop and the measured window, the old crop result, and the final card with the edges of the original picture.
   - Station Wagon: the centre crop cut the car on both sides. The measured window extends the background on every side; object 0.88 of the card.
   - Matching Mugs: the centre crop left 33% empty above. Measured: 21% above, object 0.85, table extended below.
   - The numbers come from `reframe.window()` on the stored boxes. It reproduces the logged overrun of every final card.
5. **Genre labels (point 4).** The four windows are slightly smaller (2,350 → 2,180 px). Under each: the genre and one line about the set's moment, taken from its plan.
6. **Two purposes of the reference comparison (point 5).**
   - New image `style_pairs.jpg`: four pairs, one per category, each with a similar subject:
     - Red Umbrella and the Beach sunshade;
     - Fruit Basket and the Countrystead apple basket;
     - Jewel Goblet and the Sports trophy;
     - Station Wagon and the Tour bus.

     None of these references is among the 12 sent with every request, and none is a gold card.
   - The full rows are now labelled as being for palette and rhythm only, with a note that they include gold character cards.
   - The section is renamed "Сравнение с референсами".
7. **Layout.**
   - Sections 2–4 moved down to make room; the frame is now 38,139 px tall. The area below was checked empty first.
   - Miro's measured bounds showed two problems, both fixed:
     - a heading wrapping into the band below;
     - images resized around their centres.
   - Nothing of Pavel's template was moved or deleted. Item ids stay the same, so the "Начните здесь" links still work.
8. **Export and entry point (point 6)** can't be fixed without splitting the frames. For Pavel:
   - in the Frames panel, put the results frame and "Анализ" first;
   - export only these frames;
   - send the repository link separately, since PDF links aren't clickable.

   The "Начните здесь" panel isn't in a frame, so it's not in the PDF.
9. **Docs:** the review is stored in `docs/reviews/`, and the reviews README lists what was done.

---

## 2026-10-15 / W032 / Reviewer test 3: a pirate set on the last of the Gemini balance

### Pavel's prompt (verbatim)

> I have €4.89 balance left, shall we run small test on remaining ones? Does not have to be logged on Miro but we can add to repo if there are any findings or results.
> This is input prompt as reviewer:
> Theme: Pirate Adventure (with One Piece elements where copyright is ok)

### Setup

- A clean clone of GitHub commit ef95070 in `D:\JOB2026HUNT\PLAYRIX_TEST3`, with no `.env`; the key comes from the user environment, as it would for a reviewer.
- A fresh agent with no conversation context works only in that folder and may not edit the tool or docs.
- It follows the README's three steps: `prepare.py` (the paid one-card test skipped), then the skill. It gets Pavel's request verbatim and keeps within about $4 by the tool's own estimate, because the balance is €4.89.
- It writes `sets/<set>/review_notes.md`:
  - the designer report;
  - how it handled the request for One Piece elements;
  - every problem met, by severity;
  - what would block a reviewer;
  - time and cost.
- This is the first reviewer test that includes `prepare.py`: test 2's clone (19f0c4c) predates it.

### Results

- **Run:** 11:47–12:44, about 57 minutes, of which planning took 32.5. Cost by the tool's line: $3.65 ($2.62 generation and QA, $0.92 background extension, $0.11 vision). The balance never ran out.
- **Setup:** `prepare.py` took 22 seconds. It made `.venv`, found the key without showing it, checked both models and, with "n" piped in, skipped the paid test card. There were no tool errors, and the plan validated on the first try.
- **Set "Pirates Ahoy!"** (`sets/pirates-ahoy/`, notes in `review_notes.md`):
  - A, Set Sail! (blue window), recommended;
  - B, Crew Feast (orange);
  - C, Pirate Port (violet).
  - QA: 28 passed, 2 accepted with issues. Two cards were redrawn after the sheet review.
- **The franchise request:** the agent used only genre tropes the series made popular but doesn't own:
  - a straw hat with a red band;
  - a giant meat on the bone;
  - tangerines;
  - a smiling dolphin figurehead;
  - a feast on deck.

  It avoided names, characters, the series' flag, its two ships, the devil fruit, the log pose, the snail phone, wanted posters and weapons. None of this reaches the image model, which gets only the card fields.
- **Its findings, by severity:**
  1. QA doesn't look for weapons or franchise designs: the first Deck Feast passed with something that read as a cannon. Fixed with a $0.10 regen.
  2. Framing zoomed 1.87× into the jetty of the 5★ Pirate Cove and lost the arch and the sky, with no warning. A free hand-set box fixed it, but the metrics, which measure with their own box, still flag the card.
  3. The banned words know fewer than 20 brands and films ("Luffy" and "One Piece" pass). The README's "banned words" wording overstated this.
  4. The overlap warning compares only the last word of names: Ship's Wheel against Spinning Wheel, but not a treasure chest against The Lost Island.
  5. Budget:
     - 3 variants is the smallest run;
     - background extension was needed on 24 of 30 framed cards, not "if needed";
     - 6 of the 10 paid retries were for framing alone, which framing would have fixed anyway;
     - a regen costs $0.10–0.16 with its framing.
  6. The docs didn't say which plan fields reach the image model.
  7. Smaller points:
     - there is no "sunrise" light;
     - logs stay empty until the end when output is redirected;
     - setcheck doesn't flag a lead colour below plan;
     - the skill doesn't say `card_metrics.py plan` is paid.

### What was changed before submission (docs and skill only; no code, D-036)

- **Skill:**
  - a rule for requests that name a franchise: genre tropes only, never names, characters or signature designs;
  - the list of fields the image model receives;
  - the banned-word list is short;
  - check overlaps by meaning, since the warning only matches the last word;
  - check weapons, alcohol and franchise designs on the sheets, since QA doesn't;
  - a zoom above about 1.5 on a scene means the box caught only part of it;
  - card_metrics is paid and measures with its own box;
  - corrected regen and background-extension costs, and three tests' time and cost.
- **README:**
  - test 3 in the tests list and in the time table;
  - background extension is needed by most cards (14–24 of 30 in the tests);
  - the banned-words line says it is a short list, and franchise designs are checked by the agent;
  - two new limitations;
  - test 3's code changes under "Что дальше".
- **HISTORY:** the third test, four agents in all, and about $30 of Gemini over the project.

The board is not updated, as Pavel said. It still says three tests and about $26.

---

---

## 2026-10-15 / W033 / Last accuracy pass on the board before submission

### Pavel's prompt (verbatim; the pasted list is stored in `docs/reviews/2026-10-15_board_review.md`, "Second pass")

> Last tweaks to Miro from other model before we submit task, I checked and I like it already enough to send.

### Actions and results

1. **Step 3 of the workflow diagram is labelled per route.**
   - Gemini: generation with 12 references → model judge → up to 2 retries.
   - ChatGPT: generation from references → background colour and framing checks → visual review.

   The section subtitle says step 3 depends on the route and the other steps are shared. All six boxes are now 520 px tall so the longer text fits.
2. **The repeat claim is softer.** Old: "предметы не повторяются; это проверяет валидатор плана". New: the validator warns about possible repeats by name, and the agent checks repeats in meaning. Two finals do share an object word (Storm Lantern, Fairy Lantern), so the old claim was too strong.
3. **The ChatGPT limit is an observation:** "в наших тестах — около 50 изображений за окно лимита; доступный объём может меняться". Changed on the board, in README and in HISTORY.
4. **A layout fault found and fixed.** Miro draws the detailed Mermaid scheme at about 5,364 × 1,105 px, not the estimated 400 px tall. After W031 it ran about 300 px into section 2.
   - Section 2 and everything below moved down 515 px; the frame is now 38,654 px.
   - Miro didn't confirm the move for 4 items. A read-back showed 3 still in place; one retry timed out, but a second read-back showed it had applied.
5. **The optional polish was not done.** Named frames per section were declined in W031. The board's start view is a Miro setting for Pavel.

---

## 2026-10-15 / W034 / README: Claude Code or Codex

### Pavel's prompt (verbatim)

> Pavel: Can reviewer run it not in Claude Code but with codex for example?
>
> Other model: "Yes—the repository already supports Codex. Claude Code isn’t required.
> Your [AGENTS.md (line 1)](D:/test_task/playrix-test-task-pavelnechval/AGENTS.md:1) explicitly directs Codex to the same card-set instructions. Codex automatically reads this file when working in the project, as confirmed by [OpenAI’s documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
> The reviewer would:
>
> 1. Download or clone the repository.
> 2. Run `python prepare.py` (`python3 prepare.py` on macOS), providing a funded Gemini API key.
> 3. Open the repository folder in Codex and describe the desired set.
> 4. Review the generated variants and choose one.
>
> Codex manages the work; Gemini still generates and checks the images. Using Codex as the agent does not automatically switch to the separate ChatGPT image-generation route.
> One documentation inconsistency remains: the README prerequisites and setup script’s final message still say “Claude Code,” although the README later explains that Codex works. Change those to “Claude Code or Codex” to remove doubt.
> This is supported by the current setup and instructions; I haven’t run a new complete Codex reviewer test in this check."
>
> Let's just tweak readme

### Actions and results

- README now says "Claude Code или Codex" in the tool line, the two prerequisite lists and the manual macOS/Linux setup (`claude    # или: codex`).
- The quick start adds three points:
  - Codex reaches the same skill through `AGENTS.md`; this was checked in W025;
  - the full reviewer tests ran in Claude Code;
  - with either agent Gemini draws and checks the images, and choosing Codex doesn't switch on the ChatGPT route.
- Pavel's follow-up (verbatim): "change prepare.py message too". The docstring and the final "Ready" message of `prepare.py` now say "Claude Code or Codex" too.

---

## 2026-10-15 / W035 / Independent review pass; the Gemini baseline beside the finals; README note on the finals' planning

### Pavel's prompts (verbatim)

> Check task: https://miro.com/app/board/uXjVEdsb-i4=/ and rate execution in Miro and Repo D:\test_task\playrix-test-task-pavelnechval as independent reviewer for Playrix. How would you rate it? Do not write anything, just suggest.
>
> Let's go

Then, on the proposed follow-up card:

> Do this task here: "Pre-submission accuracy fixes: board and repo"

### The review (read-only; a Claude session with no part in the build)

- Read: the brief (from the board), README, HISTORY, DECISIONS, PIPELINE, the skill, rulebook and set guidelines, both reviewer tests' notes, the three outside reviews, the final sheet and single final cards, the Gemini-route windows (Sunny Frontier, Cosy Mystery, Friendly Galaxy), the Road Trip reference window, and the whole results frame and "Анализ" frame of the board. Ran `cardgen.py validate` on all seven plans: every one prints `Plan OK`. Compiled every script; no secrets in the tree; the delivered clone matches `origin/main` (9bb20b2).
- Verdict given to Pavel: about 8.5 of 10. Scores out of 5: analysis 5, final art 4, comparison with references 4, architecture 4, autonomy for a designer 3.5, research and transparency 5, presentation 4.
- Gaps named, in order: the gallery is the ChatGPT route while the tool's automated route is Gemini, and the baseline was not shown beside the finals; 10 of the 12 category 1 finals use a ray backdrop where the references rotate rays, rings, waves and motifs; the four finals were planned before the set guidelines (lead colour blue in all four), said on the board but not in the README; no automated tests; a paid key is needed even for the demo; the W032 entry still read "pending".
- Not done from the list (Pavel's call, after submission): the category 1 backdrop variety rule and validator warning; tests for the validator, QA parsing and the empty-balance path; a zero-cost dry run.

### Actions and results

1. **The Gemini baseline now sits beside the finals on the board.** Source: `sets/ratings/chosen_windows_reframed.jpg` (W019: the four chosen variants by the Gemini route, after redo round 1 and the three measured remakes, reframed). The 2×2 sheet was re-stacked into one vertical strip of four windows (cut at the midpoints, 1110×3024 px, 845 KB; scratchpad script `make_strip.py`; not committed, since it is a re-layout of a committed file).
   - Image id 3458764687324077971, inside the results frame at centre (6563, 2710) frame-relative, width 1050 (about 2860 tall, so y 1280–4140), in the free right margin of the "Итог" panel (the panel is 120–7204 × 590–4210; the finals end at x 5922).
   - Caption shape id 3458764687323877537 at (5962, 870), 1226×390, 38 px: «Те же четыре варианта автоматическим маршрутом Gemini. Те же планы; после прогона переделаны 6 карточек по оценкам Павла и 3 по замерам, кадр по нормам референсов (W016–W019). Окна слева нарисованы ChatGPT, Павел выбрал их вслепую (W021). В The Lost Island здесь ещё Shovel: Explorer Hat появилась позже (W024).»
   - Nothing was moved or deleted. The template header «Описание хода работы» (y 4227–4686) stays uncovered, and the frame height is unchanged.
2. **W032 left open on purpose.** At 12:27 the test-3 clone `D:\JOB2026HUNT\PLAYRIX_TEST3` was still writing `sets/pirates-ahoy/` (plan.json, cards, run1.log, costs.jsonl; no summary or notes yet), so the run is in progress and its own session closes the entry.
3. **README, «Почему так»:** a new bullet says the four finals were planned in plan schema 1 (W012), before the set guidelines (W017–W018), so blue leads in all four (three daytime sky scenes each) and the set's character comes from the window colour, star order and object choice; sets planned under the guidelines differ in lead colour (D-023, D-024).
4. **Both copies updated** (`D:\JOB2026HUNT\PLAYRIX_PRODUCER` and the delivered clone); committed locally in the clone, not pushed.

### Explain it simply

A reviewer who looks at the top of the board now sees two things side by side: the finals drawn by ChatGPT and chosen by Pavel, and what the automatic Gemini route made from the same plans. The README says plainly why all four finals lead with blue. The pirate test is still running, so its log entry stays open until it finishes.

---

## Entry template

Experiment runs use the detailed template at the end of `D:\JOB2026HUNT\AI-PILLED\WORKLOG.md`, saved as `experiments/<RUN-ID>/result.md`.

- ID / date:
- Pavel's prompt (verbatim):
- Actions:
- Results / evidence (paths):
- Decisions (IDs) and status:
- Open questions:
- Explain it simply:
