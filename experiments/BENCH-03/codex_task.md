# BENCH-03, ChatGPT arm via Codex (no API credits)

How to use:

1. Open the Codex app on the folder `D:\JOB2026HUNT\PLAYRIX_PRODUCER`.
2. Paste everything below the line into a new Codex task.
3. When it finishes, tell Claude "chatgpt samples done".

Image generation in Codex runs on your ChatGPT plan, the same route as GPT-001.

---

You are helping with an image-generation benchmark. Use your built-in image generation tool. Do not edit, move or delete any existing file. Only create the 8 output images and the log file described below.

For each target T1, T2, T3, T4, and for each sample a and b (8 images in total):

1. Open `experiments/BENCH-03/prompts/openai/<target>.md`. Use only the text after the line `Prompt:`, exactly as written, with no additions or rewording.
2. Generate one image with your image tool. Pass these 12 reference images, in this order:
   `experiments/BENCH-03/refs/R1_r02c07.png`, `R2_r02c09.png`, `R3_r05c01.png`, `R4_r02c04.png`, `R5_r03c07.png`, `R6_r05c04.png`, `R7_r01c06.png`, `R8_r05c10.png`, `R9_r02c02.png`, `R10_r05c03.png`, `R11_r06c09.png`, `R12_r06c01.png` (all in `experiments/BENCH-03/refs/`).
   - If the tool cannot take 12 reference images, pass the single file `experiments/BENCH-03/refs/refs_sheet_3x4.png` instead.
   - In that case, put this sentence before the prompt: "The 12 reference cards are combined in one sheet: row 1 = Images 1-3, row 2 = Images 4-6, row 3 = Images 7-9, row 4 = Images 10-12, left to right."
3. Copy the generated image to `experiments/BENCH-03/outputs/chatgpt_<target><sample>.png`, for example `chatgpt_T1a.png`. Sample b must be a fresh generation, not an edit of sample a.
4. Make one attempt per image. Do not regenerate, crop or retouch an image because of how it looks. If a generation fails with an error, retry once and record it.

After all 8 images, write `experiments/BENCH-03/runs/chatgpt_log.md`. For each image, record:

- target and sample
- the image tool's name
- the model name or version if the tool reports it; otherwise write "not exposed"
- output size in pixels
- the original generated file path
- whether all 12 references were accepted, or the sheet fallback was used
- retries and errors
- start and end time

Do not include any credentials or tokens.
