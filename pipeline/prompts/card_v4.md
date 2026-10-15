# Card generation prompt v4

Template used by `cardgen.py`. It is prompt v3 (`experiments/BENCH-03/prompt_v3.md`) plus:

- a **card brief** from the plan: subject, detail, colours, background, cue;
- Pavel's BENCH-03 rules: margins, complete objects, one charming detail, two-colour vehicles, visible background pattern, separate floor and wall tones, bright overall.

Every rule's source is listed in `pipeline/rulebook.md`.

Placeholders: {n_refs}, {ref_id}, {category_short}, {name}, {subject}, {unique_detail}, {main_colors}, {background}, {context_cue}, {category}, {category_rules}, {fix}.

## INTRO
You will create one illustration for a collectible card in a casual mobile game. The next {n_refs} images are existing cards from this game. Use them only to learn the art style; never copy their objects.

## REFERENCE_LABEL
Reference {ref_id} ({category_short}):

## TASK
Task: draw a NEW card illustration that looks as if the same artist made it for the same card album, so that a player would not notice any difference next to the reference cards.

Card brief:
- Card: {name}.
- Object: {subject}.
- Its one charming, distinctive detail: {unique_detail}.
- Main colours of the object: {main_colors}.
- Background: {background}.
- Context cue: {context_cue}.

Rendering, matched exactly to the references:
- A clean, polished 3D game-asset finish: smooth, chunky, simplified volumes with soft rounded edges and slightly exaggerated proportions, with crisp, clearly defined materials.
- Bright, even, cheerful lighting from the upper front, with soft-edged highlight shapes and a satin sheen. Never wet-look, chrome or mirror-like gloss, and never dim, moody, theatrical or photographic lighting. The whole image is bright.
- No outlines or dark contour lines, no painterly brush strokes, no flat cel shading, no photographic depth of field, no realistic micro-textures.

Object:
- The most typical, instantly recognizable version of the object, complete with its standard parts, with a clear, simple silhouette, seen from its most familiar angle.
- Manufactured objects have smooth, clean surfaces and simple flowing lines: no grooves, ridges, panel lines, droplets, grip textures or busy decoration. Instead of generic stripes or bands, give the object the one charming detail from the brief.
- Built structures keep their crafted structural details (bricks or planks, railings, windows), drawn in the same smooth, simplified way.
- Vehicles use two main colours. Liquids are clearly visible and richly coloured. Steam, if any, is two or three thin, wispy, semi-transparent white strands.

Colour:
- A warm, juicy, inviting palette with bright, highly saturated colours. Never pastel, muddy or washed out.
- The background contrasts clearly with the object, ideally in its complementary colour, so the object never blends into it. No teal, grey, dark or muted backgrounds.

Background and context:
- Follow the background from the brief. Any pattern (rays, rings, motifs) is clearly visible and centred behind the object, and never bleak or empty-looking.
- Floor or surface and wall are in clearly different tones. At most the one context cue from the brief; never a full scene, props or scenery.

Framing:
- One main object, centred, with clear empty margins on every side, filling about 60-75% of the frame height. Nothing is cut off by the frame edges (a category 4 object may touch the bottom edge).

Composition, category {category}: {category_rules}

Output requirements:
- A single full-bleed illustration.
- No card frame, border, stars, ribbon, label, text, letters, numbers, logos or watermark.
- No people or characters, and no extra objects beyond the subject and what its category allows.
{fix}

## CATEGORY_1
The object has no small details and floats in the air, with no table, floor or ground under it, shown with a slight tilt or in three-quarter view. The background is a single saturated colour with a smooth gradient and one clearly visible pattern centred behind the object: radiating light rays, concentric rings or small repeated theme motifs.

## CATEGORY_2
The object has no small details and stands on a plain, flat surface of a single colour (not wood grain or a detailed table), seen from slightly above. Behind it is a plain vertical wall with a smooth single-colour gradient and no stripes. The surface and the wall share one warm or bright colour family that contrasts with the object, with the surface clearly lighter or darker than the wall.

## CATEGORY_3
The object stands on, or is set into, a simple realistic surface suited to it, such as a polished wooden tabletop, a glossy floor or a podium. The surface is painted in a smooth, stylized way, not photographically textured, with a soft reflection or contact shadow under the object. Behind it is a vertical wall in one colour, clearly different in tone from the surface: a smooth gradient, optionally with subtle rays or rings centred behind the object. Keep the background free of props, lights and scenery.

## CATEGORY_4
The object is set into a realistic environment suited to it, seen from a low camera angle so it looks big and heroic, but still with some sky above it. Show only the key element of the setting as a clear strip at the bottom (for example a strip of street, grass or water). The rest of the background is a smooth, bright, saturated blue sky gradient with a few soft, realistic, volumetric cumulus clouds near the horizon. No busy terrain, crowds, rocks or scattered scenery: the object stays the clear, central focus. The environment is painted in the same stylized way as the object.
