# BENCH-02 prompt template v2

Same structure and placeholders as v1 (BENCH-01/prompt_v1.md), and the same subject text, so the hidden cards stay hidden.

Every change from v1 traces back to BENCH-01 feedback. Sources:

- **P**: Pavel's blind notes
- **A**: assistant review
- **X**: external-model ratings relayed by Pavel
- **R**: visible in the Miro originals, rows 1–6

| Rule added in v2 | Source |
|---|---|
| No outlines, not painterly, not photographic, not flat cel shading; crisp, defined materials | X (U5, Y3, L3, C6, K2) |
| Satin sheen, not wet or chrome gloss | P ("too glossy", U5) |
| Background hue complementary to the object's main colour | P + A (both bottles blue on blue) + R |
| Medium detail: 2–4 defining features, no micro-texture | P ("too many unnecessary details" K7, "too little details on cup" Y3) |
| Soft, translucent, simple effects (steam) | P (V5) |
| Most typical silhouette of the object | P ("bottle not like a bottle", U5) |
| Background pattern centred behind the object (rays or rings) | P ("round like to fit shape of the object", K2) + R |
| C1: slight tilt or three-quarter view | R (bottle, popsicle, fan, cap) |
| C2: plain one-colour surface, same colour family as the wall | P ("reads as category 3", V5) + R (mojito, beach bag, tea cup, sneakers) |
| C3: polished surface with soft reflection, background free of props | P ("mirroring object image" K2, "background has too many details" R2) |
| C4: low camera angle, large and possibly cropped object, only a hint of ground, clean sky | P (C6, L3: "low angle ... terrain in ref is not shown for a reason", "too small in frame", sky) + R |

## INTRO
You will create one illustration for a collectible card in a casual mobile game. The next {n_refs} images are existing cards from this game. Use them only to learn the art style. Some may be small or low-resolution: match their style, not their blur or pixelation.

## REFERENCE_LABEL
Reference {ref_id} ({category_short}):

## TASK
Task: draw a NEW card illustration of {subject}. It must look as if the same artist made it for the same card album, so that a player would not notice any difference next to the reference cards.

Rendering, matched exactly to the references:
- A clean, polished 3D game-asset finish: smooth, chunky, simplified volumes with soft rounded edges and slightly exaggerated proportions, with crisp, clearly defined materials.
- Bright, clear lighting from the upper front that models the volumes, with soft-edged highlight shapes and a satin sheen. Never wet-look, chrome or mirror-like gloss on the object, and never dim, moody or photographic lighting.
- No outlines or dark contour lines, no painterly brush strokes, no flat cel shading, no photographic depth of field, no realistic micro-textures.

Object:
- Draw the most typical, instantly recognizable version of the object, with a clear, simple silhouette.
- Medium detail: keep the 2-4 defining features that make it recognizable (for example a simple decorative motif, a cap or a handle), but no micro-detail such as droplets, mesh, scratches, stitching, grain, decals or tiny parts.
- Effects such as steam, sparkle or splashes, if any, are soft, translucent and simple, as in the references.

Colour:
- Bright, highly saturated colours, never pastel or washed out.
- The background colour must contrast strongly with the object's main colour, ideally its complementary hue (for example a blue object on a yellow or orange background, a red object on a green or blue background), so the object stands out clearly at thumbnail size.

Framing:
- One main object, centred and large, filling about 70-85% of the frame height, readable at thumbnail size (about 64 pixels tall).

Composition, category {category}: {category_rules}

Output requirements:
- A single square, full-bleed illustration.
- No card frame, border, stars, ribbon, label, text, letters, numbers, logos or watermark.
- No characters, people or animals, and no extra objects beyond the subject and what its category allows.
- Do not reproduce any reference object; draw only the requested subject.

## CATEGORY_1
The object has no small details and floats in the air, with no table, floor or ground under it, shown with a slight tilt or in three-quarter view. The background is a single saturated colour with a gradient, either plain or with one simple, subtle pattern centred behind the object: radiating light rays, concentric rings, stripes or small repeated motifs.

## CATEGORY_2
The object has no small details and stands on a plain, flat surface of a single colour (not wood grain or a detailed table), seen from slightly above. Behind it is a plain vertical wall: a single colour with a gradient, or one simple pattern such as rays, concentric rings or stripes. The surface and the wall share one colour family that contrasts with the object.

## CATEGORY_3
The object stands on, or is set into, a simple realistic surface suited to it, such as a polished wooden tabletop, a glossy floor or a podium, with a soft mirrored reflection or contact shadow under the object. Behind it is a simple vertical wall: plain, a single-colour gradient, or one simple pattern such as rays, concentric rings or stripes, centred behind the object. Keep the background free of props and scenery. The surface is painted in the same stylized way as the object.

## CATEGORY_4
The object is set into a realistic environment suited to it, seen from a low camera angle so it looks big and heroic. It is large in the frame and may be slightly cropped by the frame edges. Show only a hint of ground or water at the bottom; the rest of the background is a clean, saturated blue sky with a few soft, puffy, stylized clouds, or an equally simple setting. No busy terrain, rocks, crashing waves or scattered scenery: the object stays the clear, central focus. The environment is painted in the same stylized way as the object.
