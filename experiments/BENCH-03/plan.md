# BENCH-03: prompt v3, Nano Banana 2.1 vs GPT Image 2.5 (plan)

**Status:** prepared on 2026-10-13 (W008). No API calls yet. Running it needs:

- Pavel's OK for the Nano Banana arm;
- an `OPENAI_API_KEY` for the GPT arm.

## Questions

1. Does prompt v3 (Pavel's and the external model's BENCH-02 notes) raise the pass rate beyond BENCH-02's 3/8 (Pavel) and 4/8 (external)?
2. Does GPT Image 2.5 match the style better than Nano Banana 2.1 under the same prompt and references? This is Nico's original suggestion, now testable.

## Design

**Unchanged from BENCH-02:**

- the 4 hidden targets and their subject text;
- the 12-card reference pack;
- 2 samples per target.

**Arms:**

| Arm | Model | Output | Images | Cost |
|---|---|---|---|---|
| nb21 | `gemini-nano-banana-2.1` | 1:1, 1K | 8 | ≈ $0.45 (measured rate from BENCH-02) |
| gpt25s | `gpt-image-2.5-sunburst` | `1024x1136` (card aspect ≈ 0.9; 2.5 supports custom sizes), quality `high` | 8 | Unknown until the first call |
| gpt2 | `gpt-image-2` | `1024x1024`, `high` | — | Fallback only, if 2.5 is unavailable to the account |

- **chatgpt arm (W009, used instead of gpt25s while there are no API credits):**
  - GPT Image runs through Pavel's ChatGPT plan, using Codex's built-in image tool (the GPT-001 route).
  - Pavel runs `codex_task.md` in the Codex app. It uses the same `prompts/openai` text and the same 12 references, with `refs/refs_sheet_3x4.png` as the fallback if the tool can't take 12 images.
  - Outputs: `outputs/chatgpt_<T><a|b>.png`. Log: `runs/chatgpt_log.md`.
  - Limitations:
    - the model version is not exposed;
    - size and quality can't be set;
    - plan limits apply;
    - it is semi-manual (Pavel starts it).
  - The sheets pick these outputs up automatically and blind them like the rest.
  - **What happened (from Codex's `runs/chatgpt_log.md`):**
    - Codex's `image_gen.imagegen` accepts **at most 5 reference paths**, so all 8 images used the 12-card sheet fallback plus the extra sentence explaining the sheet.
    - Outputs are portrait, **1028×1530** (≈2:3). The sheets centre-crop them to the card aspect (0.896), which removes about a quarter of the height.
    - Model not exposed. 23–43 s per image. One retry, caused by the 5-path limit.
  - **Confounds versus nb21:** sheet versus separate references, portrait output and crop, unknown model version. Results show what the ChatGPT-plan route can do, not pure GPT Image 2.5 under identical conditions.
- **GPT Image cost estimate:** reported rates are $0.21 per 1024² image at high quality, plus reference input at $8 per 1M image tokens. Rough guess: $0.25–0.60 per image. It is measured from `usage` on the first call.
- **Prompt formats:** Gemini gets the references labelled in place. OpenAI gets the same labels as a numbered image list. See `prompts/gemini` and `prompts/openai`.
- **Blind sheets:** every output gets a random code (`blind_key.json`), so Pavel, the external model and the assistant all score blind.

## Measures

- **Primary (D-015):** pass rate, the share of images where players would not notice. This is the brief's own test.
- **Secondary:**
  - style 1–5;
  - notes, turned into prompt or QA rules;
  - cost and time per image;
  - consistency between samples a and b.

## Commands

```
python -I pipeline/openai_image.py check                 # free; after OPENAI_API_KEY is set
python -I experiments/BENCH-03/bench.py run nb21          # ≈ $0.45
python -I experiments/BENCH-03/bench.py run gpt25s        # first call shows the real cost
python -I experiments/BENCH-03/bench.py sheets
```
