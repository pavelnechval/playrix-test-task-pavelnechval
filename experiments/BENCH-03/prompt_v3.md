# BENCH-03 prompt template v3

Builds on v2 (BENCH-02/prompt_v2.md). Placeholders and subject text are unchanged.

Sources for the v3 changes:

- **P2**: Pavel's notes on the BENCH-02 images (`BENCH-02/scores_pavel.csv`)
- **X2**: the external model's notes on the same images (`BENCH-02/scores_external_model.csv`)
- **R**: the Miro originals

| Rule added or changed in v3 | Source |
|---|---|
| Manufactured objects: smooth surfaces and flowing lines, no grooves, ridges, panel lines or grip textures | P2 (T1a, T1b), X2 (T1a) |
| Built structures keep crafted structural details (bricks, railings, windows) | X2 (T4a, T4b), R (lighthouse) |
| Familiar viewing angle for the object | P2 (T3a "preserve original angle") |
| Liquids and contents clearly visible and richly coloured | P2 (T2a "tea barely visible") |
| Steam: 2-3 thin, wispy, semi-transparent strands | P2 (T2a, T2b), X2 (T2b) |
| Warm, juicy, inviting palette; warm reds; no teal, grey or muted backgrounds | P2 (T2b, T4a, T4b), R |
| Bright, even, cheerful lighting, not theatrical | X2 (T3b) |
| Smooth single-colour gradient preferred over stripes for walls | P2 (T2a, T3b), X2 (T2b) |
| One simple context cue (a stripe on the rink floor, a strip of sea) | P2 (T3a, T3b, T4b) |
| C3 floor stylized, not photographically textured | X2 (T3a) |
| C4: soft, realistic volumetric clouds near the horizon; smooth bright sky | P2 (T4a, T4b), R |

## INTRO
You will create one illustration for a collectible card in a casual mobile game. The next {n_refs} images are existing cards from this game. Use them only to learn the art style. Some may be small or low-resolution: match their style, not their blur or pixelation.

## REFERENCE_LABEL
Reference {ref_id} ({category_short}):

## TASK
Task: draw a NEW card illustration of {subject}. It must look as if the same artist made it for the same card album, so that a player would not notice any difference next to the reference cards.

Rendering, matched exactly to the references:
- A clean, polished 3D game-asset finish: smooth, chunky, simplified volumes with soft rounded edges and slightly exaggerated proportions, with crisp, clearly defined materials.
- Bright, even, cheerful lighting from the upper front that models the volumes, with soft-edged highlight shapes and a satin sheen. Never wet-look, chrome or mirror-like gloss on the object, and never dim, moody, theatrical or photographic lighting.
- No outlines or dark contour lines, no painterly brush strokes, no flat cel shading, no photographic depth of field, no realistic micro-textures.

Object:
- Draw the most typical, instantly recognizable version of the object, with a clear, simple silhouette, seen from its most familiar angle: a three-quarter front view from slightly above for objects that float or stand on a surface, a low angle for big structures.
- Manufactured objects (bottles, cups, vehicles, tools) have smooth, clean surfaces and simple flowing lines: no grooves, ridges, panel lines, grip textures or busy decoration. At most one simple decorative element, such as a single band or a small motif.
- Built structures (towers, houses, stalls) keep their crafted structural details, such as bricks or planks, railings, windows and a lamp room, drawn in the same smooth, simplified way.
- Liquids and contents are clearly visible and richly coloured, for example dark amber tea.
- Steam, if any, is two or three thin, wispy, semi-transparent white strands rising in gentle S-curves and fading out at the top. Never thick, opaque or cartoon swirls.

Colour:
- A warm, juicy, inviting palette with bright, highly saturated colours: warm reds (orange-red, never cool crimson), sunny yellows and oranges, rich greens, warm purples and bright, clean sky blues. Never pastel, muddy or washed out.
- The background colour contrasts strongly with the object's main colour, ideally its complementary hue, but stays warm or bright: no teal, grey, dark or muted backgrounds.

Background and context:
- Prefer a smooth single-colour gradient. Add a pattern (radiating rays or concentric rings centred behind the object) only if it stays subtle.
- Add at most one simple context cue that shows where the object belongs, such as a single painted stripe on a rink floor or a visible strip of sea at the horizon. Never a full scene.

Framing:
- One main object, centred and large, filling about 70-85% of the frame height, readable at thumbnail size (about 64 pixels tall).

Composition, category {category}: {category_rules}

Output requirements:
- A single full-bleed illustration.
- No card frame, border, stars, ribbon, label, text, letters, numbers, logos or watermark.
- No characters, people or animals, and no extra objects beyond the subject and what its category allows.
- Do not reproduce any reference object; draw only the requested subject.

## CATEGORY_1
The object has no small details and floats in the air, with no table, floor or ground under it, shown with a slight tilt or in three-quarter view. The background is a single saturated colour with a smooth gradient, optionally with one subtle pattern centred behind the object: radiating light rays, concentric rings or small repeated motifs.

## CATEGORY_2
The object has no small details and stands on a plain, flat surface of a single colour (not wood grain or a detailed table), seen from slightly above. Behind it is a plain vertical wall with a smooth single-colour gradient and no stripes. The surface and the wall share one warm or bright colour family that contrasts with the object.

## CATEGORY_3
The object stands on, or is set into, a simple realistic surface suited to it, such as a polished wooden tabletop, a glossy rink floor or a podium. The surface is painted in a smooth, stylized way, not photographically textured, with a soft mirrored reflection or contact shadow under the object and at most one simple marking that tells where the object is. Behind it is a vertical wall in one colour: a smooth gradient, optionally with very subtle rays or rings centred behind the object. Keep the background free of props, lights and scenery.

## CATEGORY_4
The object is set into a realistic environment suited to it, seen from a low camera angle so it looks big and heroic. It is large in the frame and may be slightly cropped by the frame edges. Show only the key element of the setting as a clear strip at the bottom (for example a visible strip of sea or a patch of grass). The rest of the background is a smooth, bright, saturated blue sky gradient with a few soft, realistic, volumetric cumulus clouds near the horizon, not cartoon puffs. No busy terrain, rocks, crashing waves or scattered scenery: the object stays the clear, central focus. The environment is painted in the same stylized way as the object.
