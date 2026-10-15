# BENCH-01 prompt template v1

bench.py fills the sections below. The placeholders are {n_refs}, {ref_id}, {category_short}, {subject}, {category} and {category_rules}.
Every model gets the same text; only the model changes between arms. The subject is just the object's name, as a producer would write it, so the hidden card's design isn't leaked.
The category sections translate the brief (pp. 3-4). Each "painted in the same stylized way" sentence is our clarification: "realistic" in the brief means a real-world setting, not photorealism.

## INTRO
You will create one illustration for a collectible card in a casual mobile game. The next {n_refs} images are existing cards from this game. Use them only to learn the art style. Some may be small or low-resolution: match their style, not their blur or pixelation.

## REFERENCE_LABEL
Reference {ref_id} ({category_short}):

## TASK
Task: draw a NEW card illustration of {subject}. It must look as if the same artist made it for the same card album, so that a player would not notice any difference next to the reference cards.

Art style, matched to the references:
- Stylized, chunky, simplified forms with soft rounded edges and slightly exaggerated proportions; not photorealistic.
- Bright, saturated colours; smooth, soft shading with gentle glossy highlights; minimal surface texture and no fine ornament.
- A clean, instantly readable silhouette with strong contrast against the background, so the object is recognizable at thumbnail size (about 64 pixels tall).
- One main object, centred, filling most of the frame while keeping clear margins on all sides.

Composition, category {category}: {category_rules}

Output requirements:
- A single square, full-bleed illustration.
- No card frame, border, stars, ribbon, label, text, letters, numbers, logos or watermark.
- No characters, people or animals, and no extra objects beyond the subject and what its category allows.
- Do not reproduce any reference object; draw only the requested subject.

## CATEGORY_1
The object has no small details and floats in the air, with no table, floor or ground under it. The background is a single colour with a gradient, or a simple pattern such as stripes, small repeated motifs, a flat colour or radiating light rays.

## CATEGORY_2
The object has no small details and stands on a surface. The background is simple: behind the object is a vertical surface that is plain, a single colour with a gradient, or a simple pattern such as stripes, small repeated motifs, a flat colour or light rays.

## CATEGORY_3
The object stands on a realistic surface. The background has volume: the object stands on, or is set into, a simple realistic surface, and behind it is a vertical surface that is plain, a single colour with a gradient, or a simple pattern such as stripes, small repeated motifs, a flat colour or light rays. The surface is painted in the same stylized way as the object.

## CATEGORY_4
The object is set into a realistic surrounding environment suited to it, but remains the clear, central focus of the picture. The environment is painted in the same stylized way as the object.
