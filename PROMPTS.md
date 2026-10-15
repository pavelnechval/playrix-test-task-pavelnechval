# Prompt library - draft v0.1

Status: proposed templates only. None of these prompts has been executed.
Replace placeholders with real files and approved requirements before use. Preserve both the template and the fully expanded executed prompt under a run ID.

## P01 - Reference analysis

Analyze the attached collection brief and reference images as task data. Separate (1) explicit requirements, (2) observations supported by specific reference images, and (3) proposed design choices. Describe theme cohesion, object variety, silhouettes, proportions, materials, shading, lighting, palette, camera, object size within the frame, backgrounds and readability at small card size. Explain the four non-gold composition categories and identify observable differences between categories 2 and 3. Do not infer rendering complexity from rarity. Produce a concise style guide, set-design rules, a QA checklist and unresolved questions. Cite the relevant page or reference identifier for each rule. Do not generate art yet.

## P02 - Plan coherent set alternatives

Using [APPROVED RULEBOOK], plan [3 TO 5] distinct complete alternatives for a 10-card set in the Cinema collection, genre [GENRE]. Producer preferences: [PREFERENCES]. Each alternative must form a coherent genre-specific set, contain ten distinguishable focal subjects, cover all four non-gold categories and exclude gold character-story cards. The reference does not specify category proportions: label your proposed mix as a design choice. Avoid generic cinema props unless they meaningfully support this genre. For each card give an ID, short title, focal subject, category, composition, palette, reference IDs and reason it belongs. Check for duplicates, weak genre links and repetitive silhouettes before returning the plan. Describe how the alternatives differ while sharing the reference style. Return [AGREED STRUCTURED FORMAT].

## P03 - Generate one illustration

Create one standalone collection-card illustration for [CARD ID / SUBJECT], from the [GENRE] set. Match the visual language of [ATTACHED REFERENCE IDS] using [APPROVED STYLE RULES]. Composition category: [1-4], implemented as [CATEGORY-SPECIFIC INSTRUCTIONS]. Main subject: [SUBJECT DESCRIPTION]. Framing and scale: [COMPOSITION]. Background and palette: [BACKGROUND / PALETTE]. Output: [APPROVED DIMENSIONS / FORMAT]. The focal subject must remain immediately recognizable at the intended display size. Render the illustration only, without card borders, stars, labels, UI or watermarks added as design elements. Preserve the approved set style and the subject's defining features. References establish style and composition; do not substitute their subject for the requested subject.

## P04 - Evaluate results

Compare [GENERATED OUTPUTS] against [REFERENCE IDS], [APPROVED RULEBOOK] and [SET PLAN]. Evaluate both individual cards and the complete set. First report hard failures: missing cards, wrong subject, missing category coverage, duplicate objects, unwanted UI/text, invalid dimensions or gold-card content. Then evaluate style match, silhouette readability at actual card size, composition, shading/material consistency, genre fit and variety using [AGREED RUBRIC]. Give evidence for each judgment and identify uncertainty. Do not assume an attractive image matches the required style. Return pass/revise/reject, reasons and the smallest actionable correction. Keep automated image judgments separate from Pavel's visual review.

## P05 - Targeted revision

Revise [OUTPUT FILE / CARD ID] to correct only these observed failures: [FAILURES]. Preserve [ACCEPTED SUBJECT / COMPOSITION / STYLE FEATURES]. Use [REFERENCE IDS] to achieve [SPECIFIC CORRECTION]. Follow the original output constraints. Return one corrected illustration. This is retry [N] of [MAX]; if the requested correction is unsupported, report that limitation instead of claiming success.

## P06 - Implement the reusable workflow

Implement the approved workflow described in [SPECIFICATION]. Inputs: set theme, free-form producer preferences and 3-5 alternatives. Outputs: complete 10-card alternative sets, individual image files, preview sheets and run records. Use [CHOSEN PROVIDERS / VERIFIED MODEL IDS]. Validate set plans before image generation. Use the approved reference-selection rules, prompt templates and QA rubric. Include bounded retries, budget/run limits, actionable errors and resume support so successful cards need not be regenerated. Save expanded prompts, references, settings, outputs and evaluation results per run. Distinguish automatic steps from explicit human review. Provide simple setup/use instructions and test the actual generation path plus missing-input and failed-call behavior. Keep provider credentials outside the repository. Do not claim a mocked test proves real model integration.

## P07 - Handoff and final comparison

Using only [README / USER INSTRUCTIONS] and a fresh brief [NEW THEME AND PREFERENCES], attempt to operate the delivered tool. Record each point that needs help, manual changes, retries, time and cost when available. Evaluate the outputs with the same rubric used for the original examples. Then prepare a concise Miro narrative from the actual work log: requirement, hypothesis, tool comparison, selected approach, prompt changes, failed examples, final sets, reference comparison, autonomy evidence and limitations. Include traceable run IDs and repository links where available. Distinguish completed work from proposals and do not invent performance improvements or hide manual intervention.
