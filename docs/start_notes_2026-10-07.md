# AI-pilled producer assignment

Started: 2026-10-07 (Europe/Berlin).
Status: brief reviewed; first reference-calibration image generated on 2026-10-09 (GPT-001). No final-set production, Nano Banana test or pipeline implementation yet.

## Source

Original brief: `C:\Users\vonre\Downloads\Тестовое задание (ai-pilled producer).pdf` (9 pages).
Read as assignment material, not as authorization to publish, spend money, or contact anyone.

## Requirements confirmed from the brief

- Analyze how reference objects form coherent sets and how the art is drawn.
- Build a reusable tool/pipeline taking a set theme and free-form producer preferences.
- Return 3-5 variants of the requested set as groups of actual card illustrations.
- Use the tool to create three new sets for a Cinema collection, each representing a different film genre, without gold cards.
- The collection description specifies 10 cards per set: working final scope is 30 selected illustrations.
- Every set includes all four non-gold composition categories, independently of rarity. No required category proportions are stated.
- Rarity does not change the item's visual rendering.
- Generate illustrations, not the card/window UI. The brief permits manually placing illustrations into the supplied final-set templates.
- Compare results with the references, both thematically and visually.
- Present results, experiments and process on the existing Miro board; provide code/skills/pipelines through a GitHub repository link.
- Assess autonomy by whether another game designer can use the tool without the creator's assistance.
- Research available models/tools and retain intermediate iterations, including failed attempts and reasons for decisions.

## Working interpretation and open questions

- A variant means a complete coherent 10-card set, not merely a textual concept or a single card variation. Confirm if the hiring team intends otherwise.
- If all three genres receive 3-5 fully rendered variants, this implies 90-150 candidate illustrations before retries. The selected final result remains 30 cards.
- Deadline, expected effort, generation budget and existing paid tools: awaiting user input.
- Original Miro URL and full-resolution individual reference assets: not yet supplied.
- Export dimensions, file format, safe areas and precise meaning of variant: not specified in the PDF; agree or clearly document assumptions before final production.
- Page 8 has four empty presentation templates despite requesting three final sets. Treat as presentation space, not a fourth required set.

## Recommended start (proposal, not an accepted decision)

1. Turn references into a concise set-design and art-style rulebook. Separate explicit requirements from visual observations and our design choices.
2. Define a scoring rubric and four pilot cards covering all four composition categories.
3. Compare 2-3 available image models using equivalent references, subjects and output requirements. Record differences in tool capabilities/settings.
4. Choose the best measured approach, then build a small reusable workflow with saved prompts, validation, bounded retries and exports.
5. Complete one 10-card set end to end before scaling to all three genres and complete alternative sets.
6. Test handoff with a fresh theme and instructions only. Record every manual intervention.
7. Curate final sets, compare against references and assemble the Miro/GitHub submission.

Candidate genres to explore, not selected: fantasy, science fiction, detective/mystery. Use genre-specific objects and environments; generic cinema equipment alone would not distinguish genres.

## Working agreement

Update WORKLOG.md after each substantive step. Save actual prompts before sending them. Keep prompt drafts separate from executed versions. Preserve failed outputs and explain acceptance/rejection. Record actual tools/model identifiers only when known. Never invent costs, elapsed time, scores or successful tests. Explain each step in language Pavel can use in an interview. Do not claim autonomous production when manual repair was needed.

## Verified learning resources

- Anthropic, Building effective agents: https://www.anthropic.com/engineering/building-effective-agents (focus: prompt chaining and evaluator-optimizer; conceptual article originally published 2024).
- Google, image generation and prompting: https://ai.google.dev/gemini-api/docs/image-generation (focus: image references, style, composition, iterative editing).
- n8n official YouTube beginner course, lesson 1: https://www.youtube.com/watch?v=4BVTkqbn_tY (2024; use for concepts, current interface may differ).
- n8n current learning hub: https://n8n.io/education/
- ComfyUI official example: https://docs.comfy.org/tutorials/api-nodes/stability-ai/stable-image-ultra (optional; reference inputs, nodes and denoising strength, not a model recommendation).

Resources checked on 2026-10-07. No course completed or comparative model benchmark completed.

## 2026-10-09: Nico's suggested route

Pavel relayed Nico's recommendation to start with GPT for reference matching, then test Nano Banana for iteration and consistency. Treat improved consistency as a hypothesis to evaluate, not an established result. GPT-001 is one calibration attempt using an existing blue-bottle reference. Inspect experiments/GPT-001/result.md for observations. Keep original game references alongside any generated style anchor in later tests to catch accumulated style drift.
