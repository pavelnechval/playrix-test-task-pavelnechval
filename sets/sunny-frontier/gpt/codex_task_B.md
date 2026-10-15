You are generating card illustrations with your built-in image generation tool. Work only inside sets/sunny-frontier/gpt/. Do not edit, move or delete any other file, and do not change the prompt files.

For each card below, in this order:
1. Read the prompt file. Use the text after the line "Prompt:" exactly as written, with no additions or rewording.
2. Call the image tool once with that prompt and with the reference image paths listed in the file, in that order (4 paths). If the tool lets you choose a size or aspect ratio, choose square (1:1).
3. Copy the generated image, unchanged, to the raw path given below. Never crop, resize, retouch or edit an image.
4. Make one attempt per card. Do not regenerate because of how an image looks. If the tool returns an error, retry once and record it.

Cards (prompt file -> output path):
- B01: sets/sunny-frontier/gpt/prompts/B01.md -> sets/sunny-frontier/gpt/raw/B01.png
- B02: sets/sunny-frontier/gpt/prompts/B02.md -> sets/sunny-frontier/gpt/raw/B02.png
- B03: sets/sunny-frontier/gpt/prompts/B03.md -> sets/sunny-frontier/gpt/raw/B03.png
- B04: sets/sunny-frontier/gpt/prompts/B04.md -> sets/sunny-frontier/gpt/raw/B04.png
- B05: sets/sunny-frontier/gpt/prompts/B05.md -> sets/sunny-frontier/gpt/raw/B05.png
- B06: sets/sunny-frontier/gpt/prompts/B06.md -> sets/sunny-frontier/gpt/raw/B06.png
- B07: sets/sunny-frontier/gpt/prompts/B07.md -> sets/sunny-frontier/gpt/raw/B07.png
- B08: sets/sunny-frontier/gpt/prompts/B08.md -> sets/sunny-frontier/gpt/raw/B08.png
- B09: sets/sunny-frontier/gpt/prompts/B09.md -> sets/sunny-frontier/gpt/raw/B09.png
- B10: sets/sunny-frontier/gpt/prompts/B10.md -> sets/sunny-frontier/gpt/raw/B10.png

When all cards are done, write sets/sunny-frontier/gpt/codex_log_B.md with one entry per card: card id, image tool name, model name or version if the tool reports it (otherwise "not exposed"), output size in pixels, the original generated file path, retries and errors, start and end time. Do not include any credentials or tokens.
