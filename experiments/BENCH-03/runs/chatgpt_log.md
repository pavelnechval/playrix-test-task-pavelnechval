# BENCH-03 ChatGPT image-generation log

Date: 2026-10-13. Local timezone: Europe/Berlin (CEST, UTC+02:00).

Eight fresh image generations were completed using the built-in image_gen.imagegen tool. Model name/version: not exposed. Each sample b was a separate call using only the reference sheet, never sample a as an input.

Prompts: the exact text after the `Prompt:` line in `experiments/BENCH-03/prompts/openai/T1.md`, `T2.md`, `T3.md`, and `T4.md`, including original whitespace. The only added text was the user-specified fallback sentence:

> The 12 reference cards are combined in one sheet: row 1 = Images 1-3, row 2 = Images 4-6, row 3 = Images 7-9, row 4 = Images 10-12, left to right.

References: sheet fallback (`experiments/BENCH-03/refs/refs_sheet_3x4.png`) for every successful generation. The first T1a request supplied the 12 reference files in the specified order and was rejected before generation because the tool accepts at most 5 paths. T1a was retried once with the sheet. All remaining samples used the sheet directly.

No image was regenerated for appearance, cropped, retouched, or resized. PNG dimensions below were read from the delivered file headers. Every output was copied without overwriting, and source/output SHA-256 hashes matched. Existing files and original generated images were left in place.

Start/end times bracket the image-tool calls (copying and verification occurred afterward). T1a start includes the rejected initial request; its successful retry start is recorded separately.

## T1a

- Target: T1
- Sample: a
- Image tool: image_gen.imagegen
- Model name/version: not exposed
- Output size: 1028 x 1530 pixels
- Output file: `experiments/BENCH-03/outputs/chatgpt_T1a.png`
- Original generated file path: `C:\Users\vonre\.codex\generated_images\01a136ab-c956-7e81-9b70-34af0926cd06\exec-e0590e18-aeb2-45d4-ab16-0da49c6e4c13.png`
- References: sheet fallback; all 12 separate references were not accepted
- Retries: 1
- Errors: `referenced_image_paths` must contain at most 5 paths
- Start: 2026-10-13T21:18:49+02:00 (Europe/Berlin); 2026-10-13 19:18:49 UTC
- End: 2026-10-13T21:19:32+02:00 (Europe/Berlin); 2026-10-13 19:19:32 UTC
- Successful retry start: 2026-10-13T21:19:09+02:00 (Europe/Berlin); 2026-10-13 19:19:09 UTC
- SHA-256 (identical source and output): `7D51DBBEF60318EE8BD85C3D30960E6D352F59E872974A53F927B2D0837DADC7`

## T1b

- Target: T1
- Sample: b
- Image tool: image_gen.imagegen
- Model name/version: not exposed
- Output size: 1028 x 1530 pixels
- Output file: `experiments/BENCH-03/outputs/chatgpt_T1b.png`
- Original generated file path: `C:\Users\vonre\.codex\generated_images\01a136ab-c956-7e81-9b70-34af0926cd06\exec-b37c147a-4ac1-441d-9be3-75c7668203ef.png`
- References: sheet fallback; all 12 separate references were not accepted
- Retries: 0
- Errors: none
- Start: 2026-10-13T21:20:13+02:00 (Europe/Berlin); 2026-10-13 19:20:13 UTC
- End: 2026-10-13T21:20:36+02:00 (Europe/Berlin); 2026-10-13 19:20:36 UTC
- SHA-256 (identical source and output): `8FA64B87F8463AD667A41D57082872B4438817FCFC2BFAA70B42C42C7C7EE15C`

## T2a

- Target: T2
- Sample: a
- Image tool: image_gen.imagegen
- Model name/version: not exposed
- Output size: 1028 x 1530 pixels
- Output file: `experiments/BENCH-03/outputs/chatgpt_T2a.png`
- Original generated file path: `C:\Users\vonre\.codex\generated_images\01a136ab-c956-7e81-9b70-34af0926cd06\exec-75b8b685-abf4-46f6-96f2-8eb2645bb60f.png`
- References: sheet fallback; all 12 separate references were not accepted
- Retries: 0
- Errors: none
- Start: 2026-10-13T21:20:38+02:00 (Europe/Berlin); 2026-10-13 19:20:38 UTC
- End: 2026-10-13T21:21:02+02:00 (Europe/Berlin); 2026-10-13 19:21:02 UTC
- SHA-256 (identical source and output): `C76B2C4F5BC5836556AAA2FAA123ECE572878BB0B874F624F251398581EB8A19`

## T2b

- Target: T2
- Sample: b
- Image tool: image_gen.imagegen
- Model name/version: not exposed
- Output size: 1028 x 1529 pixels
- Output file: `experiments/BENCH-03/outputs/chatgpt_T2b.png`
- Original generated file path: `C:\Users\vonre\.codex\generated_images\01a136ab-c956-7e81-9b70-34af0926cd06\exec-26ccec61-9651-4a2f-93f9-cacbc6be2aed.png`
- References: sheet fallback; all 12 separate references were not accepted
- Retries: 0
- Errors: none
- Start: 2026-10-13T21:21:04+02:00 (Europe/Berlin); 2026-10-13 19:21:04 UTC
- End: 2026-10-13T21:21:36+02:00 (Europe/Berlin); 2026-10-13 19:21:36 UTC
- SHA-256 (identical source and output): `2B921A3CFD91714866A4F3E5645473D8AC73DCAED82C07ECC9466032B2392454`

## T3a

- Target: T3
- Sample: a
- Image tool: image_gen.imagegen
- Model name/version: not exposed
- Output size: 1028 x 1530 pixels
- Output file: `experiments/BENCH-03/outputs/chatgpt_T3a.png`
- Original generated file path: `C:\Users\vonre\.codex\generated_images\01a136ab-c956-7e81-9b70-34af0926cd06\exec-92615f92-4030-4e81-bb90-f66475a3bd5f.png`
- References: sheet fallback; all 12 separate references were not accepted
- Retries: 0
- Errors: none
- Start: 2026-10-13T21:21:41+02:00 (Europe/Berlin); 2026-10-13 19:21:41 UTC
- End: 2026-10-13T21:22:08+02:00 (Europe/Berlin); 2026-10-13 19:22:08 UTC
- SHA-256 (identical source and output): `F984907F4FBB23E4CD4C0530703A41E3E7053E2BAF9513C01EC253A025878F96`

## T3b

- Target: T3
- Sample: b
- Image tool: image_gen.imagegen
- Model name/version: not exposed
- Output size: 1028 x 1530 pixels
- Output file: `experiments/BENCH-03/outputs/chatgpt_T3b.png`
- Original generated file path: `C:\Users\vonre\.codex\generated_images\01a136ab-c956-7e81-9b70-34af0926cd06\exec-f68a95e5-d084-4601-b292-eb1216918a7d.png`
- References: sheet fallback; all 12 separate references were not accepted
- Retries: 0
- Errors: none
- Start: 2026-10-13T21:22:11+02:00 (Europe/Berlin); 2026-10-13 19:22:11 UTC
- End: 2026-10-13T21:22:42+02:00 (Europe/Berlin); 2026-10-13 19:22:42 UTC
- SHA-256 (identical source and output): `8AE76E7E191BB1F43CC54E94BB7EA5AAFB4CA1C455229B78011FF78EFED7FB3E`

## T4a

- Target: T4
- Sample: a
- Image tool: image_gen.imagegen
- Model name/version: not exposed
- Output size: 1028 x 1530 pixels
- Output file: `experiments/BENCH-03/outputs/chatgpt_T4a.png`
- Original generated file path: `C:\Users\vonre\.codex\generated_images\01a136ab-c956-7e81-9b70-34af0926cd06\exec-db5cd6b1-d371-41d5-8495-4f02fd6a43fd.png`
- References: sheet fallback; all 12 separate references were not accepted
- Retries: 0
- Errors: none
- Start: 2026-10-13T21:22:45+02:00 (Europe/Berlin); 2026-10-13 19:22:45 UTC
- End: 2026-10-13T21:23:08+02:00 (Europe/Berlin); 2026-10-13 19:23:08 UTC
- SHA-256 (identical source and output): `D3B58569A7D95E4C40F4288A193850CB1624A07E9CE91F09C9F7E35116D6C864`

## T4b

- Target: T4
- Sample: b
- Image tool: image_gen.imagegen
- Model name/version: not exposed
- Output size: 1028 x 1530 pixels
- Output file: `experiments/BENCH-03/outputs/chatgpt_T4b.png`
- Original generated file path: `C:\Users\vonre\.codex\generated_images\01a136ab-c956-7e81-9b70-34af0926cd06\exec-2b2618df-e7a3-4b47-9e1d-d8d353136f28.png`
- References: sheet fallback; all 12 separate references were not accepted
- Retries: 0
- Errors: none
- Start: 2026-10-13T21:23:10+02:00 (Europe/Berlin); 2026-10-13 19:23:10 UTC
- End: 2026-10-13T21:23:34+02:00 (Europe/Berlin); 2026-10-13 19:23:34 UTC
- SHA-256 (identical source and output): `210ED9DC5ADD25D353F5521D657D4101D094E23DED78AF8A651768051B2BC0D7`
