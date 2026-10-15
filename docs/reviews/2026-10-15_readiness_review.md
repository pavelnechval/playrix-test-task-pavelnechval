# Submission readiness review - 2026-10-15

## Request and scope

Pavel asked: "Analyze PLAYRIX_PRODUCER folder and it's context so far, how are we doing on test in your opinion? Break it down by category and suggest improvements we can do at this stage (we're building repo and soon will write to Miro)"

Reviewed the root documentation, decision register, recent work log, skill instructions, card/set rules, rating analysis, current final gallery and reference sheet, source manifests, metrics, generation/validation code, framing and ChatGPT route. Also inspected the existing clean-copy reviewer test's summary. This is a readiness assessment, not a full code/security audit or independent player study.

No paid API calls or new artwork were made. No existing project code, prompts or final artwork was changed. This report is the only retained review artifact.

## Overall judgment

Strong production experiment and credible final artwork. Highest remaining value: dependable handoff, accurate claims, and clear presentation. Avoid broad redraws, more genres, model training, a new frontend or architectural rewrites at this stage.

Subjective readiness scores (not a hiring prediction):

| Category | /5 | Assessment |
|---|---|---|
| Brief coverage and final assets | 4.5 | Four complete final sets, three alternatives per plan, required non-gold categories covered. Clarify three required headline sets versus the extra set. |
| Product/reference analysis | 4.5 | Set coherence, mood, roles, palette and category grammar translated into rules. Distinguish assignment requirements from observed patterns and chosen heuristics. |
| Final art and consistency | 4 | Strong casual-game fit; some environmental detail and remaining framing exceptions. No need for general regeneration. |
| Model experimentation | 4.5 | Three benchmarks, 120-card ratings, rejected hypotheses and documented model-route change. Keep small-sample and position-bias limitations visible. |
| Pipeline reliability/autonomy | 3.5 | Real generation, checking, retries, framing and new-theme operation. Two confirmed validation/status issues and reviewer handoff tests still need closure. |
| Reproducibility/reviewer onboarding | 3.5 | Clear folder structure and provenance; route parity, excluded intermediate inputs and environment assumptions require explicit guidance. |
| Miro presentation readiness | 3 | Most evidence exists locally; a concise, navigable final story remains to be assembled. Miro itself was not inspected in this review. |

## Checks actually performed

- All five existing set plans returned zero validation errors; warnings were LC 1, OG 5, PP 2, Western 0 and LI 6.
- Each of the four final_set folders contains ten PNGs, all 430x480.
- Each selected final variant contains C1=3, C2=2, C3=2, C4=3; no category 5.
- All source image paths referenced by the four final_set/sources.json files exist locally.
- Reference metrics contain C1=36, C2=20, C3=27, C4=46 and C5=31. Category-specific non-gold norms filter to categories 1-4.
- Existing clean-copy Cosy Mystery summary reports 30 output cards: 28 QA-passed and two accepted_with_issues, 47 generated images, estimated $2.89 with QA prices explicitly unverified. This is not proof that final handoff has passed: no completed review_notes.md was found at inspection time.
- Git status showed the submission files as untracked at inspection time.
- Reviewed final_sets_W022.jpg and production_refs_sheet.png visually.

## Fix before handoff

### 1. QA failure is currently recorded as a successful check

Location: pipeline/cardgen.py, produce_card(), exception around review().

When the vision review raises GeminiError, the code creates {"pass": true, "qa_error": ...}. With a successful/no-op background check, the card is written as status "passed".

Confirmed offline with mocked generation/review and an existing image in a temporary directory: a simulated QA outage returned status passed and qa_record {pass: true, qa_error: "simulated QA outage"}. The first test harness attempt lacked a refs stub; the corrected test reproduced the defect. No actual model service was called.

Recommendation: retain the usable image but mark it unchecked/review_required, retry QA separately within a limit, and report the failure. Do not equate a missing review with approval. Add a regression check for this exact case.

### 2. Category 5 is not explicitly rejected by plan validation

Location: pipeline/cardgen.py, validate().

The validator checks counts for categories 1-4 but does not require each card's category to be in that set. In an in-memory copy of the valid Western plan, changing one C1 card to category 5 still returned zero errors because C1 remained present twice.

Recommendation: explicitly require integer category in {1,2,3,4}; test category 5 and an invalid category value. Existing final plans themselves are valid.

## Make tool and gallery expectations match

- The final gallery uses ChatGPT, while the default skill generates with Gemini. README discloses this, but the reviewer workflow must make the distinction immediately clear.
- ChatGPT generation has no equivalent automatic per-card vision QA/retry loop; codex_images.py explicitly documents this. Apply the common post-generation checks or clearly list what differs.
- Give the reviewer an explicit choice: automated Gemini baseline versus the ChatGPT route used for final art. Do not quietly imply that the baseline necessarily reproduces the selected gallery quality.
- Complete the two already-planned reviewer tests. Record exact checkout/version, supplied prompt, dependencies, outputs, unresolved issues, elapsed time, estimated cost, manual interventions and any tool-code changes (ideally zero during the run).
- Define successful handoff as complete usable outputs with honest status reporting; three plans or 30 QA passes alone are insufficient.

## Evidence and wording improvements

- "Players would not notice" is a rater's prediction, not player-test evidence.
- QA passed cards had a 73% Pavel acceptance rate versus 60% among only ten flagged cards. Say QA was insufficient as a taste/selection proxy in this sample; do not claim it has zero predictive information.
- The comparison of cards needing retries with first-attempt cards is not a causal test of retry effectiveness. Harder cards are selected into the retry group, and original-vs-final paired ratings are absent.
- Comparing benchmark acceptance with production-card acceptance cannot establish that scaling did not reduce quality: tasks and subjects differ.
- 7/7 set preferences are Pavel's preferences on these comparisons, not universal model superiority. Preserve the four-set position-bias caveat.
- "Detail lost" is a pixel edge-strength difference after downsampling, not a percentage of perceived information lost. The two-point acceptance rule is a chosen heuristic; visual judgment should remain decisive.
- Category recognition and subject boxes are model estimates; pixel dimensions and file counts are directly measured. Label these separately.
- Report API costs as estimates where prices are unverified. Include framing/outpainting, QA and retries in full workflow totals. Subscription access is a prerequisite, even when incremental image cost is zero.
- Treat the observed image limit and timing as observations from these runs, not guaranteed product limits or service times.

## Repository finishing work

- Make README the authoritative current workflow; mark PIPELINE.md's old proposal as historical or update its stale model, prompt and autonomy descriptions.
- Clarify the scope of the ten-minute timing estimate: generation versus completed, reviewed, framed delivery.
- Add a small dependency manifest and a no-spend preflight for runtime, Pillow, references/templates and route availability.
- Explain that excluded raw/attempt/outpaint files mean historical framing cannot be reproduced directly from the clone. Viewing final results and generating a fresh set are different supported actions.
- Preserve representative failures and before/after images in the repository/Miro, and provide a private archive of all intermediate images if promising the brief's full iteration history. JSON logs alone do not show visual failures.
- Link directly to the final gallery, downloadable final folders, benchmark comparisons and test reports; avoid making reviewers search 2,000+ files.
- Keep the existing private-reference notice and verify reviewer access when sharing.

## Art at this stage

Final output is already strong enough to present. Suburbia and Love in the City are especially consistent. Fantasy conveys the genre clearly. Lost Island remains coherent, but Shovel and X Marks the Spot repeat a focal subject; consider a narrowly scoped change only if budget/time permit and Pavel wants it.

The existing final metrics flag LC 5, PP 4, OG 2 and LI 2 cards. Flags are inspection prompts, not automatic failures. Record a short accepted-exception rationale for full-width scenes and intentional empty space. Do not chase every metric into a redraw that harms the composition.

## Suggested Miro sequence

1. Task, required outputs and links to the final results/tool.
2. Reference analysis: four composition categories, coherent sets, concrete evidence images.
3. Model experiments: same task, blind comparisons, ratings, limitations, chosen routes.
4. Workflow diagram: input -> plan -> validation -> generation -> QA/retry -> framing -> set review -> export -> designer selection.
5. Three concise learning stories: sky-background bias, crop/framing failure, automated judge versus human taste.
6. Final selected genre sets, with a few direct reference comparisons at normal card size.
7. Autonomy demonstration: fresh prompt, complete alternatives, test result, interventions, time and cost.
8. Limitations, remaining accepted issues, repository and evidence archive links.

## Recommended order of remaining work

1. Correct the two confirmed validation/status issues.
2. Close reviewer test 1; prepare and run the planned test from the actual repository checkout.
3. Reconcile README/skill/architecture wording and make renderer choice explicit.
4. Freeze final artwork and record accepted exceptions; select three headline sets and label the fourth as additional if desired.
5. Build the Miro narrative and verify every output/link/access path.

All recommendations in this report are proposals; no implementation changes were made as part of this review.
